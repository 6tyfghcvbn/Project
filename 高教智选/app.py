from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
import hashlib
import websockets
import json
import base64
import hmac
from datetime import datetime, timezone
from urllib.parse import urlparse, urlencode
import asyncio

app = Flask(__name__)
CORS(app)

# AI 配置
APP_ID = ""
API_KEY = ""
API_SECRET = ""
SPARK_URL = ""

def get_system_prompt_with_courses(courses):
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
- 保护用户隐私，不询问或存储个人敏感信息"""

    courses_content = format_courses_for_ai(courses)
    full_content = f"""{base_content}

{courses_content}

当你回答用户关于课程的问题时：
1. 优先从上述课程数据库中查找相关信息
2. 介绍课程时，请按以下格式输出：
   - 课程名称：XXX
   - 课程链接：XXX
   - 开设高校：XXX
   - 主讲教师：XXX
   - 选课人次：XXX
   - 授课范围：（根据课程名称自动推断和生成，不依赖数据库）
3. 授课范围需要根据课程名称进行专业推断，包括该课程的主要内容、知识点、学习目标等
4. 如果课程名称相同或相似，请合并介绍或加以区分
5. 如果用户询问的课程不在数据库中，明确告知用户并建议查看其他课程
6. 如果用户想要搜索特定课程，帮助用户了解数据库中是否有匹配的课程"""

    return {
        "role": "system",
        "content": full_content
    }

host = urlparse(SPARK_URL).netloc
path = urlparse(SPARK_URL).path

def generate_auth_url():
    cur_time = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    signature_origin = f"host: {host}\ndate: {cur_time}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(API_SECRET.encode(), signature_origin.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization = base64.b64encode(
        f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'.encode()
    ).decode()
    return f"{SPARK_URL}?{urlencode({'authorization': authorization, 'date': cur_time, 'host': host})}"

def get_all_courses_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM course ORDER BY id ASC LIMIT 5")
        courses = cursor.fetchall()
        return courses
    except Exception as e:
        return []
    finally:
        conn.close()

def format_courses_for_ai(courses):
    if not courses:
        return "数据库中暂无课程信息"
    
    course_list = []
    course_list.append(f"以下是平台数据库中的部分课程信息（共 {len(courses)} 门）：\n")
    
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

async def spark_api_chat(message, chat_history=[], temperature=0.3, max_tokens=3072, retry_count=3):
    courses_data = get_all_courses_data()
    combined_system_prompt = get_system_prompt_with_courses(courses_data)
    
    last_error = None
    
    for attempt in range(retry_count):
        try:
            ws_url = generate_auth_url()
            
            async with websockets.connect(ws_url, open_timeout=10) as ws:
                # 不直接修改传入的chat_history，而是创建新的临时列表
                temp_history = chat_history.copy()
                temp_history.append({"role": "user", "content": message})
                enhanced_msg = [combined_system_prompt] + temp_history[-3:]
                
                request_data = {
                    "header": {"app_id": APP_ID, "uid": "higher_education_assistant"},
                    "parameter": {"chat": {"domain": "lite", "temperature": temperature, "max_tokens": max_tokens}},
                    "payload": {"message": {"text": enhanced_msg}}
                }
                
                await ws.send(json.dumps(request_data, ensure_ascii=False))
                
                full_response = ""
                async for resp in ws:
                    data = json.loads(resp)
                    
                    if data["header"]["code"] != 0:
                        raise Exception(f"API Error: {data['header']['message']}")
                    
                    texts = data["payload"]["choices"]["text"]
                    if texts and isinstance(texts, list):
                        for text_item in texts:
                            if "content" in text_item and text_item["content"].strip():
                                full_response += text_item["content"]
                    
                    if data["header"]["status"] == 2:
                        break
                
                if not full_response.strip():
                    last_error = "WebSocket 返回空响应"
                    continue
                
                return {"success": True, "response": full_response}
                
        except websockets.exceptions.ConnectionClosedError as e:
            last_error = f"WebSocket连接意外关闭: {str(e)}"
        except asyncio.TimeoutError:
            last_error = "WebSocket连接超时"
        except Exception as e:
            last_error = f"处理出错: {str(e)}"
        
        await asyncio.sleep(1)
    
    return {"success": False, "error": last_error}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        username = data.get('username', '')
        
        if not message.strip():
            return jsonify({"success": False, "error": "请输入有效的消息"}), 400
        
        # 获取用户ID，如果是匿名用户则为None
        user_id = get_user_id_by_username(username) if username and username != 'anonymous' else None
        
        # 如果用户已登录，保存用户消息到数据库
        if user_id:
            save_chat_message(user_id, 'user', message)
        
        # 获取用户的聊天历史用于AI上下文（仅登录用户）
        if user_id:
            user_history = get_user_chat_history(user_id)
            global_chat_history = [{"role": item['role'], "content": item['content']} for item in user_history]
        else:
            global_chat_history = []
        
        # 调用AI并传入历史记录
        response = asyncio.run(spark_api_chat(message, global_chat_history))
        
        if response.get('success') and user_id:
            # 保存AI响应到数据库（仅登录用户）
            save_chat_message(user_id, 'assistant', response['response'])
        
        return jsonify(response)
    
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
        host='127.0.0.1',
        user='root',
        password='xhq',
        database='nocourse',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        port=3306
    )

def convert_students_to_number(students_str):
    if not students_str:
        return 0
    s = students_str.replace('+', '').strip()
    if '亿' in s:
        try:
            return float(s.replace('亿', '')) * 10000
        except:
            return 0
    elif '万' in s:
        try:
            return float(s.replace('万', ''))
        except:
            return 0
    else:
        try:
            return float(s) / 10000
        except:
            return 0

@app.route('/api/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    keyword = request.args.get('keyword', '', type=str)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute("SELECT * FROM course WHERE id = %s", (id,))
    course = cursor.fetchone()
    
    conn.close()
    
    if course:
        return jsonify(course)
    else:
        return jsonify({'error': 'Course not found'}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM course")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(DISTINCT school) as schools FROM course")
    schools = cursor.fetchone()['schools']
    
    cursor.execute("SELECT COUNT(DISTINCT teacher) as teachers FROM course")
    teachers = cursor.fetchone()['teachers']
    
    cursor.execute("SELECT SUM(students) as total_students FROM course")
    total_students = cursor.fetchone()['total_students']
    
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
    
    cursor.execute("SELECT title, students FROM course ORDER BY students DESC LIMIT 10")
    courses = cursor.fetchall()
    
    conn.close()
    
    return jsonify(courses)

@app.route('/api/school_distribution', methods=['GET'])
def get_school_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT school, COUNT(*) as count 
        FROM course 
        GROUP BY school 
        ORDER BY count DESC 
        LIMIT 10
    """)
    schools = cursor.fetchall()
    
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

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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
        
        if hash_password(password) != user['password']:
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
        
        if hash_password(current_password) != user['password']:
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
    app.run(host='0.0.0.0', port=8080, debug=True)