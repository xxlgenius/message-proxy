from fastapi import APIRouter, Depends, Query, Request

from message_proxy.logging_config import get_logger
from message_proxy.model import WechatBody
from message_proxy.wechat import Wechat

logger = get_logger(__name__)

router = APIRouter()


async def get_http_client(request: Request):
    """获取httpx客户端的依赖注入函数"""
    return request.app.state.http_client


async def get_wechat(client=Depends(get_http_client)):
    """获取Wechat实例的依赖注入函数"""
    return Wechat(client=client)


@router.get("/health")
async def health():
    return {"status": "OK"}


@router.get("/wechat")
async def wechat_send_message_get(
    message: str = Query(..., description="要发送的文本消息"),
    wechat: Wechat = Depends(get_wechat),
):
    """发送文本消息到微信企业号

    Args:
        message: 要发送的文本消息内容
        wechat: Wechat实例（通过依赖注入）

    Returns:
        发送结果
    """
    try:
        response = await wechat.send_message_with_token(message)
        if response["errcode"] == 0:
            return {"success": True, "message": "消息发送成功", "data": response}
        raise Exception
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return {"success": False, "message": "消息发送失败", "error": str(e)}


@router.post("/wechat")
async def wechat_send_message_post(
    wechat_args: WechatBody, wechat: Wechat = Depends(get_wechat)
):
    """发送文本消息到微信企业号

    Args:
        wechat: Wechat实例（通过依赖注入）

    Returns:
        发送结果
    """
    if wechat_args.message is None:
        return {"success": False, "message": "消息发送失败", "error": "message为空"}
    try:
        response = await wechat.send_message_with_token(wechat_args.message)
        if response["errcode"] == 0:
            return {"success": True, "message": "消息发送成功", "data": response}
        raise Exception
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return {"success": False, "message": "消息发送失败", "error": str(e)}


@router.get("/")
async def read_root():
    logger.debug("访问根路径")
    logger.info("首页被访问")
    return {"message": "Hello World"}
