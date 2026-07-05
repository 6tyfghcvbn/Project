from flask import Flask, request, jsonify, Response
import json
import pymysql
from flask_cors import CORS
import hashlib
import os
import time
import jieba
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

courses_cache = {}
COURSES_CACHE_TTL = 300

vector_index_timestamp = 0

SPARK_API_PASSWORD = os.getenv("SPARK_API_PASSWORD")
SPARK_BASE_URL = os.getenv("SPARK_BASE_URL", "https://spark-api-open.xf-yun.com/v1")

LLM_MODEL = os.getenv("LLM_MODEL", "lite")

if not SPARK_API_PASSWORD:
    raise ValueError("SPARK_API_PASSWORD is not set in .env file")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "3072"))

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "nocourse")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

MEMORY_WINDOW_SIZE = int(os.getenv("MEMORY_WINDOW_SIZE", "10"))
MEMORY_ENABLE_SUMMARY = os.getenv("MEMORY_ENABLE_SUMMARY", "true").lower() == "true"
MEMORY_TTL = int(os.getenv("MEMORY_TTL", "3600"))

llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=SPARK_API_PASSWORD,
    base_url=SPARK_BASE_URL,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
    timeout=30
)

chat_histories = {}

def trim_messages_by_window(messages, window_size=10):
    if len(messages) <= 1:
        return messages, []
    
    system_msg = messages[0] if isinstance(messages[0], SystemMessage) else None
    conversation = messages[1:] if system_msg else messages
    
    max_pairs = window_size
    pairs_needed = max_pairs * 2
    early_messages = []
    recent_messages = []
    
    if len(conversation) > pairs_needed:
        early_messages = conversation[:-pairs_needed]
        recent_messages = conversation[-pairs_needed:]
    else:
        recent_messages = conversation
    
    if system_msg:
        result = [system_msg] + recent_messages
    else:
        result = recent_messages
    
    return result, early_messages

def summarize_early_conversations(early_messages):
    if not early_messages or not MEMORY_ENABLE_SUMMARY:
        return ""
    
    summary_prompt = """请将以下对话历史总结成一段简短的摘要，突出关键信息和用户需求：

对话历史：
"""
    
    for msg in early_messages:
        role = "用户" if isinstance(msg, HumanMessage) else "助手"
        summary_prompt += f"{role}: {msg.content}\n"
    
    summary_prompt += "\n摘要："
    
    try:
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content.strip()
    except Exception:
        return ""

def get_session_with_memory_management(session_id):
    now = time.time()
    
    expired_sessions = []
    for sid, data in chat_histories.items():
        if isinstance(data, dict) and 'timestamp' in data:
            if now - data['timestamp'] > MEMORY_TTL:
                expired_sessions.append(sid)
    
    for sid in expired_sessions:
        del chat_histories[sid]
    
    if session_id not in chat_histories:
        system_prompt_text = get_system_prompt_with_courses()['content']
        chat_histories[session_id] = {
            'messages': [SystemMessage(content=system_prompt_text)],
            'timestamp': now
        }
    else:
        if isinstance(chat_histories[session_id], dict):
            chat_histories[session_id]['timestamp'] = now
        else:
            chat_histories[session_id] = {
                'messages': chat_histories[session_id],
                'timestamp': now
            }
    
    return chat_histories[session_id]['messages']

def save_session_message(session_id, message):
    if session_id not in chat_histories:
        return
    
    if isinstance(chat_histories[session_id], dict):
        chat_histories[session_id]['messages'].append(message)
        chat_histories[session_id]['timestamp'] = time.time()
    else:
        chat_histories[session_id].append(message)

