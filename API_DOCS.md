# 费曼宠物 API 接口文档

本文档定义了费曼宠物项目的后端 API 接口，供前端开发和 AI 协作参考。

## 1. 认证模块 (Auth)

### 1.1 登录/注册
- **URL**: `/login`
- **方法**: `POST`
- **参数**:
  - `username` (string): 用户名
  - `password` (string): 密码
- **说明**: 简化逻辑，如果用户不存在则自动创建。成功后设置 `session['user_id']`。

### 1.2 退出登录
- **URL**: `/logout`
- **方法**: `GET`
- **说明**: 清除用户 Session。

## 2. 对话模块 (Chat)

### 2.1 流式对话接口
- **URL**: `/chat_stream`
- **方法**: `POST`
- **请求头**: `Content-Type: application/json`
- **请求体**:
  ```json
  {
    "message": "用户输入的解释内容"
  }
  ```
- **响应**: `text/event-stream` (SSE)
  - **数据格式**:
    - 过程中: `data: {"chunk": "文本片段"}`
    - 结束时: `data: {"level": 1, "experience": 20, "coins": 10, "done": true}`
- **说明**: 
  - 后端会自动处理上下文（最近10条消息）。
  - 结束后会自动保存对话并更新宠物状态。

## 3. 页面路由 (Main)

### 3.1 主页
- **URL**: `/`
- **方法**: `GET`
- **说明**: 渲染主聊天界面，包含历史消息和宠物状态。

## 4. 数据库模型参考 (SQLAlchemy)

### User (用户)
- `id`: Integer, PK
- `username`: String(80), Unique
- `password`: String(120)

### Pet (宠物)
- `id`: Integer, PK
- `user_id`: FK(User.id)
- `level`: Integer (默认 1)
- `experience`: Integer (默认 0)
- `coins`: Integer (默认 0)

### Message (消息)
- `id`: Integer, PK
- `pet_id`: FK(Pet.id)
- `role`: String ('user' 或 'assistant')
- `content`: Text
- `timestamp`: DateTime
