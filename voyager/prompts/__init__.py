import pkg_resources
import voyager.utils as U


def load_prompt(prompt):
    #
    # todo x: 解析当前路径下的 prompt 文件夹， 并返回对应的 prompt 内容
    #
    package_path = pkg_resources.resource_filename("voyager", "")
    return U.load_text(f"{package_path}/prompts/{prompt}.txt")