def get_system_prompt_with_courses():
    base_content = """你是"高等教育智慧教育平台"的智能助手，核心使命是"让优质教育触手可及"。

平台介绍：
- 整合全国优质教育资源，推动高等教育数字化转型
- 汇聚清华大学、北京大学、复旦大学等国内顶尖高校的精品课程
- 覆盖理学、工学、文学、管理学等多学科领域

核心职责：
1. 资源推荐：为用户推荐符合需求的精品课程，优先提及国内顶尖高校资源
2. 平台指引：解答平台功能、使用流程、数字化转型政策等方面疑问
3. 教育支持：为师生提供学习路径建议，提升教育质量和公平性

服务原则：
- 专业权威：保持教育部官方平台的严谨性，确保信息准确可靠
- 亲切友好：以平等热情的态度服务师生，让学习者感受温暖与支持
- 简洁高效：直接切入需求，提供清晰解答，避免冗余信息

限制条件：
- 只提供平台官方发布的课程资源，不提供非平台资源
- 不涉及政治敏感、商业推广或与高等教育无关的话题
- 保护用户隐私，不询问或存储个人敏感信息

当你回答用户关于课程的问题时：
1. 优先从用户消息中提供的"参考课程信息"中查找相关信息
2. 介绍课程时，请按以下格式输出：
   - 课程名称：XXX
   - 课程链接：XXX
   - 开设高校：XXX
   - 主讲教师：XXX
   - 选课人次：XXX
   - 授课范围：（根据课程名称自动推断和生成，不依赖数据库）
3. 授课范围需要根据课程名称进行专业推断，包括该课程的主要内容、知识点、学习目标等
4. 如果课程名称相同或相似，请合并介绍或加以区分
5. 如果用户询问的课程不在参考课程信息中，明确告知用户并建议查看其他课程
6. 如果用户想要搜索特定课程，帮助用户了解参考课程信息中是否有匹配的课程"""

    return {
        "role": "system",
        "content": base_content
    }

def get_all_courses_data():
    now = time.time()
    if 'data' in courses_cache and 'timestamp' in courses_cache:
        if now - courses_cache['timestamp'] < COURSES_CACHE_TTL:
            return courses_cache['data']

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT * FROM course ORDER BY id ASC")
        courses = cursor.fetchall()
        courses_cache['data'] = courses
        courses_cache['timestamp'] = now
        return courses
    except Exception as e:
        return []
    finally:
        conn.close()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tfidf_vectorizer = None
tfidf_matrix = None
tfidf_courses = []

def build_vector_index():
    global tfidf_vectorizer, tfidf_matrix, tfidf_courses, vector_index_timestamp
    
    courses = get_all_courses_data()
    if not courses:
        return False
    
    try:
        texts = []
        for course in courses:
            title = course.get('title', '')
            school = course.get('school', '')
            teacher = course.get('teacher', '')
            texts.append(f"{title} {school} {teacher}")
        
        tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba.lcut)
        tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
        
        tfidf_courses = courses
        vector_index_timestamp = time.time()
        
        return True
    except Exception as e:
        return False

def search_courses_by_semantic(query, limit=10, threshold=0.1):
    global tfidf_vectorizer, tfidf_matrix, tfidf_courses, vector_index_timestamp
    
    if tfidf_vectorizer is None or tfidf_matrix is None or not tfidf_courses:
        return []
    
    now = time.time()
    if now - vector_index_timestamp > COURSES_CACHE_TTL:
        build_vector_index()
    
    try:
        query_vec = tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        indices = similarities.argsort()[::-1][:limit]
        
        results = []
        for idx in indices:
            if similarities[idx] >= threshold:
                results.append(tfidf_courses[idx])
        
        return results
    except Exception as e:
        return []

STOP_WORDS = {'有', '哪些', '什么', '课程', '相关', '的', '是', '在', '和', '与', '了', '我', '你', '他', '她', '它', '们', '能', '会', '可以', '吗', '呢', '啊', '吧', '哦', '呀', '要', '想', '需要', '推荐', '介绍', '告诉我', '请问', '谢谢', '您好'}

COURSE_RELATED_KEYWORDS = {'课程', '课', '学习', '教育', '选课', '上课', '开课', '授课', '课时', '课本', '教材', '教学', '老师', '教师', '教授', '学院', '大学', '高校', '专业', '学科', '课堂', '讲座', '培训', '教程', '讲义', '课件', '学分', '学位', '硕士', '博士', '本科', '研究生', '入学', '毕业', '考试', '考核', '作业', '论文', '研究', '实验', '实践', '实习', '实训', '公开课', '精品课', '选修课', '必修课', '通识课', '专业课', '学', '编程', '代码', '开发', '设计', '算法', '数据', '统计', '数学', '物理', '化学', '生物', '英语', '语文', '历史', '地理', '政治', '哲学', '经济', '管理', '计算机', '软件', '网络', '信息', '人工智能', '机器学习', '深度学习', '数据分析', '大数据', '云计算', '物联网', '编程入门', '入门教程'}

