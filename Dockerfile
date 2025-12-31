# 多阶段构建 - 阶段1: 构建阶段
FROM python:3.12-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache gcc musl-dev

# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖配置文件和源代码
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# 使用uv安装依赖（不包含开发依赖，不使用缓存，不使用可编辑模式）
RUN uv sync --frozen --no-dev --no-editable --no-cache && \
    rm -rf /root/.cache/uv /tmp/*

# 多阶段构建 - 阶段2: 运行阶段（最小体积镜像）
FROM python:3.12-alpine

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2 \
    PATH="/app/.venv/bin:$PATH"

# 从构建阶段只复制必要的文件
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# 清理不必要的文件和缓存
RUN find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type f -name '*.pyc' -delete 2>/dev/null || true && \
    find /app -type f -name '*.pyo' -delete 2>/dev/null || true && \
    find /app/.venv -type d -name '*.dist-info' -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /root/.cache /tmp/* /var/tmp/*

# 暴露端口
EXPOSE 8000

# 健康检查 - 使用更轻量的方式（不依赖httpx）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# 启动命令
CMD ["uvicorn", "message_proxy.main:app", "--host", "0.0.0.0", "--port", "8000"]
