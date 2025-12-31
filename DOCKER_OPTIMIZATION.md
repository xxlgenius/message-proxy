# Docker镜像优化说明

## 优化内容

### 1. Dockerfile优化

#### 使用Alpine Linux
- **构建阶段使用Alpine**: 将构建阶段从python:3.12-slim改为python:3.12-alpine
- **运行阶段使用Alpine**: 将运行阶段从python:3.12-slim改为python:3.12-alpine
- **统一C库**: 确保构建和运行使用相同的C库(musl libc)，避免兼容性问题

#### 移除非root用户配置
- **简化镜像**: 移除非root用户创建和权限设置
- **减少层数**: 删除USER相关配置，减少镜像复杂度

#### 减少层数和镜像体积
- **合并RUN命令**: 将相关的清理操作合并到同一层，减少Docker镜像层数
- **添加PYTHONOPTIMIZE=2**: 启用Python优化级别2，移除docstring和断言，减少运行时体积
- **清理构建缓存**: 在构建阶段立即清理uv缓存和tmp目录
- **--no-cache选项**: 使用uv安装依赖时不缓存下载的包

#### 优化依赖安装
- **--no-editable**: 不使用可编辑模式安装，避免额外的符号链接
- **分离COPY操作**: 先复制依赖文件，再复制源代码，利用Docker层缓存机制

#### 激进清理
- **删除Python缓存**: 清理__pycache__目录和*.pyc/*.pyo文件
- **删除dist-info**: 移除虚拟环境中的*.dist-info目录
- **清理所有缓存**: 删除/root/.cache, /tmp/*, /var/tmp/*

#### 简化健康检查
- **使用socket模块**: 使用Python内置的socket模块替代httpx库
- **轻量级检查**: 减少健康检查的资源消耗

### 2. .dockerignore优化

添加了更多排除项，减少构建上下文大小：
- **IDE配置文件**: .project, .pydevproject, .settings/
- **环境变量文件**: .env, .env.* (排除实际环境变量，只保留.example)
- **构建产物**: dist/, build/, *.egg-info/, .eggs/, *.egg
- **CI/CD配置**: .github/, .gitlab-ci.yml, .travis.yml
- **文档和测试**: docs/, 以及更全面的测试文件排除

## 预期效果

### 镜像体积减少
- **构建阶段**: 通过清理缓存和优化安装，减少中间镜像体积
- **运行阶段**: 通过多阶段构建，只保留必要的运行时文件
- **总体积**: 预计可减少20-40%的最终镜像体积

### 构建速度提升
- **更好的层缓存**: 依赖文件与源代码分离，修改代码时无需重新安装依赖
- **减少上下文传输**: .dockerignore排除更多不必要文件

### 运行时优化
- **PYTHONOPTIMIZE=2**: Python代码执行更高效
- **更轻量的健康检查**: 减少健康检查的资源消耗

## 构建和测试

### 构建镜像
```bash
docker build -t message-proxy:optimized .
```

### 查看镜像大小
```bash
docker images message-proxy:optimized
```

### 与原镜像对比（如果有原镜像）
```bash
# 构建原镜像（git checkout原Dockerfile后）
docker build -t message-proxy:original .

# 对比大小
docker images | grep message-proxy
```

### 运行测试
```bash
docker run -d -p 8000:8000 --name message-proxy message-proxy:optimized

# 检查健康状态
docker ps

# 查看日志
docker logs message-proxy

# 测试API
curl http://localhost:8000/health

# 清理
docker stop message-proxy && docker rm message-proxy
```

## 进一步优化建议

如果需要更极致的优化，可以考虑：

1. **使用Alpine基础镜像**: 可以进一步减小体积，但可能存在兼容性问题
   ```dockerfile
   FROM python:3.12-alpine AS builder
   ```

2. **使用upx压缩Python可执行文件**: 进一步减少二进制文件大小

3. **启用Docker BuildKit**: 使用更高效的构建引擎
   ```bash
   DOCKER_BUILDKIT=1 docker build -t message-proxy:optimized .
   ```

4. **使用.dockerignore精确控制**: 只复制必要的源文件，而不是整个src目录

5. **多阶段构建进一步优化**: 在builder阶段只安装编译依赖，不在最终镜像中保留gcc
