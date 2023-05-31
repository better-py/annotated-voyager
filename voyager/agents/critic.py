from voyager.prompts import load_prompt
from voyager.utils.json_utils import fix_and_parse_json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class CriticAgent:
    """TODO X: 基于 langchain ChatOpenAI 实现
        - langchain 项目：
            - https://github.com/hwchase17/langchain
            - https://github.com/liaokongVFX/LangChain-Chinese-Getting-Started-Guide
            - 众所周知 OpenAI 的 API 无法联网， LangChain 提供  2 个能力：
                - 可以将 LLM 模型与外部数据源进行连接
                - 允许与 LLM 模型进行交互
                - 支持多种模型接口，比如 OpenAI、Hugging Face、AzureOpenAI
        - langchain 核心概念：
            - Loader: 加载器
            - Chain: 链, 把 Chain 理解为任务。一个 Chain 就是一个任务，当然也可以像链条一样，一个一个的执行多个链。
            - Agent: 代理
            - Embedding: 词嵌入
        - langchain 最小用例代码：
            from langchain.llms import OpenAI
            llm = OpenAI(model_name="text-davinci-003",max_tokens=1024)
            llm("怎么评价人工智能")  # 会自动回答一段文本
        - langchain 使用方法非常简单， 可以当成一个智能问答黑盒。
        - 本模块，核心方法是 self.llm() 的调用，这个方法会自动调用 langchain 的模型，返回一个回答。
    """

    def __init__(
            self,
            model_name="gpt-3.5-turbo",
            temperature=0,
            request_timout=120,
            mode="auto",
    ):

        #
        # TODO X: 基于 langchain + ChatOpenAI， 创建一个 LLM 模型对象，
        #   - 调用即返回一个 GPT 回答。
        #   - 跟踪该对象的调用过程
        #
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timout,
        )
        assert mode in ["auto", "manual"]
        self.mode = mode

    def render_system_message(self):
        system_message = SystemMessage(content=load_prompt("critic"))
        return system_message

    def render_human_message(self, *, events, task, context, chest_observation):
        assert events[-1][0] == "observe", "Last event must be observe"
        biome = events[-1][1]["status"]["biome"]
        time_of_day = events[-1][1]["status"]["timeOfDay"]
        voxels = events[-1][1]["voxels"]
        health = events[-1][1]["status"]["health"]
        hunger = events[-1][1]["status"]["food"]
        position = events[-1][1]["status"]["position"]
        equipment = events[-1][1]["status"]["equipment"]
        inventory_used = events[-1][1]["status"]["inventoryUsed"]
        inventory = events[-1][1]["inventory"]

        for i, (event_type, event) in enumerate(events):
            if event_type == "onError":
                print(f"\033[31mCritic Agent: Error occurs {event['onError']}\033[0m")
                return None

        observation = ""

        observation += f"Biome: {biome}\n\n"

        observation += f"Time: {time_of_day}\n\n"

        if voxels:
            observation += f"Nearby blocks: {', '.join(voxels)}\n\n"
        else:
            observation += f"Nearby blocks: None\n\n"

        observation += f"Health: {health:.1f}/20\n\n"
        observation += f"Hunger: {hunger:.1f}/20\n\n"

        observation += f"Position: x={position['x']:.1f}, y={position['y']:.1f}, z={position['z']:.1f}\n\n"

        observation += f"Equipment: {equipment}\n\n"

        if inventory:
            observation += f"Inventory ({inventory_used}/36): {inventory}\n\n"
        else:
            observation += f"Inventory ({inventory_used}/36): Empty\n\n"

        observation += chest_observation

        observation += f"Task: {task}\n\n"

        if context:
            observation += f"Context: {context}\n\n"
        else:
            observation += f"Context: None\n\n"

        print(f"\033[31m****Critic Agent human message****\n{observation}\033[0m")
        return HumanMessage(content=observation)

    def human_check_task_success(self):
        confirmed = False
        success = False
        critique = ""
        while not confirmed:
            success = input("Success? (y/n)")
            success = success.lower() == "y"
            critique = input("Enter your critique:")
            print(f"Success: {success}\nCritique: {critique}")
            confirmed = input("Confirm? (y/n)") in ["y", ""]
        return success, critique

    #
    # todo x: LLM 模型，调用 OpenAI(GPT)，解析 AI 回答, 判断 task 是否成功
    #
    def ai_check_task_success(self, messages, max_retries=5):
        if max_retries == 0:
            print(
                "\033[31mFailed to parse Critic Agent response. Consider updating your prompt.\033[0m"
            )
            return False, ""

        if messages[1] is None:
            return False, ""

        # =======================================================================

        #
        # todo x: LLM， call OpenAI, 返回 AI 回答, 解析该回答中的关键词，判断 task 是否成功
        #
        critic = self.llm(messages).content

        # =======================================================================

        print(f"\033[31m****Critic Agent ai message****\n{critic}\033[0m")
        try:
            response = fix_and_parse_json(critic)
            assert response["success"] in [True, False]
            if "critique" not in response:
                response["critique"] = ""
            return response["success"], response["critique"]
        except Exception as e:
            print(f"\033[31mError parsing critic response: {e} Trying again!\033[0m")
            # todo x: 默认，失败重试 5 次
            return self.ai_check_task_success(
                messages=messages,
                max_retries=max_retries - 1,
            )

    def check_task_success(
            self, *, events, task, context, chest_observation, max_retries=5
    ):
        human_message = self.render_human_message(
            events=events,
            task=task,
            context=context,
            chest_observation=chest_observation,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        # =======================================================================

        if self.mode == "human":
            return self.human_check_task_success()  # todo x: 人工确认
        elif self.mode == "auto":
            #
            #  todo x: LLM 模型，调用 OpenAI(GPT)，解析 AI 回答, 判断 task 是否成功
            #
            return self.ai_check_task_success(
                messages=messages, max_retries=max_retries
            )  # todo x: 自动确认
        else:
            raise ValueError(f"Invalid critic agent mode: {self.mode}")
