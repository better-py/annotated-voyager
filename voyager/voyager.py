import copy
import json
import os
import time
from typing import Dict

import voyager.utils as U
from .env import VoyagerEnv

from .agents import ActionAgent
from .agents import CriticAgent  # todo x: 评价 agent, 基于 langchain + chatgpt, 判断 task 是否处理成功
from .agents import CurriculumAgent  # todo x: 基于 langchain + chatgpt，主要用于生成新task（基于 AI 回答）
from .agents import SkillManager


# TODO: remove event memory
class Voyager:
    def __init__(
            self,
            mc_port: int = None,
            azure_login: Dict[str, str] = None,
            server_port: int = 3000,
            openai_api_key: str = None,
            env_wait_ticks: int = 20,
            env_request_timeout: int = 600,
            max_iterations: int = 160,
            reset_placed_if_failed: bool = False,

            #
            #
            #
            action_agent_model_name: str = "gpt-4",
            action_agent_temperature: int = 0,
            action_agent_task_max_retries: int = 4,
            action_agent_show_chat_log: bool = True,
            action_agent_show_execution_error: bool = True,

            #
            #
            #
            curriculum_agent_model_name: str = "gpt-4",
            curriculum_agent_temperature: int = 0,
            curriculum_agent_qa_model_name: str = "gpt-3.5-turbo",
            curriculum_agent_qa_temperature: int = 0,
            curriculum_agent_warm_up: Dict[str, int] = None,
            curriculum_agent_core_inventory_items: str = r".*_log|.*_planks|stick|crafting_table|furnace"
                                                         r"|cobblestone|dirt|coal|.*_pickaxe|.*_sword|.*_axe",
            curriculum_agent_mode: str = "auto",

            #
            #
            #
            critic_agent_model_name: str = "gpt-4",
            critic_agent_temperature: int = 0,
            critic_agent_mode: str = "auto",

            #
            #
            #
            skill_manager_model_name: str = "gpt-3.5-turbo",
            skill_manager_temperature: int = 0,
            skill_manager_retrieval_top_k: int = 5,
            openai_api_request_timeout: int = 240,
            ckpt_dir: str = "ckpt",
            resume: bool = False,
    ):
        """
        The main class for Voyager.
        Action agent is the iterative prompting mechanism in paper.
        Curriculum agent is the automatic curriculum in paper.
        Critic agent is the self-verification in paper.
        Skill manager is the skill library in paper.
        :param mc_port: minecraft in-game port
        :param azure_login: minecraft login config
        :param server_port: mineflayer port
        :param openai_api_key: openai api key
        :param env_wait_ticks: how many ticks at the end each step will wait, if you found some chat log missing,
        you should increase this value
        :param env_request_timeout: how many seconds to wait for each step, if the code execution exceeds this time,
        python side will terminate the connection and need to be resumed
        :param reset_placed_if_failed: whether to reset placed blocks if failed, useful for building task
        :param action_agent_model_name: action agent model name
        :param action_agent_temperature: action agent temperature
        :param action_agent_task_max_retries: how many times to retry if failed
        :param curriculum_agent_model_name: curriculum agent model name
        :param curriculum_agent_temperature: curriculum agent temperature
        :param curriculum_agent_qa_model_name: curriculum agent qa model name
        :param curriculum_agent_qa_temperature: curriculum agent qa temperature
        :param curriculum_agent_warm_up: info will show in curriculum human message
        if completed task larger than the value in dict, available keys are:
        {
            "context": int,
            "biome": int,
            "time": int,
            "other_blocks": int,
            "nearby_entities": int,
            "health": int,
            "hunger": int,
            "position": int,
            "equipment": int,
            "chests": int,
            "optional_inventory_items": int,
        }
        :param curriculum_agent_core_inventory_items: only show these items in inventory before optional_inventory_items
        reached in warm up
        :param curriculum_agent_mode: "auto" for automatic curriculum, "manual" for human curriculum
        :param critic_agent_model_name: critic agent model name
        :param critic_agent_temperature: critic agent temperature
        :param critic_agent_mode: "auto" for automatic critic ,"manual" for human critic
        :param skill_manager_model_name: skill manager model name
        :param skill_manager_temperature: skill manager temperature
        :param skill_manager_retrieval_top_k: how many skills to retrieve for each task
        :param openai_api_request_timeout: how many seconds to wait for openai api
        :param ckpt_dir: checkpoint dir
        :param resume: whether to resume from checkpoint
        """

        #
        # todo x:
        #
        # init env
        self.env = VoyagerEnv(
            mc_port=mc_port,
            azure_login=azure_login,
            server_port=server_port,
            request_timeout=env_request_timeout,
        )

        # =======================================================================

        self.env_wait_ticks = env_wait_ticks
        self.reset_placed_if_failed = reset_placed_if_failed
        self.max_iterations = max_iterations

        # set openai api key
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # =======================================================================

        #
        # todo x: 基于 langchain + ChatGPT 创建的 LLM 模型 agent
        #
        # init agents
        self.action_agent = ActionAgent(
            model_name=action_agent_model_name,
            temperature=action_agent_temperature,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            chat_log=action_agent_show_chat_log,
            execution_error=action_agent_show_execution_error,
        )
        self.action_agent_task_max_retries = action_agent_task_max_retries

        # =======================================================================

        #
        # todo x: 基于 langchain + ChatGPT 创建的 LLM 模型 agent
        #
        self.curriculum_agent = CurriculumAgent(
            model_name=curriculum_agent_model_name,
            temperature=curriculum_agent_temperature,
            qa_model_name=curriculum_agent_qa_model_name,
            qa_temperature=curriculum_agent_qa_temperature,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            mode=curriculum_agent_mode,
            warm_up=curriculum_agent_warm_up,
            core_inventory_items=curriculum_agent_core_inventory_items,
        )

        # =======================================================================

        #
        # todo x:  基于 langchain + ChatGPT 创建的 LLM 模型 agent
        #
        self.critic_agent = CriticAgent(
            model_name=critic_agent_model_name,
            temperature=critic_agent_temperature,
            request_timout=openai_api_request_timeout,
            mode=critic_agent_mode,
        )

        # =======================================================================

        #
        # todo x: 基于 langchain + ChatGPT 创建的 LLM 模型 agent
        #
        self.skill_manager = SkillManager(
            model_name=skill_manager_model_name,
            temperature=skill_manager_temperature,
            retrieval_top_k=skill_manager_retrieval_top_k,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
        )
        self.recorder = U.EventRecorder(ckpt_dir=ckpt_dir, resume=resume)
        self.resume = resume

        # init variables for rollout
        self.action_agent_rollout_num_iter = -1
        self.task = None

        # =======================================================================

        #
        # todo x: ⛔️⛔️⛔️ 注意! 跟踪此值调用链路!
        #
        self.context = ""  # todo x: ⛔️糟糕的使用方式！上下文，在 .reset() 中更新

        # =======================================================================

        #
        # todo x: ⛔️⛔️⛔️ 注意! 跟踪此值调用链路!
        #
        self.messages = None  # todo x: ⛔️糟糕的使用方式！共享变量: 隐式赋值(self.reset()方法) + 隐式调用(self.step()方法）.
        self.conversations = []
        self.last_events = None

    def reset(self, task, context="", reset_env=True):
        """todo x: 跟踪 task 和 context 流转链路
            - 此方法， 写法比较脏！
            - 核心用途：隐式更新了 self.context 和 self.messages.
            - 这2个值， 在其他方法中，被隐式+直接使用！

        """
        self.action_agent_rollout_num_iter = 0
        self.task = task

        # =======================================================================

        #
        # todo x: ⛔️⛔️⛔️注意！！！糟糕用法，共享变量， 注意 self.context 的使用链！
        #
        self.context = context  # todo x: 注意上下文的更新+使用链
        if reset_env:
            #
            #
            #
            self.env.reset(
                options={
                    "mode": "soft",
                    "wait_ticks": self.env_wait_ticks,
                }
            )
        difficulty = (
            "easy" if len(self.curriculum_agent.completed_tasks) > 15 else "peaceful"
        )

        # =======================================================================

        #
        # todo x: 🔥️🔥️🔥️ HTTP 请求本地启动的 mineflayer 服务
        #
        # step to peek an observation
        events = self.env.step(
            "bot.chat(`/time set ${getNextTime()}`);\n"
            + f"bot.chat('/difficulty {difficulty}');"
        )

        # =======================================================================

        #
        # todo x: 传入 context, 检索向量数据库, 尝试复用已存在技能
        #
        skills = self.skill_manager.retrieve_skills(query=self.context)
        print(
            f"\033[33mRender Action Agent system message with {len(skills)} control_primitives\033[0m"
        )

        # =======================================================================

        #
        # todo x: 根据 skills, 让 GPT 写代码, 执行控制动作
        #
        system_message = self.action_agent.render_system_message(skills=skills)  # todo x: 让GPT自己写代码，实现控制功能
        human_message = self.action_agent.render_human_message(
            events=events, code="", task=self.task, context=context, critique=""
        )

        # =======================================================================

        #
        # todo x: ⛔️⛔️⛔️注意！比较糟糕的用法, 使用 self.messages 作内部数据共享。（跟踪此变量的调用处， 隐式操作）
        #   - 注意， 此时 GPT 生成的代码，还未被执行。 具体在 self.step() 中执行的。（非常隐晦）
        #
        self.messages = [system_message, human_message]  # todo x: 糟糕的初始化方式！隐式被 self.step() 使用
        print(
            f"\033[32m****Action Agent human message****\n{human_message.content}\033[0m"
        )
        assert len(self.messages) == 2
        self.conversations = []
        return self.messages

    def close(self):
        self.env.close()

    ########################################################################################

    #
    # todo x:
    #
    def step(self):
        """todo x: 🔥️🔥️🔥️🔥🔥️ 核心方法！

        """
        if self.action_agent_rollout_num_iter < 0:
            raise ValueError("Agent must be reset before stepping")

        # =======================================================================

        #
        # todo x: 🔥️🔥️🔥️🔥🔥️ call OpenAI(GPT)
        #   - 此处使用的 self.messages, 是在 self.reset() 中初始化的
        #   - 这里的 messages，内容是 由 GPT 自己生成的代码（待被执行）
        #
        ai_message = self.action_agent.llm(self.messages)  # todo x: 此处 self.messages, 是隐式由
        print(f"\033[34m****Action Agent ai message****\n{ai_message.content}\033[0m")
        self.conversations.append(
            (self.messages[0].content, self.messages[1].content, ai_message.content)
        )

        # =======================================================================

        #
        # todo x: 🔥️🔥️🔥️🔥️ 导入 JS 模块，调用 JS lib
        #
        parsed_result = self.action_agent.process_ai_message(message=ai_message)

        success = False
        if isinstance(parsed_result, dict):
            code = parsed_result["program_code"] + "\n" + parsed_result["exec_code"]

            # =======================================================================

            #
            # todo x: HTTP 请求本地启动的 mineflayer 服务, 远程执行 js 代码
            #
            events = self.env.step(
                code,
                programs=self.skill_manager.programs,  # todo x： js 代码
            )

            # =======================================================================

            self.recorder.record(events, self.task)
            self.action_agent.update_chest_memory(events[-1][1]["nearbyChests"])

            #
            # todo x: call OpenAI(GPT), 根据 AI(GPT) 回答，自动判断 task 是否完成
            #
            success, critique = self.critic_agent.check_task_success(
                events=events,
                task=self.task,
                context=self.context,
                chest_observation=self.action_agent.render_chest_observation(),
                max_retries=5,
            )

            # =======================================================================

            if self.reset_placed_if_failed and not success:
                # revert all the placing event in the last step
                blocks = []
                positions = []
                for event_type, event in events:
                    if event_type == "onSave" and event["onSave"].endswith("_placed"):
                        block = event["onSave"].split("_placed")[0]
                        position = event["status"]["position"]
                        blocks.append(block)
                        positions.append(position)

                # =======================================================================

                #
                # todo x: HTTP 请求本地启动的 mineflayer 服务, 远程执行 js 代码
                #
                new_events = self.env.step(
                    f"await givePlacedItemBack(bot, {U.json_dumps(blocks)}, {U.json_dumps(positions)})",
                    programs=self.skill_manager.programs,  # todo x： js 代码
                )
                events[-1][1]["inventory"] = new_events[-1][1]["inventory"]
                events[-1][1]["voxels"] = new_events[-1][1]["voxels"]

            # =======================================================================

            #
            # todo x: 检索向量数据库, 尝试复用已存在技能
            #
            new_skills = self.skill_manager.retrieve_skills(
                query=self.context
                      + "\n\n"
                      + self.action_agent.summarize_chatlog(events)
            )

            # =======================================================================

            #
            #
            #
            system_message = self.action_agent.render_system_message(skills=new_skills)  # todo x: GPT 自己写代码，实现控制逻辑
            human_message = self.action_agent.render_human_message(
                events=events,
                code=parsed_result["program_code"],
                task=self.task,
                context=self.context,
                critique=critique,
            )
            self.last_events = copy.deepcopy(events)
            self.messages = [system_message, human_message]
        else:
            assert isinstance(parsed_result, str)
            self.recorder.record([], self.task)
            print(f"\033[34m{parsed_result} Trying again!\033[0m")

        # =======================================================================

        assert len(self.messages) == 2
        self.action_agent_rollout_num_iter += 1
        done = (
                self.action_agent_rollout_num_iter >= self.action_agent_task_max_retries
                or success
        )
        info = {
            "success": success,
            "conversations": self.conversations,
        }

        # =======================================================================

        if success:
            assert (
                    "program_code" in parsed_result and "program_name" in parsed_result
            ), "program and program_name must be returned when success"
            info["program_code"] = parsed_result["program_code"]
            info["program_name"] = parsed_result["program_name"]
        else:
            print(
                f"\033[32m****Action Agent human message****\n{self.messages[-1].content}\033[0m"
            )
        return self.messages, 0, done, info

    ########################################################################################

    def rollout(self, *, task, context, reset_env=True):
        """todo x:  🔥️🔥️🔥️🔥️ 核心方法.
            - 传入具体任务（task）和上下文（context）, 执行核心逻辑
            - 注意 task 的流转链路
            - 详细功能： GPT 自主分析任务 -> 生成 JS 代码 -> call mineflayer server, 执行 js 代码 -> 反馈 new_skill

        """
        #
        # todo x: ⛔️⛔️⛔️ 注意！核心工作，隐式更新了 self.messages 值，此值在 self.step() 中被使用
        #
        self.reset(task=task, context=context, reset_env=reset_env)  # todo x: 注意更新上下文值

        # =======================================================================

        while True:
            #
            # todo x: GPT 自己分析任务+自主写JS代码+自动执行+自动反馈（判断执行效果）
            #   - 1. call GPT 分析任务，并生成 JS 代码
            #   - 2. 对 JS 代码预处理：基于 python + javascript + babel 预处理
            #   - 3. 通过 HTTP 请求本地启动的 mineflayer 服务, 远程执行 js 代码
            #   - 4. GPT 自主判定：对执行结果进行判断，判断任务是否完成
            #   - 5. 并返回新学会的技能 new_skill
            #
            messages, reward, done, info = self.step()  # todo x: 核心操作， AI(GPT) + JS
            if done:
                break
        return messages, reward, done, info

    ########################################################################################

    #
    #
    #
    def learn(self, reset_env=True):
        """TODO X: 🔥️🔥️🔥️🔥️🔥️ 核心方法
            - Learn a task

        """
        if self.resume:
            # keep the inventory
            self.env.reset(
                options={
                    "mode": "soft",
                    "wait_ticks": self.env_wait_ticks,
                }
            )
        else:
            # clear the inventory
            self.env.reset(
                options={
                    "mode": "hard",
                    "wait_ticks": self.env_wait_ticks,
                }
            )
            self.resume = True

        # =======================================================================

        #
        # todo x: 🔥️🔥️🔥️ HTTP 请求本地启动的 mineflayer 服务
        #   - 获取最近的上一次操作结果
        #   - 接下来， 根据此结果，让GPT推理+判断，生成新的task，并自主执行
        #
        self.last_events = self.env.step("")  # todo x: 此时 code=""，programs="" 为空

        # =======================================================================

        #
        # todo x: 主逻辑部分
        #
        while True:
            if self.recorder.iteration > self.max_iterations:
                print("Iteration limit reached")
                break

            # =======================================================================

            #
            # todo x: 🔥️🔥️🔥️🔥️ 处理 task 模式， 自动处理 vs 手动输入
            #   - 注意此处的 task 和 context 值，后续传递链路
            #
            task, context = self.curriculum_agent.propose_next_task(
                events=self.last_events,
                chest_observation=self.action_agent.render_chest_observation(),
                max_retries=5,
            )
            print(
                f"\033[35mStarting task {task} for at most {self.action_agent_task_max_retries} times\033[0m"
            )

            # =======================================================================

            try:
                #
                # todo x:  🔥️🔥️🔥️🔥️ 传入具体任务（task）和上下文（context）, 执行核心逻辑
                #   - GPT 自主学习 -> 分析任务 -> 生成JS代码 -> 执行JS代码 -> 结果反馈，返回新学会的技能 new_skill
                #
                messages, reward, done, info = self.rollout(
                    task=task,
                    context=context,
                    reset_env=reset_env,
                )
            except Exception as e:
                time.sleep(3)  # wait for mineflayer to exit
                info = {
                    "success": False,
                }
                # reset inventory here
                self.last_events = self.env.reset(
                    options={
                        "mode": "hard",
                        "wait_ticks": self.env_wait_ticks,
                        "inventory": self.last_events[-1][1]["inventory"],
                        "equipment": self.last_events[-1][1]["status"]["equipment"],
                        "position": self.last_events[-1][1]["status"]["position"],
                    }
                )
                # use red color background to print the error
                print("Your last round rollout terminated due to error:")
                print(f"\033[41m{e}\033[0m")
            if (
                    task == "Place and deposit useless items into a chest"
                    or task.startswith("Deposit useless items into the chest at")
            ):
                continue

            # =======================================================================

            if info["success"]:
                print(f"\033[35mCompleted task {task}.\033[0m")

                #
                # todo x: GPT 将新学会的技能（js），保存到向量数据库
                #
                self.skill_manager.add_skill(
                    program_name=info["program_name"],
                    program_code=info["program_code"],
                )
                self.curriculum_agent.completed_tasks.append(task)
            else:
                self.curriculum_agent.failed_tasks.append(task)
                print(
                    f"\033[35mFailed to complete task {task}. Skipping to next task.\033[0m"
                )

            # =======================================================================

            # clean up tasks and dump to disk
            self.curriculum_agent.clean_up_tasks()
            print(
                f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
            )
            print(
                f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            )

        # =======================================================================

        #
        #
        #
        return {
            "completed_tasks": self.curriculum_agent.completed_tasks,
            "failed_tasks": self.curriculum_agent.failed_tasks,
            "control_primitives": self.skill_manager.skills,
        }

    def inference(
            self, task, reset_mode="hard", reset_env=True, early_stop=False, sub_tasks=None
    ):
        self.env.reset(
            options={
                "mode": reset_mode,
                "wait_ticks": self.env_wait_ticks,
            }
        )
        self.curriculum_agent.completed_tasks = []
        self.curriculum_agent.failed_tasks = []

        # =======================================================================

        #
        # todo x: HTTP 请求本地启动的 mineflayer 服务
        #
        self.last_events = self.env.step("")
        if not sub_tasks:
            sub_tasks = self.curriculum_agent.decompose_task(task, self.last_events)  # TODO X: call GPT4, 拆分子任务
        iter_without_new_item = 0
        last_item_history = set()

        # =======================================================================

        while self.curriculum_agent.progress < len(sub_tasks):
            next_task = sub_tasks[self.curriculum_agent.progress]  # todo x: 从子任务集，提取最新子任务
            context = self.curriculum_agent.get_task_context(next_task)
            print(
                f"\033[35mStarting task {next_task} for at most {self.action_agent_task_max_retries} times\033[0m"
            )

            # =======================================================================

            #
            # todo x: 🔥️🔥️🔥️🔥️ 传入子任务(next_task)和上下文(context), 继续执行
            #   - GPT 自主学习 -> 分析任务 -> 生成JS代码 -> 执行JS代码 -> 结果反馈，返回新学会的技能 new_skill
            #
            messages, reward, done, info = self.rollout(
                task=next_task,
                context=context,
                reset_env=reset_env,
            )
            if not self.recorder.item_history - last_item_history:
                iter_without_new_item += 1
            else:
                iter_without_new_item = 0
            last_item_history = self.recorder.item_history.copy()
            if iter_without_new_item >= 3 and early_stop:
                print("Early stop")
                break
            if info["success"]:
                print(f"\033[35mCompleted task {next_task}.\033[0m")
                self.curriculum_agent.completed_tasks.append(next_task)
            else:
                print(
                    f"\033[35mFailed to complete task {next_task}. Skipping to next task.\033[0m"
                )
                self.curriculum_agent.failed_tasks.append(next_task)

            # clean up tasks and dump to disk
            self.curriculum_agent.clean_up_tasks()
            print(
                f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
            )
            print(
                f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            )
