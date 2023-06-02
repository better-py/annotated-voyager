import pkg_resources
import voyager.utils as U


def load_prompt(prompt):
    """
    todo x: 解析当前路径下的 prompt 文件夹， 并返回指定 prompt 文件(txt)内容
        1. prompts/ 文件夹下， 已对 prompts 文件翻译（后缀为 .zh.yml), 值得学习 prompts 编写技巧（质量非常高）
        2. agents/ 源码，有对 prompts 文件的使用， 理解整个使用链路
    """
    package_path = pkg_resources.resource_filename("voyager", "")  # todo x: 加载当前包的路径
    return U.load_text(f"{package_path}/prompts/{prompt}.txt")  # todo x: 加载+解析指定 prompt 文件（txt) 内容
