import nonebot
from nonebot.adapters.mirai import Bot

nonebot.init()
nonebot.get_driver().register_adapter('mirai', Bot)
nonebot.load_builtin_plugins() # 加载 nonebot 内置插件
nonebot.run()
