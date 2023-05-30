import pkg_resources
import os
import voyager.utils as U


#
# todo x： 遍历 control_primitives 目录下的 js 文件， 并返回 js 文件内容
#
def load_control_primitives(primitive_names=None):
    package_path = pkg_resources.resource_filename("voyager", "")
    if primitive_names is None:
        #
        # todo x: 遍历 control_primitives 文件夹，
        #
        primitive_names = [
            primitives[:-3]

            #
            for primitives in os.listdir(f"{package_path}/control_primitives")
            if primitives.endswith(".js")
        ]

    #
    # todo x: 遍历 control_primitives 文件夹，并返回解析的 js 文件内容
    #
    primitives = [
        # todo x: 解析 js 文件内容
        U.load_text(f"{package_path}/control_primitives/{primitive_name}.js")
        for primitive_name in primitive_names
    ]
    return primitives
