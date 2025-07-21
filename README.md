# Data Agent

一个基于 LangGraph 和 Next.js 的智能数据分析代理系统，集成了强大的数据处理、可视化和交互式聊天界面。

## 🚀 功能特性

### 核心功能
- **智能数据分析**: 支持 SQL 查询、数据提取和 Python 代码执行
- **数据可视化**: 集成 matplotlib 和 seaborn，支持多种图片格式输出
- **文件处理**: 支持 Excel、CSV、JSON、XML、HTML 等多种文件格式读取
- **图片优化**: 支持 PNG、JPG、SVG、PDF、WebP 格式，自动压缩和优化
- **交互式界面**: 基于 Next.js 的现代化聊天界面

### 工具集
- **SQL 查询工具**: 支持 MySQL 数据库查询
- **数据提取工具**: 从数据库提取数据到 Python 环境
- **Python 代码执行**: 支持动态 Python 代码执行
- **图片生成工具**: 支持 matplotlib/seaborn 图表生成
- **文件读取工具**: 支持多种格式文件读取和预览
- **搜索工具**: 集成 Tavily 搜索功能

## 📋 系统要求

- Python 3.11+
- Node.js 18+
- pnpm 包管理器
- MySQL 数据库（可选）

## 🛠️ 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd data_agent
```

### 2. 安装 Python 依赖
```bash
# 使用 uv 包管理器（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd frontend
pnpm install
```

### 4. 环境配置
创建 `.env` 文件并配置以下环境变量：

```env
# LangGraph 配置
LANGGRAPH_API_URL=http://localhost:8123
LANGSMITH_API_KEY=your_langsmith_api_key

# 数据库配置（可选）
HOST=localhost
USER=your_username
MYSQL_PW=your_password
DB_NAME=your_database
PORT=3306

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key

# Tavily 搜索配置
TAVILY_API_KEY=your_tavily_api_key
```

## 🚀 启动服务

### 启动 LangGraph 后端

```bash
# 启动 LangGraph 服务
langgraph dev

# 或直接运行 Python 文件
python -m src.agents.graph
```

LangGraph 服务将在 `http://localhost:2024` 启动。

### 启动前端界面

```bash
cd frontend
pnpm dev
```

前端界面将在 `http://localhost:3000` 启动。

## 📁 项目结构

```
data_agent/
├── frontend/                 # Next.js 前端应用
│   ├── src/
│   │   ├── app/             # Next.js 应用路由
│   │   ├── components/      # React 组件
│   │   └── providers/       # 状态管理
│   └── package.json
├── src/
│   └── agents/
│       └── graph.py         # LangGraph 主图定义
├── tools/                   # 自定义工具
├── tests/                   # 测试文件
├── project_document/        # 项目文档
├── pyproject.toml          # Python 项目配置
├── langgraph.json          # LangGraph 配置
└── README.md
```

## 🔧 开发指南

### 添加新工具
1. 在 `src/agents/graph.py` 中定义新的工具函数
2. 使用 `@tool` 装饰器注册工具
3. 在 `graph` 函数中添加工具到工具列表

### 自定义前端
1. 修改 `frontend/src/components/` 中的组件
2. 更新 `frontend/src/app/page.tsx` 主页面
3. 调整 `frontend/src/app/api/[..._path]/route.ts` API 配置

## 📊 使用示例

### 数据分析
```
用户: 帮我分析一下销售数据
Agent: 我可以帮您分析销售数据。请提供数据文件或告诉我数据来源。
```

### 数据可视化
```
用户: 生成一个销售趋势图
Agent: 我将为您生成销售趋势图，请稍等...
```

### 文件处理
```
用户: 读取这个Excel文件
Agent: 正在读取文件，显示前5行数据预览...
```

## 🧪 测试

```bash
# 运行 Python 测试
python -m pytest tests/

# 运行前端测试
cd frontend
pnpm test
```

## 📝 项目文档

详细的项目文档请参考 `project_document/` 目录：
- `[001]增强文件读取和图片生成工具.md`: 工具增强实施计划
- `[001]添加文件读取和图片优化工具.md`: 工具添加记录

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 常见问题

### Q: LangGraph 服务启动失败
A: 检查环境变量配置，确保所有必需的 API 密钥已正确设置。

### Q: 前端无法连接到后端
A: 确保 LangGraph 服务正在运行，并检查 `LANGGRAPH_API_URL` 配置。

### Q: 数据库连接失败
A: 检查 MySQL 服务状态和数据库连接配置。

## 📞 支持

如有问题或建议，请提交 Issue 或联系开发团队。
