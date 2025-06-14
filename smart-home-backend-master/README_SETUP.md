# 智能家居系统 - 设置指南

## 项目概述

这是一个基于Django REST Framework的智能家居后端系统，支持用户认证、设备管理、场景控制等功能。

## 功能特性

- 🔐 **JWT用户认证** - 安全的用户登录和注册系统
- 👤 **用户管理** - 多角色用户系统（管理员/普通成员/访客）
- 🏠 **设备管理** - 支持多种设备类型（灯光、空调、插座等）
- 🏘️ **房间管理** - 设备按房间分类管理
- 🎭 **场景控制** - 一键激活预设场景
- 📱 **RESTful API** - 完整的API接口
- 🔒 **权限控制** - 基于角色的细粒度权限管理

## 安装步骤

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd smart-home-backend-master
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

### 6. 运行开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://localhost:8000` 启动

## API文档

### 基础URL

- API基础地址: `http://localhost:8000/api/`
- 管理后台: `http://localhost:8000/admin/`

### 主要接口

#### 用户认证

- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户注销
- `POST /api/auth/token/refresh/` - 刷新令牌

#### 用户资料

- `GET /api/auth/profile/` - 获取用户资料
- `PUT /api/auth/profile/` - 更新用户资料
- `POST /api/auth/change-password/` - 修改密码

#### 设备管理

- `GET /api/devices/` - 获取设备列表
- `POST /api/devices/` - 创建设备
- `GET /api/devices/{id}/` - 获取设备详情
- `PUT /api/devices/{id}/` - 更新设备
- `DELETE /api/devices/{id}/` - 删除设备

#### 房间管理

- `GET /api/rooms/` - 获取房间列表
- `POST /api/rooms/` - 创建房间
- `PUT /api/rooms/{id}/` - 更新房间
- `DELETE /api/rooms/{id}/` - 删除房间

#### 场景管理

- `GET /api/scenes/` - 获取场景列表
- `POST /api/scenes/` - 创建场景
- `POST /api/scenes/{id}/activate/` - 激活场景

## 认证说明

### JWT令牌使用

1. 用户登录后获得访问令牌和刷新令牌
2. 在请求头中添加：`Authorization: Bearer <access_token>`
3. 令牌过期时使用刷新令牌获取新的访问令牌

### 示例请求

```javascript
// 登录
const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});

const data = await response.json();
const accessToken = data.tokens.access;

// 使用令牌访问API
const devicesResponse = await fetch('/api/devices/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
});
```

## 用户角色

### 管理员 (admin)

- 可以访问所有功能
- 可以管理所有用户和设备
- 可以创建和删除房间

### 普通成员 (member)

- 只能管理自己的设备
- 可以查看所有房间
- 可以创建和管理场景

### 访客 (guest)

- 只读权限
- 可以查看设备状态
- 可以激活场景

## 设备类型

系统支持以下设备类型：

- `light` - 灯光
- `ac` - 空调
- `outlet` - 插座
- `curtain` - 窗帘
- `tv` - 电视

## 测试

运行测试脚本：

```bash
python test_api.py
```

## 开发环境配置

### 环境变量

创建 `.env` 文件（可选）：

```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

### 数据库配置

默认使用SQLite数据库，如需使用其他数据库，请修改 `settings.py` 中的 `DATABASES` 配置。

### 媒体文件

用户上传的头像等文件存储在 `media/` 目录下。

## 部署

### 生产环境设置

1. 设置 `DEBUG = False`
2. 配置 `ALLOWED_HOSTS`
3. 使用生产级数据库（如PostgreSQL）
4. 配置静态文件服务
5. 设置HTTPS

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 故障排除

### 常见问题

1. **数据库迁移失败**

   ```bash
   python manage.py makemigrations --empty core
   python manage.py migrate
   ```
2. **JWT令牌问题**

   - 检查 `djangorestframework-simplejwt` 是否正确安装
   - 确认 `settings.py` 中的JWT配置
3. **CORS错误**

   - 检查 `django-cors-headers` 配置
   - 确认前端域名在 `CORS_ALLOWED_ORIGINS` 中
4. **媒体文件无法访问**

   - 确认 `MEDIA_URL` 和 `MEDIA_ROOT` 配置
   - 检查文件权限

### 日志查看

```bash
# 查看Django日志
tail -f logs/django.log

