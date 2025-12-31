from unittest.mock import AsyncMock, call, patch

import httpx
import pytest

from message_proxy.wechat import Wechat


class TestWechat:
    @pytest.fixture
    def wechat_instance(self):
        mock_client = AsyncMock()
