import pkg_resources
import voyager.utils as U


def load_prompt(prompt):
    """
    todo x: 解析当前路径下的 prompt 文件夹， 并返回指定 prompt 文件(txt)内容
        1. prompts/ 文件夹下， 已对 prompts 文件翻译（后缀为 .zh.yml), 值得学习 prompts 编写技巧（质量非常高）
        2. agents/ 源码，有对 prompts 文件的使用， 理解整个使用链路
        3. 综合说明：
            - prompts 是 GPT4 自主学习+规划任务+执行+结果反馈+形成能力（skill）+ 进一步循环迭代的过程
            - 整个链路是不断循环+反馈+迭代+优化， 让 GPT4 不断强化自我能力， 自主探索+玩游戏（成为高级玩家）
        4. prompts 功能说明：
            a. curriculum: 让 GPT4 根据现存条件， 推理+学习+推荐下一步最佳任务路线。
            b. curriculum_qa_step1_ask_questions: 让 GPT4 根据输入， 提高质量问题（辅助提升游戏效率）。
            c. curriculum_qa_step2_answer_questions: 让 GPT4 诚实回答 游戏相关知识。
            d. curriculum_task_decomposition: 让 GPT4 拆解子任务。
            e. action_template: 让 GPT4 自己写代码， 来处理任务
            f. critic: 任务反馈，让 GPT4 对任务执行的结果，做综合评价（打分），给出鼓励 or 批评，促进 GPT4 自己进步
            f. skill: 让 GPT4 读代码 + 一句话总结
    """
    package_path = pkg_resources.resource_filename("voyager", "")  # todo x: 加载当前包的路径
    return U.load_text(f"{package_path}/prompts/{prompt}.txt")  # todo x: 加载+解析指定 prompt 文件（txt) 内容
