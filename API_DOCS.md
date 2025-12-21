# 费曼宠物 API 接口文档

本文档定义了费曼宠物项目的后端 API 接口及数据库结构。

## 1. 认证模块 (Auth)

### 1.1 登录/注册
- **URL**: `/login`
- **方法**: `POST`
- **参数**: `username`, `password`
- **说明**: 自动注册/登录逻辑。

## 2. 宠物管理 (Pet)

### 2.1 宠物列表
- **URL**: `/pet/`
- **方法**: `GET`
- **说明**: 返回用户拥有的所有宠物。

### 2.2 领养宠物
- **URL**: `/pet/create`
- **方法**: `POST`
- **参数**: `name` (宠物名称)

### 2.3 会话列表
- **URL**: `/pet/<pet_id>/sessions`
- **方法**: `GET`
- **说明**: 查看特定宠物的历史学习会话。

### 2.4 开启新会话
- **URL**: `/pet/<pet_id>/sessions/create`
- **方法**: `POST`
- **参数**: `title` (会话主题)

## 3. 对话模块 (Chat)

### 3.1 流式对话接口
- **URL**: `/chat_stream`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "message": "用户输入",
    "session_id": 1
  }
  ```
- **响应**: `text/event-stream`
- **说明**: 宠物会根据 `knowledge` 字段中的记忆进行回复，并在结束时自动提取新知识。

## 4. 商城模块 (Shop)

### 4.1 获取商品
- **URL**: `/shop/`
- **方法**: `GET`

### 4.2 购买皮肤
- **URL**: `/shop/buy/<skin_id>`
- **方法**: `POST`
- **说明**: 使用用户账户中的金币购买皮肤。购买后皮肤将进入用户的“已拥有”列表。

### 4.3 穿戴皮肤
- **URL**: `/shop/wear/<pet_id>/<skin_id>`
- **方法**: `POST`
- **说明**: 为指定宠物更换已拥有的皮肤。`skin_id` 为 0 时表示恢复默认皮肤。

---

# 数据库表格文档 (MySQL)

### 1. `user` (用户表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | INT (PK) | 用户唯一标识 |
| username | VARCHAR(80) | 用户名 (唯一) |
| password | VARCHAR(120) | 密码 |
| coins | INT | **金币** (初始 200，属于用户) |

### 2. `pet` (宠物表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | INT (PK) | 宠物唯一标识 |
| user_id | INT (FK) | 所属用户 ID |
| name | VARCHAR(50) | 宠物名称 |
| level | INT | 等级 (默认 1) |
| experience | INT | 经验值 |
| knowledge | TEXT | **核心字段**：存储学到的知识点 (跨会话共享) |
| current_skin_id | INT (FK) | 当前穿戴的皮肤 ID |

### 3. `session` (会话表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | INT (PK) | 会话唯一标识 |
| pet_id | INT (FK) | 所属宠物 ID |
| title | VARCHAR(100) | 会话主题 (如：学习勾股定理) |
| created_at | DATETIME | 创建时间 |

### 4. `message` (消息表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | INT (PK) | 消息唯一标识 |
| session_id | INT (FK) | 所属会话 ID |
| role | VARCHAR(10) | 角色 (user/assistant) |
| content | TEXT | 消息内容 |
| timestamp | DATETIME | 发送时间 |

### 5. `skin` (皮肤表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | INT (PK) | 皮肤唯一标识 |
| name | VARCHAR(50) | 皮肤名称 |
| price | INT | 售价 |
| description | VARCHAR(200) | 描述 |

### 6. `user_skin` (用户皮肤关联表)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id | INT (FK) | 用户 ID |
| skin_id | INT (FK) | 皮肤 ID |
| purchased_at | DATETIME | 购买时间 |

