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
        # 可自定义欢迎语
        self.friend_welcome_msg = "你好！感谢添加我为好友，有什么我可以帮你的吗？"
        self.group_welcome_msg = "大家好！我是机器人，很高兴加入本群～"

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def event_monitoring(self, event: AstrMessageEvent):
        """监听好友申请和群邀请并自动同意，随后发送欢迎消息"""
        raw_message = getattr(event.message_obj, 'raw_message', None)
        
        if not isinstance(raw_message, dict) or raw_message.get("post_type") != "request":
            return

        logger.info(f"收到请求事件: {raw_message}")
        
        if not isinstance(event, AiocqhttpMessageEvent):
            logger.error("事件类型不是 AiocqhttpMessageEvent，无法处理")
            return
            
        client = event.bot
        flag = raw_message.get("flag")
        user_id = raw_message.get("user_id")
        
        # 处理好友申请
        if raw_message.get("request_type") == "friend":
            try:
                await client.set_friend_add_request(flag=flag, approve=True)
                logger.info(f"已自动同意好友申请 from {user_id}")
                
                # 发送欢迎消息
                try:
                    await client.send_private_msg(user_id=user_id, message=self.friend_welcome_msg)
                    logger.info(f"已向好友 {user_id} 发送欢迎消息")
                except Exception as e:
                    logger.warning(f"发送好友欢迎消息失败: {e}")

                # 获取用户信息用于日志（可选）
                nickname = "未知用户"
                try:
                    user_info = await client.get_stranger_info(user_id=user_id)
                    nickname = user_info.get("nickname", "未知用户")
                except Exception as e:
                    logger.warning(f"获取用户信息失败: {e}")
                
                await self.log_and_notify(f"已自动同意好友申请: {nickname}({user_id})")

            except Exception as e:
                logger.error(f"同意好友申请失败: {e}")

        # 处理群邀请
        elif (raw_message.get("request_type") == "group" and 
              raw_message.get("sub_type") == "invite"):
            group_id = raw_message.get("group_id")
            try:
                await client.set_group_add_request(
                    flag=flag, 
                    sub_type="invite", 
                    approve=True
                )
                logger.info(f"已自动同意群邀请: 群{group_id} from {user_id}")
                
                # 等待一小会儿，确保机器人已入群（部分 OneBot 实现需要）
                await asyncio.sleep(1)

                # 发送群欢迎消息
                try:
                    await client.send_group_msg(group_id=group_id, message=self.group_welcome_msg)
                    logger.info(f"已向群 {group_id} 发送欢迎消息")
                except Exception as e:
                    logger.warning(f"发送群欢迎消息失败: {e}")

                # 获取群信息用于日志（可选）
                group_name = "未知群聊"
                try:
                    group_info = await client.get_group_info(group_id=group_id)
                    group_name = group_info.get("group_name", "未知群聊")
                except Exception as e:
                    logger.warning(f"获取群信息失败: {e}")
                
                await self.log_and_notify(
                    f"已自动同意群邀请: {group_name}({group_id})，邀请人: {user_id}"
                )
                
            except Exception as e:
                logger.error(f"同意群邀请失败: {e}")

    async def log_and_notify(self, message: str):
        """记录日志（可扩展为发送通知）"""
        logger.info(f"自动同意操作: {message}")

    async def terminate(self):
        """插件终止时的清理工作"""
        logger.info("自动同意插件已卸载")