# 查看设备控制日志
tail -f logs/device_control.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱：your-email@example.com
- 项目地址：https://github.com/your-username/smart-home-backend

# 智能家居系统 - 前端数据接口说明

## 1. 用户注册/登录

### 注册（POST /api/auth/register/）

| 字段名   | 类型   | 必须 | 说明                                              |
| -------- | ------ | ---- | ------------------------------------------------- |
| username | string | 是   | 用户名                                            |
| password | string | 是   | 密码                                              |
| email    | string | 是   | 邮箱（唯一）                                      |
| role     | string | 否   | 用户角色，默认 member，可选值：admin/member/guest |
| phone    | string | 否   | 手机号，11位                                      |
| avatar   | file   | 否   | 头像                                              |
| nickname | string | 否   | 昵称                                              |
| bio      | string | 否   | 个人简介                                          |

示例：

## 2. 房间管理

### 创建房间（POST /api/rooms/）

| 字段名 | 类型   | 必须 | 说明     |
| ------ | ------ | ---- | -------- |
| name   | string | 是   | 房间名称 |

示例：

## 3. 设备管理

### 创建设备（POST /api/devices/）

| 字段名 | 类型   | 必须 | 说明                       |
| ------ | ------ | ---- | -------------------------- |
| name   | string | 是   | 设备名称                   |
| brand  | string | 否   | 品牌                       |
| type   | string | 是   | 设备类型（见下方说明）     |
| room   | int    | 是   | 房间ID（外键）             |
| status | bool   | 否   | 开关状态，默认 false       |
| extra  | dict   | 否   | 设备扩展属性（见下方说明） |
| owner  | int    | 否   | 用户ID（如需指定归属用户） |

**type 可选值**

- light
- ac
- outlet
- curtain
- tv

**extra 字段说明**

- light: `{"brightness": 80, "color": "#FFDD88"}`
- ac: `{"temperature": 25}`
- curtain: `{"openPercentage": 50}`
- 其他类型可为空 `{}`

示例：

## 4. 场景管理

### 创建场景（POST /api/scenes/）

| 字段名         | 类型         | 必须 | 说明                   |
| -------------- | ------------ | ---- | ---------------------- |
| name           | string       | 是   | 场景名称               |
| description    | string       | 是   | 场景描述               |
| device_configs | list[object] | 是   | 设备配置列表（见下表） |

**device_configs 每项说明**

| 字段名 | 类型 | 必须 | 说明                     |
| ------ | ---- | ---- | ------------------------ |
| device | int  | 是   | 设备ID                   |
| status | bool | 是   | 目标开关状态             |
| config | dict | 否   | 目标扩展属性（如亮度等） |

示例：

## 5. 设备/场景状态变更

- 修改设备状态：`PATCH /api/devices/{id}/`，如 `{"status": false}`
- 修改场景描述：`PATCH /api/scenes/{id}/`，如 `{"description": "新的描述"}`

## 6. 其它说明

- 所有ID字段均为后端返回的主键ID。
- 设备的 `extra` 字段和场景的 `config` 字段均为可选，按实际设备类型传递。
- 用户注册时 `email` 必须唯一，`role` 不传默认为 `member`。
- 设备的 `owner` 字段可选，通常由后端自动关联当前登录用户。

运行 `python manage.py createsuperuser` 后，Django 会启动一个交互式命令行流程，引导你创建一个超级用户（管理员账户）。具体流程如下：

1. 系统会依次提示你输入用户名、邮箱、密码（并要求确认密码）。
2. 如果你的 `User` 模型（如 `SmartHomeUser`）有额外的必填字段（如 email），也会要求你输入。
3. 系统会校验密码强度和邮箱唯一性等约束。
4. 创建成功后，这个超级用户可以用来登录 Django 管理后台（/admin/），拥有所有权限。
