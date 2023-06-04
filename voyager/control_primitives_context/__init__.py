import pkg_resources
import os
import voyager.utils as U


def load_control_primitives_context(primitive_names=None):
    """todo x: 遍历当前目录， 提取当前文件夹下的 js 文件， 以 list 返回

    """
    package_path = pkg_resources.resource_filename("voyager", "")
    if primitive_names is None:
        #
        #
        #
        primitive_names = [
            primitive[:-3]

            #
            # todo x: 注意是当前路径
            #
            for primitive in os.listdir(f"{package_path}/control_primitives_context")
            if primitive.endswith(".js")
        ]

    #
    # todo x: 提取当前路径下的 js 文件
    #
    primitives = [
        U.load_text(f"{package_path}/control_primitives_context/{primitive_name}.js")
        for primitive_name in primitive_names
    ]
    return primitives
