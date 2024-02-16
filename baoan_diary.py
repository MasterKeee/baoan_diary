import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_LINHUN = "https://api.linhun.vip/api/" #https://api.linhun.vip/


@plugins.register(name="baoan_diary",
                  desc="baoan_diary插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class baoan_diary(Plugin):
    content = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f""
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        
        if self.content == "保安日记":
            logger.info(f"[baoan_diary] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__),"config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return
            reply = Reply()
            result = self.baoan_diary()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def baoan_diary(self):
        url = BASE_URL_LINHUN + "security"
        params = f"apiKey={self.config_data['baoan_diary_apikey']}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        try:
            response = requests.get(url=url, params=params, headers=headers)
            json_data = response.json()
            if json_data.get('code') == 200:
                text = response.json().get('body', None)
                logger.info(json_data)
                return text
            else:
                logger.error(json_data)
        except Exception as e:
            logger.error(f"抛出异常:{e}")
            
        logger.error("所有接口都挂了,无法获取")
        return None
