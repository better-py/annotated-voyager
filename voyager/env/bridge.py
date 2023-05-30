import os.path
import time
import warnings
from typing import SupportsFloat, Any, Tuple, Dict

import requests
import json

import gymnasium as gym
from gymnasium.core import ObsType

import voyager.utils as U

from .minecraft_launcher import MinecraftInstance
from .process_monitor import SubprocessMonitor


class VoyagerEnv(gym.Env):
    """
    TODO X: 辅助模块， 用于与 Minecraft 服务器进行交互
        - 注意基类 gym.Env
        - https://github.com/Farama-Foundation/Gymnasium
            - openAI Gym 的 fork 分支，官方不维护了。
            - 功能是： 强化学习算法相关
        - 核心方法是 step()方法

    """

    def __init__(
            self,
            mc_port=None,
            azure_login=None,
            server_host="http://127.0.0.1",
            server_port=3000,  # todo x: mineflayer 服务器端口
            request_timeout=600,
            log_path="./logs",
    ):
        if not mc_port and not azure_login:
            raise ValueError("Either mc_port or azure_login must be specified")
        if mc_port and azure_login:
            warnings.warn(
                "Both mc_port and mc_login are specified, mc_port will be ignored"
            )
        self.mc_port = mc_port
        self.azure_login = azure_login

        # =======================================================================

        #
        # todo x:
        #
        self.server = f"{server_host}:{server_port}"
        self.server_port = server_port
        self.request_timeout = request_timeout
        self.log_path = log_path

        # =======================================================================

        #
        # todo x: 调用 Nodejs， 运行 mineflayer/index.js， 完整路径： voyager/env/mineflayer/index.js
        #
        self.mineflayer = self.get_mineflayer_process(server_port)  # todo x: mineflayer 服务器端口， 默认 3000

        # =======================================================================

        if azure_login:
            self.mc_instance = self.get_mc_instance()
        else:
            self.mc_instance = None
        self.has_reset = False
        self.reset_options = None
        self.connected = False
        self.server_paused = False

    #
    # todo x: 调用 Nodejs， 运行 mineflayer/index.js
    #
    def get_mineflayer_process(self, server_port):
        U.f_mkdir(self.log_path, "mineflayer")

        # todo x: 获取当前文件的绝对路径
        file_path = os.path.abspath(os.path.dirname(__file__))

        return SubprocessMonitor(
            #
            # todo x: 调用 Nodejs， 运行 mineflayer/index.js
            #   - 完整路径： voyager/env/mineflayer/index.js
            #
            commands=[
                "node",
                U.f_join(file_path, "mineflayer/index.js"),
                str(server_port),
            ],
            name="mineflayer",
            ready_match=r"Server started on port (\d+)",
            log_path=U.f_join(self.log_path, "mineflayer"),
        )

    def get_mc_instance(self):
        print("Creating Minecraft server")
        U.f_mkdir(self.log_path, "minecraft")
        return MinecraftInstance(
            **self.azure_login,
            mineflayer=self.mineflayer, # todo x: 注意参数
            log_path=U.f_join(self.log_path, "minecraft"),
        )

    def check_process(self):
        if self.mc_instance and not self.mc_instance.is_running:
            # if self.mc_instance:
            #     self.mc_instance.check_process()
            #     if not self.mc_instance.is_running:
            print("Starting Minecraft server")

            #
            # todo x:
            #
            self.mc_instance.run()

            self.mc_port = self.mc_instance.port
            self.reset_options["port"] = self.mc_instance.port
            print(f"Server started on port {self.reset_options['port']}")

        # =======================================================================

        #
        # todo x: 检查 mineflayer 进程是否存在
        #
        retry = 0
        while not self.mineflayer.is_running:
            print("Mineflayer process has exited, restarting")

            #
            #
            #
            self.mineflayer.run()
            if not self.mineflayer.is_running:
                if retry > 3:
                    raise RuntimeError("Mineflayer process failed to start")
                else:
                    continue
            print(self.mineflayer.ready_line)

            # =======================================================================

            #
            # todo x: 发送请求到本地启动的 mineflayer 服务
            #   - 启动路径：voyager/env/mineflayer/index.js
            #
            res = requests.post(
                f"{self.server}/start",
                json=self.reset_options,
                timeout=self.request_timeout,
            )  # todo x: 执行开发操作
            if res.status_code != 200:
                self.mineflayer.stop()
                raise RuntimeError(
                    f"Minecraft server reply with code {res.status_code}"
                )
            return res.json()

    ########################################################################################

    #
    # todo x: HTTP POST 请求本地 mineflayer 服务， 远程执行 js 代码
    #
    def step(
            self,
            code: str,
            programs: str = "",
    ) -> Tuple[ObsType, SupportsFloat, bool, bool, Dict[str, Any]]:
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")

        self.check_process()  # todo x: 检查进程状态
        self.unpause()  # todo x: fixme, 内部实现参数，似乎传错了？ 潜在 bug

        # =======================================================================

        #
        # todo x: http post 执行 js 代码， call 本地的 mineflayer 服务
        #
        data = {
            "code": code,  # todo x: js 代码
            "programs": programs,
        }

        # =======================================================================

        #
        # todo x: http call 本地的 mineflayer 服务， 执行 step 操作
        #   - 查看 API 实现: `voyager/env/mineflayer/index.js` 中的 `/step` 定义
        #
        res = requests.post(
            f"{self.server}/step", json=data, timeout=self.request_timeout
        )
        if res.status_code != 200:
            raise RuntimeError("Failed to step Minecraft server")
        returned_data = res.json()

        # todo x: 执行暂停操作
        self.pause()
        return json.loads(returned_data)

    ########################################################################################

    def render(self):
        raise NotImplementedError("render is not implemented")

    def reset(
            self,
            *,
            seed=None,
            options=None,
    ) -> Tuple[ObsType, Dict[str, Any]]:
        if options is None:
            options = {}

        if options.get("inventory", {}) and options.get("mode", "hard") != "hard":
            raise RuntimeError("inventory can only be set when options is hard")

        self.reset_options = {
            "port": self.mc_port,
            "reset": options.get("mode", "hard"),
            "inventory": options.get("inventory", {}),
            "equipment": options.get("equipment", []),
            "spread": options.get("spread", False),
            "waitTicks": options.get("wait_ticks", 5),
            "position": options.get("position", None),
        }

        self.unpause()
        self.mineflayer.stop()
        time.sleep(1)  # wait for mineflayer to exit

        #
        # todo x:
        #
        returned_data = self.check_process()
        self.has_reset = True
        self.connected = True
        # All the reset in step will be soft
        self.reset_options["reset"] = "soft"
        self.pause()
        return json.loads(returned_data)

    def close(self):
        self.unpause()
        if self.connected:
            res = requests.post(f"{self.server}/stop")  # todo x: call 本地的 mineflayer 服务, 执行关闭操作
            if res.status_code == 200:
                self.connected = False
        if self.mc_instance:
            self.mc_instance.stop()
        self.mineflayer.stop()
        return not self.connected

    def pause(self):
        if self.mineflayer.is_running and not self.server_paused:
            res = requests.post(f"{self.server}/pause")  # todo x: call 本地的 mineflayer 服务, 执行暂停操作
            if res.status_code == 200:
                self.server_paused = True
        return self.server_paused

    def unpause(self):
        if self.mineflayer.is_running and self.server_paused:
            res = requests.post(f"{self.server}/pause")  # todo x: call 本地的 mineflayer 服务， 这里似乎有 bug!!!， 参数传错了: unpause
            if res.status_code == 200:
                self.server_paused = False
            else:
                print(res.json())
        return self.server_paused
