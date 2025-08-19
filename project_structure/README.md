# 敏捷需求调研系统 (Agile SRS)

一个前后端分离的需求调研管理系统，支持多用户协作、需求收集与LLM辅助生成需求文档。

## 功能特性

- **用户管理**: 注册、登录、个人资料管理
- **需求任务管理**: 创建、编辑、删除需求调研任务
- **协作功能**: 邀请其他用户参与需求调研任务
- **多格式需求收集**: 支持文字、图片、语音等方式提交原始需求
- **LLM集成**: 自动生成完整的需求文档
- **文档管理**: 预览、确认和下载生成的需求文档
- **现代化前端**: 基于Vue 3的响应式界面
- **容器化部署**: 支持Docker一键部署

## 技术栈

### 后端
- Python 3.9
- Flask 2.3.2
- Flask-SQLAlchemy 3.0.5
- Flask-JWT-Extended 4.5.2
- MySQL 8.0
- Redis 7
- Gunicorn

### 前端
- Vue 3.3.4
- Vue Router 4.2.4
- Pinia 2.1.6
- Element Plus 2.3.8
- Axios 1.4.0
- Vite 4.4.9

### 部署
- Docker
- Docker Compose
- Nginx

## 快速开始

### 环境要求

- Docker
- Docker Compose

### 部署步骤

1. 克隆项目代码:
   ```bash
   git clone <repository-url>
   cd agile-srs
   ```

2. 配置环境变量:
   编辑 `deployment/docker-compose.yml` 文件，修改以下环境变量:
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_PASSWORD`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `LLM_API_KEY`

3. 启动服务:
   ```bash
   cd deployment
   docker-compose up -d
   ```

4. 访问应用:
   打开浏览器访问 `http://localhost`

### 开发环境

#### 后端开发

1. 进入后端目录:
   ```bash
   cd backend
   ```

2. 创建虚拟环境并激活:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

4. 配置数据库:
   确保MySQL服务运行，并创建数据库 `agile_srs_db`

5. 初始化数据库:
   运行数据库初始化脚本创建SQLite数据库并初始化默认admin用户:
   ```bash
   python init_db.py
   ```
   默认admin用户凭证:
   - 用户名: admin
   - 邮箱: admin@example.com
   - 密码: 123123

6. 运行应用:
   ```bash
   python run.py
   ```

#### 前端开发

1. 进入前端目录:
   ```bash
   cd frontend
   ```

2. 安装依赖:
   ```bash
   npm install
   ```

3. 启动开发服务器:
   ```bash
   npm run dev
   ```

4. 访问应用:
   打开浏览器访问 `http://localhost:3000`

## 项目结构

```
agile-srs/
├── backend/          # 后端代码
│   ├── app/          # 应用核心代码
│   │   ├── api/      # API接口
│   │   ├── models/   # 数据模型
│   │   └── utils/    # 工具类
│   ├── uploads/      # 上传文件目录
│   ├── run.py        # 应用入口
│   ├── requirements.txt # 依赖文件
│   └── Dockerfile    # 后端Docker配置
├── frontend/         # 前端代码
│   ├── src/          # 源代码
│   │   ├── assets/   # 静态资源
│   │   ├── components/ # 组件
│   │   ├── router/   # 路由配置
│   │   ├── store/    # 状态管理
│   │   ├── views/    # 页面视图
│   │   ├── App.vue   # 根组件
│   │   └── main.js   # 入口文件
│   ├── dist/         # 构建输出目录
│   ├── package.json  # 项目配置
│   ├── vite.config.js # 构建配置
│   ├── Dockerfile    # 前端Docker配置
│   └── nginx.conf    # Nginx配置
├── deployment/       # 部署配置
│   └── docker-compose.yml # Docker Compose配置
└── README.md         # 项目说明
```

## API文档

### 用户认证

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户资料

### 需求管理

- `POST /api/requirements` - 创建需求任务
- `GET /api/requirements` - 获取需求任务列表
- `GET /api/requirements/<id>` - 获取需求任务详情
- `PUT /api/requirements/<id>` - 更新需求任务
- `DELETE /api/requirements/<id>` - 删除需求任务
- `POST /api/requirements/<id>/invite` - 邀请用户参与需求任务
- `POST /api/requirements/<id>/content` - 提交需求内容
- `POST /api/requirements/<id>/generate-document` - 生成需求文档

## 数据库设计

### 用户表 (users)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | Integer | 用户ID |
| username | String(80) | 用户名 |
| email | String(120) | 邮箱 |
| password_hash | String(128) | 密码哈希 |
| created_at | DateTime | 创建时间 |

### 需求表 (requirements)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | Integer | 需求ID |
| title | String(200) | 需求标题 |
| description | Text | 需求描述 |
| creator_id | Integer | 创建者ID |
| status | String(50) | 需求状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 用户需求关联表 (user_requirements)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| user_id | Integer | 用户ID |
| requirement_id | Integer | 需求ID |
| role | String(50) | 用户在该需求中的角色 |

### 需求内容表 (requirement_contents)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | Integer | 内容ID |
| requirement_id | Integer | 需求ID |
| content_type | String(50) | 内容类型 (text/image/audio) |
| content | Text | 文本内容 |
| file_path | String(255) | 文件路径 |
| created_at | DateTime | 创建时间 |

## 许可证

[MIT License](LICENSE)