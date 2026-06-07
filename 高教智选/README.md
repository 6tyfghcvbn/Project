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
- [未来展望](#未来展望)

---

## 研究背景与意义

### 研究背景

随着互联网技术的飞速发展，在线教育已成为现代教育体系的重要组成部分。2020年以来，全球在线教育市场规模持续扩大，传统课堂教学与数字化学习的融合成为教育发展的重要趋势。然而，当前在线教育资源分散、优质课程获取门槛较高、学习者难以高效筛选符合自身需求的课程等问题依然突出。

国家大力推进教育数字化战略行动，明确提出要建设公平包容、开放共享、质量卓越的的数字教育生态。高等教育作为国家人才培养的主阵地，迫切需要通过数字化转型整合优质课程资源，提升教育质量和公平性。

### 研究意义

1. **资源整合价值**：通过爬虫技术自动采集国内顶尖高校的精品课程资源，打破信息孤岛，形成统一的课程资源库，解决资源分散、难以获取的问题。

2. **智能推荐价值**：引入AI智能助手，基于科大讯飞星火大模型技术，为用户提供个性化的课程推荐和学习路径建议，提升学习效率。

3. **数据洞察价值**：通过ECharts数据可视化技术，直观展示课程分布、选课趋势等关键数据，为教育管理者提供决策支持。

4. **用户体验价值**：采用现代化的前端技术栈（Vue3 + Element Plus），提供流畅、友好的交互体验，降低用户使用门槛。

---

## 项目概述

本项目是一个**高等教育智慧教育平台**，旨在整合全国优质高等教育资源，为学习者提供课程查询、数据分析、智能推荐等一站式服务。平台采用前后端分离架构，后端基于Python Flask框架，前端基于Vue3框架，数据库采用MySQL，AI能力接入科大讯飞星火大模型API。

### 核心目标

- 整合国内顶尖高校精品课程资源
- 提供高效的课程检索和筛选功能
- 利用AI技术实现智能化课程推荐
- 通过数据可视化展示教育发展趋势
- 保障用户数据安全和隐私保护

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
│                      数据访问层 (PyMySQL)                    │
├─────────────────────────────────────────────────────────────┤
│                    MySQL 数据库 │ 科大讯飞Spark API           │
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
| WebSockets | - | 实时AI通信 |

### 其他技术

| 技术 | 用途 |
|------|------|
| Selenium | 课程数据爬虫 |
| WebSocket | 与科大讯飞AI实时通信 |
| SHA256 | 密码加密 |
| HMAC-SHA256 | API签名认证 |

---

## 数据库设计

### 数据库：nocourse

#### 表1：users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| password | VARCHAR(255) | 密码（SHA256加密） |
| email | VARCHAR(100) | 邮箱，唯一 |
| created_at | TIMESTAMP | 创建时间 |

#### 表2：course（课程表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| title | VARCHAR(255) | 课程名称 |
| school | VARCHAR(100) | 开设学校 |
| teacher | VARCHAR(100) | 主讲教师 |
| students | VARCHAR(50) | 选课人次 |
| category | VARCHAR(50) | 课程分类 |
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
  - 密码使用SHA256哈希加密存储
  - 唯一性校验：用户名和邮箱不能重复

**核心代码**：
```python
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    # 验证唯一性、加密密码、插入数据库
```

#### 2. 用户登录

**功能描述**：已注册用户输入用户名密码进行登录。

**实现方法**：
- **前端**：
  - 登录成功后保存用户信息到`localStorage`
  - 密码显示/隐藏切换（😎隐藏 / 🤪显示）
  - 表单验证和错误提示

- **后端**：
  - `POST /api/login` 接口
  - 密码比对使用SHA256哈希
  - 返回用户基本信息（id, username, email）

#### 3. 用户设置

**功能描述**：登录用户可以修改用户名、密码、邮箱。

**实现方法**：
- `PUT /api/user/username` - 修改用户名（检查唯一性）
- `PUT /api/user/password` - 修改密码（验证当前密码）
- `PUT /api/user/email` - 修改邮箱（检查唯一性和格式）

**前端实现**：
- 页面路径：`/settings`
- 点击侧边栏用户头像按钮跳转
- 表单验证和成功/失败提示

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

**核心代码**：
```python
@app.route('/api/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    keyword = request.args.get('keyword', '', type=str)
    # 分页查询 + 关键词过滤
```

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
- XPath定位页面元素
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
- 渐变色配置：`#6366f1` → `#8b5cf6`

#### 2. 课程来源分布

**实现方法**：
- 后端`GET /api/school_distribution`获取学校分布数据
- 前端ECharts饼图展示
- 学院分类统计：`GROUP BY school`

#### 3. 教师授课数量 Top 10

**实现方法**：
- 使用mock数据（模拟教师课程统计）
- ECharts柱状图展示

#### 4. 数据统计概览

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

**功能描述**：基于科大讯飞星火大模型，为用户提供智能课程推荐和问题解答。

**实现方法**：
- **后端**：
  - WebSocket连接科大讯飞Spark API
  - HMAC-SHA256签名认证
  - 异步通信处理

- **AI提示词工程**：
  - 系统提示词定义AI角色和职责
  - 课程数据库实时注入（每次对话前获取5门课程信息）
  - 回答格式规范：课程名称、链接、高校、教师、选课人次、授课范围

**核心代码**：
```python
async def spark_api_chat(message, chat_history=[]):
    ws_url = generate_auth_url()  # 生成签名URL
    async with websockets.connect(ws_url) as ws:
        # 构造消息，包含系统提示和课程数据
        enhanced_msg = [combined_system_prompt] + chat_history[-3:]
        await ws.send(json.dumps(request_data))
        # 接收AI响应
```

#### 2. 聊天记录持久化

**功能描述**：保存用户与AI的对话记录，支持跨页面会话恢复。

**实现方法**：
- 数据库`chat_history`表存储聊天记录
- 关联用户ID：`user_id`外键
- 页面加载时自动从数据库读取历史记录
- 支持清空聊天记录功能

**前端实现**：
```javascript
onMounted(() => {
  const userData = localStorage.getItem('currentUser')
  if (userData) {
    currentUser.value = JSON.parse(userData)
    loadChatHistory()  // 加载历史记录
  }
})
```

#### 3. 课程智能推荐

**功能描述**：AI根据用户需求推荐数据库中的课程。

**实现方法**：
- 系统提示词要求AI优先从课程数据库查找
- 回答格式规范，包含课程链接方便跳转
- 授课范围由AI根据课程名称自动生成（不依赖数据库）

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
| POST | /api/chat | 发送消息 | message, username |
| GET | /api/chat_history | 获取聊天记录 | username |
| POST | /api/clear_chat | 清空聊天记录 | username |

---

## 项目结构

```
d:\mysql\daima\2/
├── src/                          # 前端源代码
│   ├── components/               # Vue组件
│   │   ├── ChatAssistant.vue     # 智能助手组件
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
├── ai/                           # AI模块（独立版本）
│   ├── index.html
│   └── webai.py                  # AI对话后端
├── app.py                        # Flask后端主应用
├── spider.py                     # 课程数据爬虫
├── requirements.txt              # Python依赖
├── package.json                  # Node依赖
├── vite.config.js                # Vite配置
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

### 数据库配置

```python
# app.py中的数据库配置
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='xhq',
    database='nocourse',
    charset='utf8mb4',
    port=3306
)
```

### AI服务配置

```python
# 科大讯飞Spark API配置
APP_ID = ""
API_KEY = ""
API_SECRET = ""
SPARK_URL = ""
```

---

## 未来展望

### 短期优化

1. **性能优化**：引入Vue虚拟滚动，优化大列表渲染性能
2. **缓存策略**：Redis缓存热门课程数据，减轻数据库压力
3. **错误处理**：完善全局错误处理和用户提示

### 中期扩展

1. **个性化推荐**：基于用户学习历史，实现协同过滤推荐算法
2. **学习笔记**：支持用户在课程页面添加笔记和收藏
3. **社交功能**：用户之间可以分享课程推荐和学习心得

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
- [科大讯飞开放平台](https://www.xfyun.cn/) - 智能语音和AI技术

---

*最后更新：2026年5月*
