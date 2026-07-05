# 高等教育智慧教育平台

## 目录

- [研究背景与意义](#研究背景与意义)
- [项目概述](#项目概述)
- [功能架构](#功能架构)
- [技术栈](#技术栈)
- [数据库设计](#数据库设计)
- [功能模块详解](#功能模块详解)
  - [用户管理模块](#用户管理模块)
  - [课程管理模块](#课程管理模块)
  - [数据可视化模块](#数据可视化模块)
  - [智能助手模块](#智能助手模块)
- [接口文档](#接口文档)
- [项目结构](#项目结构)
- [安装部署](#安装部署)
- [环境配置](#环境配置)
- [未来展望](#未来展望)

---

## 研究背景与意义

### 研究背景

随着互联网技术的飞速发展，在线教育已成为现代教育体系的重要组成部分。2020年以来，全球在线教育市场规模持续扩大，传统课堂教学与数字化学习的融合成为教育发展的重要趋势。然而，当前在线教育资源分散、优质课程获取门槛较高、学习者难以高效筛选符合自身需求的课程等问题依然突出。

国家大力推进教育数字化战略行动，明确提出要建设公平包容、开放共享、质量卓越的数字教育生态。高等教育作为国家人才培养的主阵地，迫切需要通过数字化转型整合优质课程资源，提升教育质量和公平性。

### 研究意义

1. **资源整合价值**：通过爬虫技术自动采集国内顶尖高校的精品课程资源，打破信息孤岛，形成统一的课程资源库，解决资源分散、难以获取的问题。

2. **智能推荐价值**：引入AI智能助手，基于科大讯飞星火大模型技术，结合RAG（检索增强生成）技术，为用户提供精准的课程推荐和学习路径建议，提升学习效率。

3. **数据洞察价值**：通过ECharts数据可视化技术，直观展示课程分布、选课趋势等关键数据，为教育管理者提供决策支持。

4. **用户体验价值**：采用现代化的前端技术栈（Vue3 + Element Plus），提供流畅、友好的交互体验，降低用户使用门槛。

---

## 项目概述

本项目是一个**高等教育智慧教育平台**，旨在整合全国优质高等教育资源，为学习者提供课程查询、数据分析、智能推荐等一站式服务。平台采用前后端分离架构，后端基于Python Flask框架，前端基于Vue3框架，数据库采用MySQL，AI能力接入科大讯飞星火大模型API。

### 核心目标

- 整合国内顶尖高校精品课程资源
- 提供高效的课程检索和筛选功能（支持语义检索）
- 利用AI技术实现智能化课程推荐（RAG技术）
- 通过数据可视化展示教育发展趋势
- 保障用户数据安全和隐私保护
- 支持流式AI响应，提升交互体验

---

## 功能架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端展示层 (Vue3)                       │
├─────────────────────────────────────────────────────────────┤
│  首页 │ 课程列表 │ 课程详情 │ 数据可视化 │ 智能助手 │ 用户设置 │
├─────────────────────────────────────────────────────────────┤
│                      API网关层 (Vite Proxy)                 │
├─────────────────────────────────────────────────────────────┤
│                    后端服务层 (Flask)                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  用户管理API  │  课程管理API  │  数据统计API  │   AI对话API    │
├──────────────┴──────────────┴──────────────┴────────────────┤
│               RAG检索层 (TF-IDF + MySQL)                    │
├─────────────────────────────────────────────────────────────┤
│                    数据访问层 (PyMySQL)                     │
├─────────────────────────────────────────────────────────────┤
│                  MySQL 数据库 │ 科大讯飞Spark API            │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x | 渐进式JavaScript框架 |
| Vite | 5.x | 下一代前端构建工具 |
| Element Plus | 2.x | UI组件库 |
| ECharts | 5.x | 数据可视化图表库 |
| Vue Router | 4.x | 前端路由管理 |
| Axios | 1.x | HTTP请求库 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 后端开发语言 |
| Flask | 2.x | 轻量级Web框架 |
| PyMySQL | 1.x | MySQL数据库驱动 |
| Flask-CORS | 4.x | 跨域资源共享 |
| LangChain | 0.2.x | LLM应用框架 |
| scikit-learn | 1.8.x | TF-IDF向量检索 |
| jieba | 0.42.x | 中文分词 |

### AI技术

| 技术 | 用途 |
|------|------|
| 讯飞星火大模型 | AI对话引擎（Spark Lite） |
| RAG（检索增强生成） | 基于TF-IDF的课程语义检索 |
| SSE（Server-Sent Events） | 流式AI响应 |
| 滑动窗口记忆 | 对话上下文管理 |
| 对话摘要 | 早期对话内容压缩 |

### 其他技术

| 技术 | 用途 |
|------|------|
| Selenium | 课程数据爬虫 |
| SHA256 + Salt | 密码加密 |
| Bearer Token | API认证 |
| python-dotenv | 环境变量管理 |

---

## 数据库设计

### 数据库：nocourse

#### 表1：users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| password | VARCHAR(255) | 密码（SHA256+Salt加密） |
| email | VARCHAR(100) | 邮箱，唯一 |
| avatar | VARCHAR(10) | 用户头像（默认👶） |
| created_at | TIMESTAMP | 创建时间 |

#### 表2：course（课程表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| title | VARCHAR(255) | 课程名称 |
| school | VARCHAR(100) | 开设学校 |
| teacher | VARCHAR(100) | 主讲教师 |
| students | VARCHAR(50) | 选课人次 |
| link | VARCHAR(500) | 课程链接 |
| created_at | TIMESTAMP | 添加时间 |

#### 表3：chat_history（聊天记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 外键，关联users表 |
| role | VARCHAR(20) | 角色（user/assistant） |
| content | TEXT | 消息内容 |
| created_at | TIMESTAMP | 创建时间 |

---

## 功能模块详解

### 用户管理模块

#### 1. 用户注册

**功能描述**：新用户通过填写用户名、密码、邮箱进行注册。

**实现方法**：
- **前端**：Vue3组合式API + Element Plus表单验证
  - 使用`ref`管理表单数据
  - Element Plus的`el-form`和`el-form-item`组件
  - 自定义验证规则：用户名长度3-20字符，密码长度6-20字符，邮箱格式校验

- **后端**：Flask RESTful API
  - `POST /api/register` 接口
  - 密码使用SHA256+Salt哈希加密存储
  - 唯一性校验：用户名和邮箱不能重复

#### 2. 用户登录

**功能描述**：已注册用户输入用户名密码进行登录。

**实现方法**：
- **前端**：
  - 登录成功后保存用户信息到`localStorage`
  - 密码显示/隐藏切换
  - 表单验证和错误提示

- **后端**：
  - `POST /api/login` 接口
  - 密码比对使用SHA256+Salt哈希
  - 返回用户基本信息（id, username, email, avatar）

#### 3. 用户设置

**功能描述**：登录用户可以修改用户名、密码、邮箱、头像。

**实现方法**：
- `PUT /api/user/username` - 修改用户名（检查唯一性）
- `PUT /api/user/password` - 修改密码（验证当前密码）
- `PUT /api/user/email` - 修改邮箱（检查唯一性和格式）
- `PUT /api/user/avatar` - 修改头像

#### 4. 退出登录

**功能描述**：用户退出当前登录状态。

**实现方法**：
- 弹出确认对话框（Element Plus MessageBox）
- 清除`localStorage`中的用户信息
- 跳转到登录页面

---

### 课程管理模块

#### 1. 课程列表展示

**功能描述**：分页展示课程列表，支持关键词搜索。

**实现方法**：
- **前端**：
  - `GET /api/courses` 获取课程数据
  - 分页组件：`el-pagination`
  - 搜索组件：`el-input` + `@keyup.enter`
  - 表格展示：`el-table`

- **后端**：
  - `GET /api/courses` 接口
  - 参数：`page`, `size`, `keyword`
  - 支持按课程名称、学校、教师搜索
  - 按选课人次降序排列

#### 2. 课程详情查看

**功能描述**：查看单个课程的详细信息。

**实现方法**：
- 前端点击课程名称跳转详情页
- 后端`GET /api/courses/<id>`获取详情
- 前端`CourseDetail.vue`组件展示

#### 3. 课程数据爬取

**功能描述**：从外部网站自动爬取课程数据。

**实现方法**（spider.py）：
- 使用Selenium模拟浏览器
- CSS选择器定位页面元素
- 滚动加载更多课程
- 数据清洗和格式化
- 直接插入MySQL数据库

---

### 数据可视化模块

**功能描述**：通过ECharts图表展示课程数据统计分析结果。

#### 1. 选课人次排行 Top 10

**实现方法**：
- 后端`GET /api/top_courses`获取课程排行数据
- 前端ECharts柱状图展示

#### 2. 课程来源分布

**实现方法**：
- 后端`GET /api/school_distribution`获取学校分布数据
- 前端ECharts饼图展示

#### 3. 数据统计概览

**实现方法**：
- 后端`GET /api/statistics`获取统计数据
  - 课程总数
  - 学校数量
  - 教师数量
  - 总选课人次
- 前端卡片式布局展示

---

### 智能助手模块

#### 1. AI对话功能

**功能描述**：基于科大讯飞星火大模型，为用户提供智能课程推荐和问题解答，支持流式响应。

**实现方法**：
- **后端**：
  - HTTP API接入科大讯飞Spark API（替代WebSocket）
  - Bearer Token认证
  - SSE（Server-Sent Events）流式响应
  - `/api/chat/stream` 接口支持实时打字机效果

- **前端**：
  - 使用`fetch()`配合`ReadableStream`处理SSE流式数据
  - 实时更新消息内容，实现打字机效果

- **AI提示词工程**：
  - 系统提示词定义AI角色和职责
  - RAG检索实时注入课程信息
  - 回答格式规范：课程名称、链接、高校、教师、选课人次、授课范围

#### 2. RAG知识库检索

**功能描述**：基于TF-IDF语义检索，从数据库中获取相关课程信息注入AI对话。

**实现方法**：
- **检索流程**：
  1. 判断用户查询是否与课程相关
  2. 使用jieba分词处理查询
  3. TF-IDF向量化 + 余弦相似度计算
  4. 返回Top-K最相关课程
  5. 格式化为AI可读的上下文信息

- **检索策略**：
  - 优先使用语义检索（TF-IDF）
  - 语义检索无结果时降级为关键词检索（SQL LIKE）
  - 相似度阈值过滤（默认0.1）
  - 课程数据定时刷新（300秒TTL）

#### 3. 对话记忆管理

**功能描述**：支持多轮对话，自动管理上下文历史。

**实现方法**：
- **滑动窗口机制**：保留最近N轮对话（默认10轮）
- **对话摘要**：对早期对话生成摘要，注入系统提示
- **会话TTL**：长时间无活动自动清理会话（默认3600秒）
- **会话存储**：内存字典存储，支持多用户独立会话

#### 4. 聊天记录持久化

**功能描述**：保存用户与AI的对话记录，支持跨页面会话恢复。

**实现方法**：
- 数据库`chat_history`表存储聊天记录
- 关联用户ID：`user_id`外键
- 页面加载时自动从数据库读取历史记录
- 支持清空聊天记录功能

---

## 接口文档

### 用户相关接口

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| POST | /api/register | 用户注册 | username, password, email |
| POST | /api/login | 用户登录 | username, password |
| PUT | /api/user/username | 修改用户名 | userId, newUsername |
| PUT | /api/user/password | 修改密码 | userId, currentPassword, newPassword |
| PUT | /api/user/email | 修改邮箱 | userId, newEmail |
| PUT | /api/user/avatar | 修改头像 | userId, avatar |

### 课程相关接口

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | /api/courses | 获取课程列表 | page, size, keyword |
| GET | /api/courses/\<id\> | 获取课程详情 | - |

### 数据统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/statistics | 获取统计数据 |
| GET | /api/top_courses | 获取热门课程排行 |
| GET | /api/school_distribution | 获取学校分布数据 |

### AI对话接口

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| POST | /api/chat | 发送消息（非流式） | message, username |
| POST | /api/chat/stream | 发送消息（SSE流式） | message, username |
| GET | /api/chat_history | 获取聊天记录 | username |
| POST | /api/clear_chat | 清空聊天记录 | username |

---

## 项目结构

```
./
├── src/                          # 前端源代码
│   ├── components/               # Vue组件
│   │   ├── AvatarSettings.vue    # 头像设置组件
│   │   ├── ChatAssistant.vue     # 智能助手组件（支持SSE流式）
│   │   ├── CourseChart.vue       # 数据可视化组件
│   │   ├── CourseDetail.vue      # 课程详情组件
│   │   ├── CourseList.vue        # 课程列表组件
│   │   ├── HomePage.vue          # 首页组件
│   │   ├── LoginRegister.vue     # 登录注册组件
│   │   ├── MainLayout.vue        # 主布局组件
│   │   └── UserSettings.vue      # 用户设置组件
│   ├── router/
│   │   └── index.js              # 路由配置
│   ├── App.vue                   # 根组件
│   ├── main.js                   # 入口文件
│   └── style.css                 # 全局样式
├── app.py                        # Flask后端主应用
├── spider.py                     # 课程数据爬虫
├── requirements.txt              # Python依赖
├── package.json                  # Node依赖
├── vite.config.js                # Vite配置
├── .env                          # 环境变量配置
├── index.html                    # HTML模板
└── README.md                     # 项目文档
```

---

## 安装部署

### 环境要求

- Node.js 16+
- Python 3.8+
- MySQL 5.7+

### 前端部署

```bash
# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

### 后端部署

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动Flask服务
python app.py
```

---

## 环境配置

### .env文件配置

创建 `.env` 文件，配置以下参数：

```env
# 讯飞星火API配置
SPARK_API_PASSWORD=your_api_password
SPARK_BASE_URL=https://spark-api-open.xf-yun.com/v1
LLM_MODEL=lite

# LLM参数配置
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=3072

# 数据库配置
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=nocourse
DB_PORT=3306

# 对话记忆配置
MEMORY_WINDOW_SIZE=10
MEMORY_ENABLE_SUMMARY=true
MEMORY_TTL=3600
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| SPARK_API_PASSWORD | 讯飞星火API密码（格式：appid:apisecret） | - |
| SPARK_BASE_URL | 讯飞星火API基础地址 | https://spark-api-open.xf-yun.com/v1 |
| LLM_MODEL | 使用的模型 | lite |
| LLM_TEMPERATURE | 温度参数（0-1），越高越随机 | 0.3 |
| LLM_MAX_TOKENS | 最大响应token数 | 3072 |
| MEMORY_WINDOW_SIZE | 对话滑动窗口大小 | 10 |
| MEMORY_ENABLE_SUMMARY | 是否启用对话摘要 | true |
| MEMORY_TTL | 会话过期时间（秒） | 3600 |

### 配置步骤

#### 1. 配置讯飞星火API密钥

**文件**: `.env` 第1行  
**配置项**: `SPARK_API_PASSWORD`  
**当前内容**: `SPARK_API_PASSWORD=your_api_password`  
**需要更改为**: `SPARK_API_PASSWORD=你的appid:你的apisecret`  
**获取方式**:  
- 访问 [科大讯飞开放平台](https://www.xfyun.cn/)
- 注册并登录账号
- 创建应用，选择"星火大模型"服务
- 在应用管理中获取 `APPID` 和 `APISecret`
- 将两者拼接为 `APPID:APISecret` 格式填入

#### 2. 配置数据库密码

**文件**: `.env` 第6行  
**配置项**: `DB_PASSWORD`  
**当前内容**: `DB_PASSWORD=your_password`  
**需要更改为**: `DB_PASSWORD=你的MySQL密码`  
**获取方式**:  
- 使用本地MySQL数据库的root用户密码
- 确保MySQL服务已启动且可访问
- 数据库名称默认为 `nocourse`，可在第7行 `DB_DATABASE` 修改

#### 3. 数据库连接配置（可选）

**文件**: `.env` 第4-8行  
**配置项**: `DB_HOST`, `DB_USER`, `DB_PORT`  
**默认值**:  
- `DB_HOST=127.0.0.1`（本地数据库）
- `DB_USER=root`（MySQL默认管理员账号）
- `DB_PORT=3306`（MySQL默认端口）  
**修改场景**: 如果使用远程数据库或非默认端口，需要相应修改

#### 4. 爬虫脚本数据库配置

**文件**: `spider.py` 第14-18行  
**配置项**: 数据库连接参数  
**说明**: 爬虫脚本已配置为从 `.env` 文件读取数据库连接信息，无需单独修改。确保 `.env` 文件配置正确后，爬虫会自动使用相同的数据库连接。

### 启动前准备

#### 1. 创建MySQL数据库

在启动应用之前，需要先创建名为 `nocourse` 的数据库：

```sql
CREATE DATABASE IF NOT EXISTS nocourse DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**说明**: 应用启动时会自动创建 `users` 和 `chat_history` 表，但 `course` 表需要通过爬虫脚本创建和填充。

#### 2. 爬取课程数据

配置好数据库后，运行爬虫脚本获取课程数据：

```bash
python spider.py
```

**说明**: 
- 爬虫会自动创建 `course` 表并填充课程数据
- 需要安装 `selenium` 库（已包含在 `requirements.txt` 中）
- 需要安装 Chrome 浏览器和对应版本的 ChromeDriver

---

## 未来展望

### 短期优化

1. **性能优化**：引入Vue虚拟滚动，优化大列表渲染性能
2. **缓存策略**：Redis缓存热门课程数据，减轻数据库压力
3. **错误处理**：完善全局错误处理和用户提示
4. **API限流**：添加请求频率限制，防止滥用

### 中期扩展

1. **向量检索升级**：引入sentence-transformers预训练模型，实现更精准的语义检索
2. **个性化推荐**：基于用户学习历史，实现协同过滤推荐算法
3. **学习笔记**：支持用户在课程页面添加笔记和收藏
4. **社交功能**：用户之间可以分享课程推荐和学习心得

### 长期愿景

1. **多语言支持**：支持中英文切换，服务更广泛的学习者
2. **移动端适配**：开发移动端应用或响应式设计
3. **数据分析**：引入机器学习模型，预测学习趋势和课程热度
4. **开放API**：对外提供标准API，支持第三方应用接入

---

## 致谢

本项目在开发过程中参考了以下开源项目和文档：

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue3 UI组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库
- [Flask](https://flask.palletsprojects.com/) - Python轻量级Web框架
- [LangChain](https://python.langchain.com/) - LLM应用开发框架
- [scikit-learn](https://scikit-learn.org/) - 机器学习库
- [科大讯飞开放平台](https://www.xfyun.cn/) - 智能语音和AI技术

---

*最后更新：2026年7月*