def is_course_related_query(query):
    for keyword in COURSE_RELATED_KEYWORDS:
        if keyword in query:
            return True
    return False

def search_courses_by_keyword(query, limit=10):
    semantic_results = search_courses_by_semantic(query, limit)
    if semantic_results:
        return semantic_results
    
    keywords = [k for k in jieba.lcut(query) if k not in STOP_WORDS and len(k) > 1]
    if not keywords:
        return []

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        like_patterns = ' OR '.join([f"title LIKE %s OR school LIKE %s OR teacher LIKE %s" for _ in keywords])
        params = []
        for keyword in keywords:
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])

        cursor.execute(f"""
            SELECT * FROM course 
            WHERE {like_patterns}
            ORDER BY id ASC
        """, params)

        courses = cursor.fetchall()

        scored_courses = []
        for course in courses:
            title = course.get('title', '')
            school = course.get('school', '')
            teacher = course.get('teacher', '')
            
            score = 0
            for keyword in keywords:
                if keyword in title:
                    score += 3
                if keyword in school:
                    score += 2
                if keyword in teacher:
                    score += 1
            
            scored_courses.append((score, course))

        scored_courses.sort(key=lambda x: x[0], reverse=True)
        return [course for _, course in scored_courses[:limit]]
    except Exception as e:
        return []
    finally:
        conn.close()

def format_courses_for_ai(courses):
    if not courses:
        return "数据库中暂无课程信息"

    course_list = []
    course_list.append(f"以下是平台数据库中的相关课程信息（共 {len(courses)} 门）：\n")

    for i, course in enumerate(courses, 1):
        title = course.get('title', '未知')
        school = course.get('school', '未知')
        teacher = course.get('teacher', '未知')
        students = course.get('students', '未知')
        url = course.get('link', '#')

        course_info = f"""{i}. 课程名称：{title}
   课程链接：{url}
   开设高校：{school}
   主讲教师：{teacher}
   选课人次：{students}"""
        course_list.append(course_info)

    return "\n\n".join(course_list)

def llm_chat(message, session_id="default", retry_count=3):
    last_error = None

    for attempt in range(retry_count):
        try:
            session_messages = get_session_with_memory_management(session_id)

            if is_course_related_query(message):
                relevant_courses = search_courses_by_keyword(message, limit=5)
                rag_context = format_courses_for_ai(relevant_courses)
                user_message_with_context = f"""{message}

参考课程信息：
{rag_context}"""
            else:
                user_message_with_context = message
            
            messages = session_messages.copy()
            messages.append(HumanMessage(content=user_message_with_context))

            messages, early_messages = trim_messages_by_window(messages, MEMORY_WINDOW_SIZE)
            
            if early_messages:
                summary = summarize_early_conversations(early_messages)
                if summary and isinstance(messages[0], SystemMessage):
                    messages.insert(1, SystemMessage(content=f"之前的对话摘要：{summary}"))

            response = llm.invoke(messages)

            if response and response.content:
                save_session_message(session_id, HumanMessage(content=message))
                save_session_message(session_id, AIMessage(content=response.content))
                return {"success": True, "response": response.content}
            else:
                last_error = "API 返回空响应"
                continue

        except Exception as e:
            last_error = f"处理出错: {str(e)}"
            if session_id in chat_histories:
                del chat_histories[session_id]

    return {"success": False, "error": last_error}

