import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent

@register(
    "auto_approve_all",
    "Developer",
    "自动同意所有群邀请和好友申请，并发送欢迎消息",
    "1.0.1",
    "https://github.com/your-repo/auto_approve_all",
)
class AutoApproveAll(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.friend_welcome_msg = "你好！感谢添加我为好友，有什么我可以帮你的吗？"
        self.group_welcome_msg = "大家好！我是机器人，很高兴加入本群～"

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def event_monitoring(self, event: AstrMessageEvent):
        raw_message = getattr(event.message_obj, 'raw_message', None)
        
        if not isinstance(raw_message, dict) or raw_message.get("post_type") != "request":
            return

        if not isinstance(event, AiocqhttpMessageEvent):
            return
            
        client = event.bot
        flag = raw_message.get("flag")
        user_id = raw_message.get("user_id")
        
        if raw_message.get("request_type") == "friend":
            try:
                await client.set_friend_add_request(flag=flag, approve=True)
                await client.send_private_msg(user_id=user_id, message=self.friend_welcome_msg)
            except Exception as e:
                logger.error(f"处理好友申请失败: {e}")

        elif (raw_message.get("request_type") == "group" and 
              raw_message.get("sub_type") == "invite"):
            group_id = raw_message.get("group_id")
            try:
                await client.set_group_add_request(flag=flag, sub_type="invite", approve=True)
                await asyncio.sleep(1)
                await client.send_group_msg(group_id=group_id, message=self.group_welcome_msg)
            except Exception as e:
                logger.error(f"处理群邀请失败: {e}")

    async def terminate(self):
        pass
