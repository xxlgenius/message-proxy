# import json
# import secrets
# from typing import Any

# from pydantic import Field, SecretStr, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """使用 Pydantic V2 最新语法的配置类"""

    # 模型配置
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 应用配置
    wechat_copid: str | None = None
    wechat_corpsecret: str | None = None
    wechat_agentid: str | None = None
    app_token: str | None = None
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 安全配置 - 使用 SecretStr 隐藏敏感信息
    # secret_key: SecretStr = Field(
    #     default_factory=lambda: SecretStr(secrets.token_urlsafe(32))
    # )
    # access_token_expire_minutes: int = 30

    # CORS 配置
    # backend_cors_origins: list[str] = ["http://localhost:3000"]

    # 日志配置
    log_level: str = "INFO"

    # Docker 配置
    docker_mode: bool = False

    # @field_validator("backend_cors_origins", mode="before")
    # @classmethod
    # def parse_cors_origins(cls, v: Any) -> list[str]:
    #     """解析 CORS 来源"""
    #     if isinstance(v, str):
    #         if v.startswith("[") and v.endswith("]"):
    #             return json.loads(v)
    #         else:
    #             # 逗号分隔的字符串
    #             return [item.strip() for item in v.split(",") if item.strip()]
    #     return v

    # @field_validator("debug", mode="before")
    # @classmethod
    # def parse_bool(cls, v: Any) -> bool:
    #     """解析布尔值"""
    #     if isinstance(v, str):
    #         return v.lower() in ("true", "1", "yes", "on", "t")
    #     return bool(v)

    # @field_validator("port", mode="before")
    # @classmethod
    # def validate_port(cls, v: Any) -> int:
    #     """验证端口号"""
    #     if isinstance(v, str):
    #         v = int(v)
    #     if not 1 <= v <= 65535:  # noqa: PLR2004
    #         raise ValueError("端口号必须在 1-65535 之间")
    #     return v


# 创建实例
settings = Settings()
