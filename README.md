# annotated-voyager:

## 🆚️ 源码分析笔记:

- ✅️ [annotated-notes.md](annotated-notes.md): 笔记
- ✅️ [annotated-notes.ipynb](annotated-notes.ipynb): 重要代码片段分析

## 🔥️源码目录详细说明:

- ✅️ [voyager/voyager.py](voyager/voyager.py): 源码入口. 请从 .learn() 方法开始看！
- ✅️ 如下是完整的源码目录结构说明：

```ruby

❯ tree ./voyager/ -L 3
./voyager/
├── __init__.py
├── agents                  // ✅️ GPT bot 代理
│   ├── __init__.py
│   ├── action.py           // 🔥️ GPT bot 任务执行: 生成js代码 + 执行js代码
│   ├── critic.py           // 🔥️ GPT bot 任务执行结果监督
│   ├── curriculum.py       // 🔥️ GPT bot 自主学习过程
│   └── skill.py            // 🔥️ GPT bot 技能库
├── control_primitives      // ✅️ GPT bot 一组初始技能（js代码）
│   ├── __init__.py         // 🔥️ 注意此文件里的方法！（提取js代码）
│   ├── killMob.js
│   ├── mineBlock.js
│   ├── shoot.js
├── control_primitives_context // ✅️ GPT bot 一组初始技能上下文（js代码）
│   ├── __init__.py            // 🔥️ 注意此文件里的方法！（提取js代码）
│   ├── mineBlock.js
│   ├── mineflayer.js
├── env                       // ✅️ GPT bot 依赖的本地运行的 mineflayer server 代理，用于执行 js 代码
│   ├── __init__.py
│   ├── bridge.py             // 🔥️ GPT bot 的 HTTP 代理，HTTP POST 执行 JS 代码.
│   ├── minecraft_launcher.py // 🔥️ Minecraft 登录 + 启动 mineflayer server 
│   ├── mineflayer
│   │   ├── index.js          // 🔥️ mineflayer server 启动，内部定义一组 HTTP API(前面 python 中的 bridge.py 会调用这些 API)
│   │   ├── lib
│   │   ├── mineflayer-collectblock
│   │   └── package.json
│   └── process_monitor.py
├── prompts                   // ✅️ GPT bot 的 prompts 定义，学习 prompts 编写技巧（请看 .zh.yml 翻译文件）
│   ├── __init__.py
│   ├── action_response_format.txt
│   ├── action_template.txt
│   ├── action_template.zh.yml // 🔥️ 请看此 prompt 翻译文件
│   ├── critic.txt
│   ├── critic.zh.yml          // 🔥️ 请看此 prompt 翻译文件
│   ├── curriculum.txt
│   ├── curriculum.zh.yml
├── utils                     // ✅️ GPT bot 依赖的工具类, txt，json，读写方法
│   ├── __init__.py
│   ├── file_utils.py
│   ├── json_utils.py
│   └── record_utils.py
└── voyager.py               // 🚀️️ GPT bot 主程序入口，请从 .learn() 方法开始看！

9 directories, 54 files


```





️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥️🔥


---

# Voyager: An Open-Ended Embodied Agent with Large Language Models

<div align="center">

