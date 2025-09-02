# Docker 部署指南

本项目支持使用 Docker 进行容器化部署，支持多种数据库配置（SQLite、Supabase、MySQL）。

## 快速开始

### 1. 环境配置

复制环境配置文件：
```bash
cp .env.docker .env
```

编辑 `.env` 文件，根据需要配置数据库类型和相关参数。

### 2. 数据库配置选项

#### 选项 A: 使用 SQLite（默认，适合开发和小型部署）
```bash
# .env 文件中设置
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URI=sqlite:///app.db
```

启动服务：
```bash
docker-compose --profile backend --profile frontend up -d
```

#### 选项 B: 使用 Supabase（推荐用于生产环境）
```bash
# .env 文件中设置
DATABASE_TYPE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

启动服务：
```bash
docker-compose --profile backend --profile frontend up -d
```

#### 选项 C: 使用 MySQL（传统关系型数据库）
```bash
# .env 文件中设置
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://agile_user:agile_password@mysql:3306/agile_srs
```

启动所有服务（包括 MySQL）：
```bash
docker-compose --profile mysql --profile backend --profile frontend up -d
```

### 3. 服务访问

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:5000
- **Redis**: localhost:6379
- **MySQL**（如果启用）: localhost:3306

## 服务管理

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

## 数据持久化

- **MySQL 数据**: 存储在 `mysql_data` 数据卷中
- **Redis 数据**: 存储在 `redis_data` 数据卷中
- **后端上传文件**: 存储在 `backend_uploads` 数据卷中
- **SQLite 数据库**: 存储在后端容器的 `/app` 目录中

## 开发模式

在开发模式下，源代码会挂载到容器中，支持热重载：

```bash
# 启动开发环境
docker-compose --profile backend --profile frontend up
```

## 生产部署建议

1. **使用 Supabase**: 提供托管的 PostgreSQL 数据库，具有自动备份、扩展性和高可用性
2. **配置环境变量**: 确保所有敏感信息（API 密钥、数据库凭据）通过环境变量配置
3. **使用 HTTPS**: 在生产环境中配置 SSL/TLS 证书
4. **监控和日志**: 配置适当的监控和日志收集

## 故障排除

### 数据库连接问题
1. 检查 `.env` 文件中的数据库配置
2. 确保数据库服务正在运行
3. 查看后端服务日志：`docker-compose logs backend`

### 端口冲突
如果端口被占用，可以在 `docker-compose.yml` 中修改端口映射：
```yaml
ports:
  - "8080:3000"  # 将前端映射到 8080 端口
  - "8000:5000"  # 将后端映射到 8000 端口
```

### 权限问题
在 Linux/macOS 上，可能需要调整文件权限：
```bash
sudo chown -R $USER:$USER .
```