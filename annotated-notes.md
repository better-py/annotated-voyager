
# voyager 源码分析笔记：

## 注解说明：

- ✅️ `# todo x`： 为注解标识符， 方便利用 IDE 的 TODO 工具，快速筛查注解点。

![](./images/note-1.png)


## 核心依赖库：

- ✅️ [javascript](https://pypi.org/project/javascript/)
    - https://github.com/extremeheat/JSPyBridge
    - 基于此库， 实现在 python 中调用 js lib
    - 项目依赖处： [Voyager.step](Voyager.step)

## 源码入口：

- ✅️ [voyager/voyager.py](voyager/voyager.py)


