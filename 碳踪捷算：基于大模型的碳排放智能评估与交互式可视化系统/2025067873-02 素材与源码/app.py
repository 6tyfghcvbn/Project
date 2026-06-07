from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta
import re
import sqlite3
import secrets
import logging
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask_session import Session
import numpy as np
from wordcloud import WordCloud
import subprocess
# ==================== 基础配置 ====================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 日志配置
if os.environ.get('ENV') == 'production':
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath('user.db')


# ==================== 工具函数 ====================
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('请先登录', 'error')
            logger.debug(f"未登录用户尝试访问 {request.path}，重定向到登录页")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def is_password_complex(password):
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


def execute_db_query(query, params=(), fetch_one=False):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(query, params)
            if query.lower().startswith('select'):
                result = c.fetchone() if fetch_one else c.fetchall()
            else:
                conn.commit()
                result = None
            return result
    except sqlite3.Error as e:
        logger.error(f"数据库操作失败: {str(e)} | 查询: {query} | 参数: {params}")
        return None



def _generate_chart(categories, values, total):
    """生成碳排放可视化图表（含多图表类型）"""
    try:
        plt.rcParams.update({
            'font.sans-serif': ['SimHei'],  # 解决中文乱码
            'axes.unicode_minus': False,
            'figure.autolayout': True
        })

        fig = plt.figure(figsize=(22, 16))
        gs = fig.add_gridspec(2, 2, width_ratios=[1.5, 1])

        # 柱状图
        ax1 = fig.add_subplot(gs[0, 0])
        colors = ['#4CAF50' if "出行" in cat else '#2196F3' for cat in categories]
        bars = ax1.bar(categories, values, color=colors, alpha=0.8)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                     f'{height:.2f}kg', ha='center', va='bottom', fontsize=9)
        ax1.set_title('今日碳排放统计', fontsize=14)
        ax1.set_xlabel('项目类别', fontsize=12)
        ax1.set_ylabel('碳排放量 (kg)', fontsize=12)
        ax1.tick_params(axis='x', rotation=30)

        # 饼图
        ax2 = fig.add_subplot(gs[0, 1])
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        ax2.pie(values, labels=categories, colors=colors_pie,
                autopct='%1.1f%%', startangle=150, explode=[0.03] * len(categories))
        ax2.set_title('碳排放占比', fontsize=14)

        # 雷达图（分类聚合）
        ax3 = fig.add_subplot(gs[1, 0], polar=True)
        category_groups = {
            "居住类": ["每月用电", "每月用水", "燃气使用"],
            "出行类": ["飞机出行", "汽车通勤", "火车旅行", "公交出行", "地铁通勤"],
            "饮食类": ["主食消费", "肉类消费"],
            "衣物类": ["棉质衣物", "化纤衣物", "混纺衣物"]
        }
        group_values = [sum(v for c, v in zip(categories, values) if c in group)
                        for group in category_groups.values()]
        angles = np.linspace(0, 2 * np.pi, len(category_groups), endpoint=False)
        ax3.plot(angles, group_values, color='#FF6F00', linewidth=2)
        ax3.fill(angles, group_values, color='#FFB300', alpha=0.25)
        ax3.set_xticklabels(category_groups.keys())
        ax3.set_title('分类碳排放雷达图', pad=20)

        # 热力图（排放强度）
        ax4 = fig.add_subplot(gs[1, 1])
        heatmap_data = np.array([values]).T
        im = ax4.imshow(heatmap_data, cmap='YlGnBu', aspect='auto')
        ax4.set_yticks(np.arange(len(categories)))
        ax4.set_yticklabels(categories)
        ax4.set_title('排放强度热力图')
        plt.colorbar(im, ax=ax4, label="kg CO₂")

        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)  # 显式释放资源
        return img_base64
    except Exception as e:
        logger.error(f"图表生成失败: {str(e)} | 分类: {categories} | 数值: {values}")
        return ''


def _get_emission_level(total):
    """根据总排放量返回等级"""
    if not isinstance(total, (int, float)):
        logger.error(f"无效的排放量类型: {type(total)}")
        return "数据异常"
    if total < 10:
        return "节碳达人"
    elif 10 <= total < 22.5:
        return "中级碳人"
    else:
        return "终极碳人"


# ==================== 数据库初始化 ====================
def initialize_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            '''
            conn.execute(create_table_query)
            table_exists = conn.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            ''').fetchone()
            if not table_exists:
                raise RuntimeError("用户表创建失败")
            logger.info("数据库初始化完成，用户表已创建")
    except sqlite3.Error as e:
        logger.error(f"数据库初始化失败: {str(e)} | SQL: {create_table_query}")
        raise


