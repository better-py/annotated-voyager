# voyager 源码分析笔记：

## 阅读提示：

- ✅️ `# todo x`： 为注解标识符， 方便利用 IDE 的 TODO 工具，快速筛查注解点。
- ✅️ 源码文件，`核心链路和功能`， 都做了`详细注解`，注解`越多`越重要，注意抓重点。
- ❎️ `未注解`的代码，通常都可以`忽略+跳过不看`（不重要+不影响理解）。


<img width="400" src="./images/notes/img1.png"  alt=""/>

> 项目入口说明：

- ✅️ 建议从 [voyager/voyager.py](voyager/voyager.py) 的 `learn()` 方法，读起。


<img width="300" src="./images/notes/img2.png"  alt=""/>


> agents:

- ✅️ [voyager/agents/curriculum.py](voyager/agents/curriculum.py): GPT BOT 自主学习技能
- ✅️ [voyager/agents/action.py](voyager/agents/action.py): GPT BOT 执行任务
- ✅️ [voyager/agents/critic.py](voyager/agents/critic.py): GPT BOT 对执行结果，自主评估
- ✅️ [voyager/agents/skill.py](voyager/agents/skill.py): GPT BOT 记录新学习的技能（new_skill)


<img width="400" src="./images/notes/img3.png"  alt=""/>



## 补充知识：

### MineCraft 游戏相关：

- ✅️ [MineCraft](https://www.minecraft.net/) 是个沙盒游戏，玩家可以自由创造和破坏各种方块，探索和冒险。
- ✅️ [MineCraft](https://www.minecraft.net/) 游戏，有两种模式：`创造模式` 和 `生存模式`。
- ✅️ 已被`微软`收购，所以代码中的`帐号登录` 是`微软`的帐号登录。

> minecraft 游戏， 补充 Commands 和 Cheats 说明：

- ✅️ https://www.ign.com/wikis/minecraft/All_Minecraft_Commands_and_Cheats
- ✅️ 项目源码 [voyager/env/mineflayer/index.js](voyager/env/mineflayer/index.js) 涉及使用的 minecraft 指令，
  可以在上面的链接中查找到。

## 主要模块说明：

- ✅️ Voyager 的入口方法：`Voyager.learn()`, 由此依次展开。
- ✅️ Voyager 项目， 主要分为3部分：
    - ✅️ Python 部分： 代码在 [voyager](voyager) 目录下
    - ✅️ JS 部分： 代码在 [voyager/control_primitives](voyager/control_primitives) 目录下， 定义了一组JS脚本
    - ✅️ Nodejs 部分： 代码在 [voyager/env/mineflayer](voyager/env/mineflayer) 目录下， 启动一个 http server, 定义一组
      HTTP API.

> prompts 部分：

- ✅️ [voyager/prompts](voyager/prompts): 存放 `prompts`
- ✅️ 该目录下 [\_\_init__.py](voyager/prompts/__init__.py) 中的 `load_prompts()` 方法， 该方法会加载 `prompts`
  目录下的所有 `prompts` 文件。
- ✅️ 跟踪 `load_prompts()` 的引用链， 就可以找到 `prompts` 使用方法。

### Python 部分核心依赖包：

1. langchain/openai/tiktoken: GPT 相关
2. javascript： 这个包比较有意思， 实现在 python 中调用 js lib。（我笔记有注解）
3. chromadb： 向量数据库，存储 task 中间步
4. minecraft_launcher_lib： minecraft 服务器登录 + 拼接 minecraft 指令

### JS 脚本：

- ✅️ voyager/control_primitives： 这目录有写了一组 minecraft bot 指令脚本

### Nodejs 服务：

- ✅️ voyager/env/mineflayer： 这里基于 `nodejs + express`, 定义了一个本地的 http server，定义的一组 HTTP API，
- ✅️ Python 代码部分，在执行 task 时， 调用的本地 HTTP API，就对应这里.

## 核心依赖库：

- ✅️ [javascript](https://pypi.org/project/javascript/)
    - https://github.com/extremeheat/JSPyBridge
    - 基于此库， 实现在 python 中调用 js lib
    - 项目依赖处： [Voyager.step](Voyager.step)

## 源码入口：

- ✅️ [voyager/voyager.py](voyager/voyager.py)

### 执行 JS 代码：

- ✅️ JS 代码位置： [control_primitives](voyager/control_primitives)
    - voyager.step() 中调用 load_control_primitives() 在 [control_primitives/__init
      __.py](voyager/control_primitives/__init__.py)

### 辅助模块：

- ✅️ [VoyagerEnv](voyager/env/bridge.py): `voyager/env/bridge.py`
- ✅️ [MinecraftInstance](voyager/env/minecraft_launcher.py): `voyager/env/minecraft_launcher.py`

#### mineflayer 本地服务(端口3000):

- ✅️ [mineflayer](voyager/env/mineflayer/index.js): `voyager/env/mineflayer/index.js`
    - 这是基于 `nodejs + express` 开发的一个 js 服务
    - 在 `voyager/env/bridge.py` 中 `get_mineflayer_process（）` 实现本地启动
    - 默认 HTTP server： `http://localhost:3000`， 端口： `3000`
- ✅️ 此模块，内部定义了一组 HTTP API：
    - `/start`: 调用此API， 启动一个 `bot`
    - `/step`: 核心功能方法, 注意内部的 `bot` 调用流程， 🔥️🔥️🔥️
    - `/stop`
    - `/pause`
- ✅️ 这组 API， 也是上述 python 代码调用中，使用的。


