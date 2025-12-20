# AI 协作指南 (AGENTS.md)

本指南旨在帮助 AI 助手（如 GitHub Copilot, Cursor 等）和人类开发者更好地理解项目结构并进行协作开发。

## 1. 项目架构原则

项目采用 **模块化 Flask 架构**，遵循以下分层原则：

- **路由层 (`app/routes/`)**: 仅处理 HTTP 请求、参数校验和响应分发。不应包含复杂的业务逻辑。
- **服务层 (`app/services/`)**: 核心业务逻辑所在地。例如 AI 调用逻辑、游戏数值计算等。
- **模型层 (`app/models.py`)**: 定义数据库结构。
- **工厂模式 (`app/__init__.py`)**: 负责应用初始化和 Blueprint 注册。

## 2. AI 协作规范

当要求 AI 修改代码时，请遵循以下指令：

### 2.1 增加新功能
1. **定义路由**: 在 `app/routes/` 下创建新的 Blueprint 文件。
2. **实现逻辑**: 在 `app/services/` 下创建对应的服务函数。
3. **注册模块**: 在 `app/__init__.py` 中注册新的 Blueprint。

### 2.2 修改 AI 行为
- 修改 `app/services/ai_service.py` 中的 `SYSTEM_PROMPT`。
- 保持“费曼”的人设：呆萌、好奇、示弱、引导。

### 2.3 数据库变更
- 在 `app/models.py` 中修改模型。
- 提醒开发者运行数据库迁移（如果引入了 Flask-Migrate）。

## 3. 待开发模块预留

AI 在协作时应注意以下预留接口：
- **语音模块**: 预留 `app/routes/voice.py`。
- **绘图模块**: 预留 `app/routes/draw.py`。
- **宠物互动**: 预留 `app/services/pet_service.py` 中的互动函数。

## 4. 常用命令

- **启动项目**: `python run.py`
- **安装依赖**: `uv add <package>`
- **查看日志**: 关注终端输出的 Flask Debug 信息。