# ==================== 路由功能 ====================
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not (username and password):
            flash('用户名和密码不能为空', 'error')
            return redirect(url_for('register'))

        if not is_password_complex(password):
            flash('密码需至少8位，包含大小写字母和数字', 'error')
            logger.debug(f"用户 {username} 注册失败：密码复杂度不满足")
            return redirect(url_for('register'))

        if execute_db_query("SELECT * FROM users WHERE username=?", (username,), fetch_one=True):
            flash('用户名已存在', 'error')
            logger.debug(f"用户 {username} 注册失败：用户名重复")
            return redirect(url_for('register'))

        hashed_pwd = generate_password_hash(password)
        execute_db_query("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pwd))
        flash('注册成功，请登录', 'success')
        logger.info(f"用户 {username} 注册成功")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = execute_db_query("SELECT * FROM users WHERE username=?", (username,), fetch_one=True)

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session.permanent = True
            logger.info(f"用户 {username} 登录成功")
            return redirect(url_for('success'))

        flash('用户名或密码错误', 'error')
        logger.debug(f"用户 {username} 登录失败：密码错误")
    return render_template('login.html')


@app.route('/success')
@login_required
def success():
    username = session['username']
    chart_data = session.get('chart_data', '')
    if not chart_data:
        logger.warning(f"用户 {username} 的图表数据为空")

    return render_template(
        'success.html',
        username=username,  # 保留username用于调试（可选）
        chart=chart_data,
        debug=app.debug  # 传递调试模式状态到模板
    )

@app.route('/CarbonAI')
@login_required
def CarbonAI():
    """AI页面路由"""
    logger.debug("用户访问AI页面")
    return render_template('CarbonAI.html')

# 新增：ditu 页面路由（碳排放分布）
@app.route('/input')
@login_required
def input():
    return render_template('input.html')  # 需创建对应的模板文件

@app.route('/qxt')
@login_required
def qxt_page():
    return render_template('qxt.html')

@app.route('/bintu')
@login_required
def bintu_page():
    return render_template('bintu.html')  # 需创建对应的模板文件


@app.route('/Dqp')
@login_required
def Dqp():
    return render_template('Dqp.html')  # 需创建对应的模板文件


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('您已成功注销', 'success')
    logger.info(f"用户 {session.get('username')} 注销")
    return redirect(url_for('login'))


@app.route('/input')
@login_required
def input_page():
    return render_template('input.html')


COEFFICIENTS = {
    # 居住类
    "每月用电": 0.785,"每月用水": 0.90,"燃气使用": 0.19,
    # 出行类
    "飞机": 0.246,"汽车": 0.30,"火车": 0.03,"公交": 0.20,"地铁": 0.040,
    # 衣食类
    "主食": 0.0065,"肉类": 0.0125,"棉质衣物": 0.28,"化纤衣物": 0.55,"混纺衣物": 0.32,
    }


@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        categories = request.form.getlist('category[]')
        values = list(map(float, request.form.getlist('value[]')))

        if len(categories) != len(values) or not categories:
            logger.error(f"用户 {session['username']} 输入错误：分类与数值数量不匹配")
            return "分类与数值数量不匹配", 400

        calculated = [v * COEFFICIENTS[c] for c, v in zip(categories, values)]
        total = sum(calculated)
        level = _get_emission_level(total)

        img_base64 = _generate_chart(categories, calculated, total)
        session.update({
            'chart_data': img_base64,
            'total_emission': f"{total:.2f}",
            'level': level
        })
        return redirect(url_for('result'))

    except KeyError as e:
        logger.error(f"用户 {session['username']} 输入无效分类：{e}")
        return f"无效分类：{e}", 400
    except ValueError:
        logger.error(f"用户 {session['username']} 输入非数字值")
        return "输入值必须为数字", 400


@app.route('/result')
@login_required
def result():
    return render_template(
        'result.html',
        chart=session.get('chart_data', ''),
        total=session.get('total_emission', '0.00'),
        level=session.get('level', '未检测到数据')
    )





if __name__ == '__main__':
    try:        # 启动 CarbonAI.py 作为子进程
        carbon_process = subprocess.Popen(
            ['python', 'CarbonAI.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 等待 CarbonAI.py 启动完成
        initialize_database()
        Session(app)
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=os.environ.get('ENV') != 'production',
            use_reloader=False
        )
    except Exception as e:
        logger.critical(f"应用启动失败: {str(e)}")
        exit(1)
    finally:
        # 确保子进程在主进程退出时终止
        if carbon_process:
            carbon_process.terminate()