[[Website]](https://voyager.minedojo.org/)
[[Arxiv]](https://arxiv.org/abs/2305.16291)
[[PDF]](https://arxiv.org/pdf/2305.16291.pdf)
[[Tweet]](https://twitter.com/DrJimFan/status/1662115266933972993?s=20)

[![Python Version](https://img.shields.io/badge/Python-3.9-blue.svg)](https://github.com/MineDojo/Voyager)
[![GitHub license](https://img.shields.io/github/license/MineDojo/Voyager)](https://github.com/MineDojo/Voyager/blob/main/LICENSE)
______________________________________________________________________


https://github.com/MineDojo/Voyager/assets/25460983/ce29f45b-43a5-4399-8fd8-5dd105fd64f2

![](images/pull.png)


</div>

We introduce Voyager, the first LLM-powered embodied lifelong learning agent
in Minecraft that continuously explores the world, acquires diverse skills, and
makes novel discoveries without human intervention. Voyager consists of three
key components: 1) an automatic curriculum that maximizes exploration, 2) an
ever-growing skill library of executable code for storing and retrieving complex
behaviors, and 3) a new iterative prompting mechanism that incorporates environment
feedback, execution errors, and self-verification for program improvement.
Voyager interacts with GPT-4 via blackbox queries, which bypasses the need for
model parameter fine-tuning. The skills developed by Voyager are temporally
extended, interpretable, and compositional, which compounds the agent’s abilities
rapidly and alleviates catastrophic forgetting. Empirically, Voyager shows
strong in-context lifelong learning capability and exhibits exceptional proficiency
in playing Minecraft. It obtains 3.3× more unique items, travels 2.3× longer
distances, and unlocks key tech tree milestones up to 15.3× faster than prior SOTA.
Voyager is able to utilize the learned skill library in a new Minecraft world to
solve novel tasks from scratch, while other techniques struggle to generalize.

In this repo, we provide Voyager code. This codebase is under [MIT License](LICENSE).

# Installation

Voyager requires Python ≥ 3.9 and Node.js ≥ 16.13.0. We have tested on Ubuntu 20.04, Windows 11, and macOS. You need to
follow the instructions below to install Voyager.

## Python Install

```
git clone https://github.com/MineDojo/Voyager
cd Voyager
pip install -e .
```

## Node.js Install

In addition to the Python dependencies, you need to install the following Node.js packages:

```
cd voyager/env/mineflayer
npm install -g npx
npm install
cd mineflayer-collectblock
npx tsc
cd ..
npm install
```

## Minecraft Instance Install

Voyager depends on Minecraft game. You need to install Minecraft game and set up a Minecraft instance.

Follow the instructions in [Minecraft Login Tutorial](installation/minecraft_instance_install.md) to set up your
Minecraft Instance.

## Fabric Mods Install

You need to install fabric mods to support all the features in Voyager. Remember to use the correct Fabric version of
all the mods.

Follow the instructions in [Fabric Mods Install](installation/fabric_mods_install.md) to install the mods.

# Getting Started

Voyager uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You can get one
from [here](https://platform.openai.com/account/api-keys).

After the installation process, you can run Voyager by:

```python
from voyager import Voyager

# you can also use mc_port instead of azure_login, but azure_login is highly recommended
azure_login = {
    "client_id": "YOUR_CLIENT_ID",
    "redirect_url": "https://127.0.0.1/auth-response",
    "secret_value": "[OPTIONAL] YOUR_SECRET_VALUE",
    "version": "fabric-loader-0.14.18-1.19",  # the version Voyager is tested on
}
openai_api_key = "YOUR_API_KEY"

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()
```

* If you are running with `Azure Login` for the first time, it will ask you to follow the command line instruction to
  generate a config file.
* For `Azure Login`, you also need to select the world and open the world to LAN by yourself. After you
  run `voyager.learn()` the game will pop up soon, you need to:
    1. Select `Singleplayer` and press `Create New World`.
    2. Set Game Mode to `Creative` and Difficulty to `Peaceful`.
    3. After the world is created, press `Esc` key and press `Open to LAN`.
    4. Select `Allow cheats: ON` and press `Start LAN World`. You will see the bot join the world soon.

# FAQ

If you have any questions, please check our [FAQ](FAQ.md) first before opening an issue.

# Paper and Citation

If you find our work useful, please consider citing us!

```bibtex
@article{wang2023voyager,
  title   = {Voyager: An Open-Ended Embodied Agent with Large Language Models},
  author  = {Guanzhi Wang and Yuqi Xie and Yunfan Jiang and Ajay Mandlekar and Chaowei Xiao and Yuke Zhu and Linxi Fan and Anima Anandkumar},
  year    = {2023},
  journal = {arXiv preprint arXiv: Arxiv-2305.16291}
}
```

Disclaimer: This project is strictly for research purposes, and not an official product from NVIDIA.
