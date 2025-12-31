import pytest  # noqa: F401

from src.message_proxy.config import settings


def test_config():
    assert settings.log_level == "DEBUG"
    assert settings.docker_mode is False
    assert settings.wechat_copid == "ww5829cfd5388f15ea"
