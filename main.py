import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent

@register(
    "auto_approve_all",
    "知鱼",
    "自动同意所有群邀请和好友申请并发送消息",
    "1.0",
    "https://github.com/ovoox/zhiyu-astrbot-zdtyfxx",
)
class AutoApproveAll(Star):
    def __init__(self, context: Context):
        super().__init__(context)
      #好友发消息改这里
        self.friend_welcome_msg = "好友发消息请改我"
      #群聊发消息改这里
        self.group_welcome_msg = "群聊发消息请改我"

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
