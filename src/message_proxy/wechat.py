import json
import logging

import httpx
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from message_proxy.config import settings
from message_proxy.logging_config import get_logger

logger = get_logger(__name__)


class Wechat:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.http_client = client
        self._get_access_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={settings.wechat_copid}&corpsecret={settings.wechat_corpsecret}"
        self.touid = "@all"

    @retry(
        reraise=True,
        stop=(stop_after_delay(30) | stop_after_attempt(5)),
        wait=wait_fixed(2),
        after=after_log(logger, logging.WARNING),
        retry=retry_if_exception_type((httpx.RequestError,)),
    )
    async def fetch_new_token(self) -> str:
        """
        获取token, 没有实现缓存,
        因为企业微信可能会出于运营需要，提前使access_token失效，开发者应实现access_token失效时重新获取的逻辑。
        且调用频率不高
        有需要再实现缓存
        """
        logger.info("Access Key 已过期或未初始化，正在刷新...")
        try:
            response = await self.http_client.get(self._get_access_token_url)
            response.raise_for_status()  # 直接抛出非200异常
            response_data = response.json()
            if response_data["errcode"] == 0:
                logger.info(
                    f"获取 微信 Access Token 成功, 有效期：{response_data['expires_in']}"
                )
                return response_data["access_token"]
            else:
                raise response_data["errmsg"]
        except httpx.HTTPStatusError as e:
            logger.error(f"获取 微信 Access Token 失败，发生网络错误：{e}")
            raise
        except Exception as e:
            logger.error(f"获取 微信 Access Token 失败，发生未知错误:{e}")
            raise

    async def send_message(self, token: str, message: str, message_type: str = "text"):
        # 发送文本消息到微信企业号, 参数: 企业ID, 应用密钥, 应用ID, 接收用户ID, 消息内容
        # touid支持多个用户，用‘|’分隔，如"UserID1|UserID2"
        # 返回值: 微信接口返回的结果
        logger.info(f"正在向用户 {self.touid} 发送消息: {message}")
        try:
            send_msg_url = (
                f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
            )
            data = {
                "touser": self.touid,
                "agentid": settings.wechat_agentid,
                "msgtype": message_type,
                message_type: {"content": message},
                "duplicate_check_interval": 600,
            }
            logger.debug(f"发送请求体:{data}")
            response = await self.http_client.post(send_msg_url, json=data)
        except Exception as e:
            logger.error(f"向用户 {self.touid} 发送消息失败, 错误信息: {str(e)}")
            raise e
        response_json = response.json()
        logger.debug(f"向用户 {self.touid} 发送消息完成, 返回结果: {response_json}")
        return response_json

    async def send_message_with_token(self, message: str, is_markdown: bool = False):
        token = await self.fetch_new_token()
        message_type = "markdown" if is_markdown else "text"
        return await self.send_message(token, message, message_type)
