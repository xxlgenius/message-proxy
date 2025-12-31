# 多阶段构建 - 阶段1: 构建阶段
FROM python:3.12-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖配置文件和源代码
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# 使用uv安装依赖到只读环境
RUN uv sync --frozen --no-dev --no-editable

# 多阶段构建 - 阶段2: 运行阶段（最小体积镜像）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 从构建阶段复制虚拟环境和源代码
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

# 启动命令
CMD ["uvicorn", "message_proxy.main:app", "--host", "0.0.0.0", "--port", "8000"]