def llm_chat_stream(message, session_id="default"):
    try:
        session_messages = get_session_with_memory_management(session_id)

        if is_course_related_query(message):
            relevant_courses = search_courses_by_keyword(message, limit=5)
            rag_context = format_courses_for_ai(relevant_courses)
            user_message_with_context = f"""{message}

参考课程信息：
{rag_context}"""
        else:
            user_message_with_context = message
        
        messages = session_messages.copy()
        messages.append(HumanMessage(content=user_message_with_context))

        messages, early_messages = trim_messages_by_window(messages, MEMORY_WINDOW_SIZE)
        
        if early_messages:
            summary = summarize_early_conversations(early_messages)
            if summary and isinstance(messages[0], SystemMessage):
                messages.insert(1, SystemMessage(content=f"之前的对话摘要：{summary}"))

        full_response = ""
        
        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        if full_response:
            save_session_message(session_id, HumanMessage(content=message))
            save_session_message(session_id, AIMessage(content=full_response))

    except Exception as e:
        error_msg = f"流式处理出错: {str(e)}"
        yield f"[ERROR]{error_msg}"
        if session_id in chat_histories:
            del chat_histories[session_id]

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        username = data.get('username', '')

        if not message.strip():
            return jsonify({"success": False, "error": "请输入有效的消息"}), 400

        session_id = username if username and username != 'anonymous' else "default"
        user_id = get_user_id_by_username(username) if username and username != 'anonymous' else None

        if user_id:
            save_chat_message(user_id, 'user', message)

        response = llm_chat(message, session_id)

        if response.get('success') and user_id:
            save_chat_message(user_id, 'assistant', response['response'])

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    try:
        data = request.get_json()
        message = data.get('message', '')
        username = data.get('username', '')

        if not message.strip():
            return jsonify({"success": False, "error": "请输入有效的消息"}), 400

        session_id = username if username and username != 'anonymous' else "default"
        user_id = get_user_id_by_username(username) if username and username != 'anonymous' else None

        if user_id:
            save_chat_message(user_id, 'user', message)

        def generate():
            full_response = ""
            for chunk in llm_chat_stream(message, session_id):
                if chunk.startswith("[ERROR]"):
                    event_data = json.dumps({
                        "type": "error",
                        "content": chunk[7:]
                    }, ensure_ascii=False)
                    yield f"data: {event_data}\n\n"
                else:
                    full_response += chunk
                    event_data = json.dumps({
                        "type": "message",
                        "content": chunk
                    }, ensure_ascii=False)
                    yield f"data: {event_data}\n\n"
            
            if user_id and full_response:
                save_chat_message(user_id, 'assistant', full_response)

            finish_data = json.dumps({
                "type": "finish",
                "content": full_response
            }, ensure_ascii=False)
            yield f"data: {finish_data}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    username = request.args.get('username', '')

    if not username:
        return jsonify({"success": False, "error": "缺少用户名参数"}), 400

    user_id = get_user_id_by_username(username)
    if not user_id:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    history = get_user_chat_history(user_id)
    return jsonify({"success": True, "history": history})

@app.route('/api/clear_chat', methods=['POST'])
def clear_chat_history():
    data = request.get_json()
    username = data.get('username', '')

    if not username:
        return jsonify({"success": False, "error": "缺少用户名参数"}), 400

    user_id = get_user_id_by_username(username)
    if not user_id:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    clear_user_chat_history(user_id)
    return jsonify({"success": True, "message": "对话历史已清空"})

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        port=DB_PORT
    )

def convert_students_to_number(students_str):
    if not students_str:
        return 0
    s = students_str.replace('+', '').strip()
    if '亿' in s:
        try:
            return float(s.replace('亿', '')) * 10000
        except ValueError:
            return 0
    elif '万' in s:
        try:
            return float(s.replace('万', ''))
        except ValueError:
            return 0
    else:
        try:
            return float(s) / 10000
        except ValueError:
            return 0

