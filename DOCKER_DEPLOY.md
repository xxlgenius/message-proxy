# Docker 部署文档

本文档说明如何将 message-proxy 项目打包成 Docker 镜像并进行部署。

## 特性

- ✅ **多阶段构建**：最小化镜像体积
- ✅ **非 root 用户运行**：提高安全性
- ✅ **健康检查**：自动监控服务状态
- ✅ **环境变量配置**：通过 Docker env 传递参数
- ✅ **Python 3.12-slim**：基于轻量级基础镜像

## 镜像体积优化

通过多阶段构建，最终镜像体积预计在 150-250MB 之间（不含应用数据）。

优化措施：
1. 使用 `python:3.12-slim` 轻量级基础镜像
2. 多阶段构建，仅复制必要的虚拟环境和源代码
3. 使用 `uv` 包管理器，依赖安装更高效
4. 清理构建缓存和临时文件
5. 使用非 root 用户，减少潜在的安全风险

## 快速开始

### 方法一：使用 Docker Compose（推荐）

1. **配置环境变量**

复制示例配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：
```bash
# 微信企业配置（必填）
WECHAT_COPID=your_corp_id
WECHAT_CORPSECRET=your_corp_secret
WECHAT_AGENTID=your_agent_id

# 日志级别（可选）
LOG_LEVEL=INFO
```

2. **构建并启动服务**

```bash
docker-compose up -d --build
```

3. **查看日志**

```bash
docker-compose logs -f message-proxy
```

4. **停止服务**

```bash
docker-compose down
```

### 方法二：使用 Docker 命令

1. **构建镜像**

```bash
docker build -t message-proxy:latest .
```

2. **运行容器**

```bash
docker run -d \
  --name message-proxy \
  -p 8000:8000 \
  -e WECHAT_COPID=your_corp_id \
  -e WECHAT_CORPSECRET=your_corp_secret \
  -e WECHAT_AGENTID=your_agent_id \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  message-proxy:latest
```

3. **查看日志**

```bash
docker logs -f message-proxy
```

4. **停止容器**

```bash
docker stop message-proxy
docker rm message-proxy
```

## 环境变量说明

所有环境变量都可以通过 Docker 的 `-e` 参数或 docker-compose.yml 的 `environment` 部分传递。

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `WECHAT_COPID` | 是 | - | 微信企业号 CorpID |
| `WECHAT_CORPSECRET` | 是 | - | 微信企业号 CorpSecret |
| `WECHAT_AGENTID` | 是 | - | 微信企业号应用 AgentID |
| `HOST` | 否 | 0.0.0.0 | 服务监听地址 |
| `PORT` | 否 | 8000 | 服务监听端口 |
| `LOG_LEVEL` | 否 | INFO | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `DOCKER_MODE` | 否 | false | Docker 模式标识 |

## 验证部署

1. **检查容器状态**

```bash
docker ps | grep message-proxy
```

2. **健康检查**

```bash
docker inspect --format='{{.State.Health.Status}}' message-proxy
```

3. **访问 API 文档**

在浏览器中打开：http://localhost:8000/docs

4. **测试 API**

```bash
curl http://localhost:8000/docs
```

## 生产环境建议

### 1. 使用特定版本标签

```bash
docker build -t message-proxy:v1.0.0 .
docker run -d --name message-proxy message-proxy:v1.0.0
```

### 2. 持久化日志（可选）

在 docker-compose.yml 中取消注释：
```yaml
volumes:
  - ./logs:/app/logs
```

### 3. 使用外部网络

如果需要与其他服务通信，可以配置网络：
```yaml
networks:
  - proxy-network

networks:
  proxy-network:
    external: true
```

### 4. 配置重启策略

```yaml
restart: always  # 或 unless-stopped
```

### 5. 限制资源使用

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

## 常见问题

### 1. 镜像构建失败

**问题**：构建过程中出现依赖安装失败

**解决方案**：
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 2. 容器无法启动

**问题**：容器启动后立即退出

**解决方案**：
查看日志排查问题：
```bash
docker logs message-proxy
```

常见原因：
- 环境变量未正确配置
- 端口被占用
- 依赖项版本不兼容

### 3. 无法访问服务

**问题**：无法访问 localhost:8000

**解决方案**：
```bash
# 检查端口映射
docker ps | grep message-proxy

# 检查防火墙设置

# 使用容器 IP 访问
docker inspect message-proxy | grep IPAddress
```

### 4. 日志输出过多

**问题**：DEBUG 级别日志过多

**解决方案**：
设置环境变量：
```bash
LOG_LEVEL=INFO
```

### 5. 镜像体积过大

**问题**：镜像体积超过预期

**解决方案**：
1. 使用多阶段构建（已配置）
2. 清理不必要的文件（已在 .dockerignore 中配置）
3. 使用 `docker system prune` 清理未使用的镜像

## Docker 命令速查

```bash
# 构建镜像
docker build -t message-proxy:latest .

# 运行容器
docker run -d -p 8000:8000 --name message-proxy message-proxy:latest

# 查看日志
docker logs -f message-proxy

# 进入容器
docker exec -it message-proxy /bin/bash

# 停止容器
docker stop message-proxy

# 启动容器
docker start message-proxy

# 重启容器
docker restart message-proxy

# 删除容器
docker rm -f message-proxy

# 删除镜像
docker rmi message-proxy:latest

# 查看镜像大小
docker images message-proxy

# 清理未使用的资源
docker system prune -a
```

## 技术架构

```
┌─────────────────────────────────────┐
│         Docker Host                 │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   message-proxy Container   │   │
│  │                             │   │
│  │  ┌─────────────────────┐    │   │
│  │  │  Python 3.12-slim   │    │   │
│  │  │                     │    │   │
│  │  │  ┌───────────────┐  │    │   │
│  │  │  │ FastAPI App   │  │    │   │
│  │  │  │ Port: 8000    │  │    │   │
│  │  │  └───────────────┘  │    │   │
│  │  │                     │    │   │
│  │  └─────────────────────┘    │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Port: 8000 ←→ Host: 8000          │
└─────────────────────────────────────┘
```

## 安全建议

1. ✅ 使用非 root 用户运行容器（已配置）
2. ✅ 定期更新基础镜像
3. ✅ 不要在镜像中硬编码敏感信息
4. ✅ 使用环境变量传递配置
5. ✅ 限制容器资源使用
6. ✅ 启用健康检查（已配置）
7. ⚠️ 生产环境建议使用 HTTPS
8. ⚠️ 配置适当的网络隔离

## 性能优化

1. 使用 `--no-cache` 构建可以确保使用最新依赖
2. 生产环境可以使用 `gunicorn` 替代 `uvicorn` 获得更好的性能
3. 考虑使用 Nginx 作为反向代理
4. 启用日志轮转避免磁盘占满

## 更新日志

- 初始版本：支持 Docker 多阶段构建和部署
- 支持环境变量配置
- 包含健康检查
- 使用非 root 用户运行

## 支持

如有问题，请查看项目文档或提交 Issue。