@app.route('/api/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    keyword = request.args.get('keyword', '', type=str)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        offset = (page - 1) * size
        if keyword:
            cursor.execute("""
                SELECT COUNT(*) as total FROM course
                WHERE title LIKE %s OR school LIKE %s OR teacher LIKE %s
            """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0

            cursor.execute("""
                SELECT * FROM course
                WHERE title LIKE %s OR school LIKE %s OR teacher LIKE %s
                ORDER BY id ASC
                LIMIT %s OFFSET %s
            """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', size, offset))
        else:
            cursor.execute("SELECT COUNT(*) as total FROM course")
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0

            cursor.execute("SELECT * FROM course ORDER BY id ASC LIMIT %s OFFSET %s", (size, offset))

        courses = cursor.fetchall()
    finally:
        conn.close()

    courses.sort(key=lambda x: convert_students_to_number(x.get('students', '')), reverse=True)

    return jsonify({
        'data': courses,
        'total': total,
        'page': page,
        'size': size
    })

@app.route('/api/courses/<int:id>', methods=['GET'])
def get_course(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM course WHERE id = %s", (id,))
        course = cursor.fetchone()
    finally:
        conn.close()

    if course:
        return jsonify(course)
    else:
        return jsonify({'error': 'Course not found'}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) as total FROM course")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(DISTINCT school) as schools FROM course")
        schools = cursor.fetchone()['schools']

        cursor.execute("SELECT COUNT(DISTINCT teacher) as teachers FROM course")
        teachers = cursor.fetchone()['teachers']

        cursor.execute("SELECT SUM(students) as total_students FROM course")
        total_students = cursor.fetchone()['total_students']
    finally:
        conn.close()

    return jsonify({
        'total': total,
        'schools': schools,
        'teachers': teachers,
        'total_students': total_students or 0
    })

@app.route('/api/top_courses', methods=['GET'])
def get_top_courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT title, students FROM course ORDER BY students DESC LIMIT 10")
        courses = cursor.fetchall()
    finally:
        conn.close()

    return jsonify(courses)

@app.route('/api/school_distribution', methods=['GET'])
def get_school_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT school, COUNT(*) as count
            FROM course
            GROUP BY school
            ORDER BY count DESC
            LIMIT 10
        """)
        schools = cursor.fetchall()
    finally:
        conn.close()

    return jsonify(schools)

def init_user_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            avatar VARCHAR(10) DEFAULT '👶',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("SHOW COLUMNS FROM users LIKE 'avatar';")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(10) DEFAULT '👶';")

    conn.commit()
    conn.close()

def init_chat_history_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()
    conn.close()

def get_user_id_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    conn.close()

    return result['id'] if result else None

def save_chat_message(user_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (user_id, role, content)
        VALUES (%s, %s, %s)
    """, (user_id, role, content))

    conn.commit()
    conn.close()

def get_user_chat_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, created_at FROM chat_history
        WHERE user_id = %s
        ORDER BY created_at ASC
    """, (user_id,))

    history = cursor.fetchall()
    conn.close()

    return history

def clear_user_chat_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))

    conn.commit()
    conn.close()

import random
import string

def generate_salt(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hash_password(password, salt=None):
    if salt is None:
        salt = generate_salt()
    salted_password = f"{salt}{password}"
    return f"{salt}${hashlib.sha256(salted_password.encode('utf-8')).hexdigest()}"

def verify_password(password, hashed_password):
    if '$' in hashed_password:
        salt, hash_value = hashed_password.split('$', 1)
        return hash_password(password, salt) == hashed_password
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed_password

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': '请填写完整信息'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'error': '用户名已存在'}), 400

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': '邮箱已被注册'}), 400

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users (username, password, email)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, email))

        conn.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '请填写用户名和密码'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401

        if not verify_password(password, user['password']):
            return jsonify({'error': '用户名或密码错误'}), 401

        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'avatar': user.get('avatar', '👶')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/user/username', methods=['PUT'])
def update_username():
    data = request.get_json()
    user_id = data.get('userId')
    new_username = data.get('newUsername')

    if not user_id or not new_username:
        return jsonify({'success': False, 'error': '参数不完整'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        cursor.execute("SELECT * FROM users WHERE username = %s AND id != %s", (new_username, user_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': '用户名已存在'}), 400

        cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': '用户名修改成功'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/user/password', methods=['PUT'])
def update_password():
    data = request.get_json()
    user_id = data.get('userId')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not user_id or not current_password or not new_password:
        return jsonify({'success': False, 'error': '参数不完整'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        if not verify_password(current_password, user['password']):
            return jsonify({'success': False, 'error': '当前密码错误'}), 400

        hashed_new_password = hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': '密码修改成功'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/user/email', methods=['PUT'])
def update_email():
    data = request.get_json()
    user_id = data.get('userId')
    new_email = data.get('newEmail')

    if not user_id or not new_email:
        return jsonify({'success': False, 'error': '参数不完整'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        cursor.execute("SELECT * FROM users WHERE email = %s AND id != %s", (new_email, user_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': '邮箱已被使用'}), 400

        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': '邮箱修改成功'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/user/avatar', methods=['PUT'])
def update_avatar():
    data = request.get_json()
    user_id = data.get('userId')
    avatar = data.get('avatar')

    if not user_id or not avatar:
        return jsonify({'success': False, 'error': '参数不完整'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        cursor.execute("UPDATE users SET avatar = %s WHERE id = %s", (avatar, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': '头像修改成功'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_user_table()
    init_chat_history_table()
    
    print("正在构建课程向量索引...")
    if build_vector_index():
        print(f"向量索引构建成功，共索引 {len(tfidf_courses)} 门课程")
    else:
        print("向量索引构建失败，将使用关键词检索作为备选")
    
    app.run(host='0.0.0.0', port=8080, debug=False)