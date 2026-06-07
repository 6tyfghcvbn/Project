const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');

const app = express();

app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*'); // 允许所有源，生产环境中应替换为具体的允许源
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'); // 允许的HTTP方法
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type'); // 允许的自定义请求头
  if (req.method === 'OPTIONS') {
    res.sendStatus(204); // 对于预检请求，直接返回204状态码
  } else {
    next();
  }
});

// 创建MySQL连接池
const pool = mysql.createPool({
  host: 'localhost', // 替换为您的MySQL服务器地址
  user: 'yang', // 替换为具有查询权限的MySQL用户
  password: '001216', // 替换为对应的MySQL用户密码
  database: 'try', // 使用您创建的数据库名
  waitForConnections: true, // 是否等待可用连接（推荐）
  connectionLimit: 10, // 连接池大小
  queueLimit: 0, // 查询队列限制（默认无限制）
});

// 用户验证函数
async function checkUserExistence(username, password) {
  try {
    const [rows] = await pool.query(
      'SELECT * FROM your_users_table WHERE username = ? AND password = ?', // 替换为实际的用户表名
      [username, password]
    );

    return rows.length > 0; // 如果查询结果有记录，说明用户存在
  } catch (error) {
    console.error('查询用户信息时发生错误:', error);
    throw new Error('服务器内部错误，请稍后再试'); // 抛出错误，让上层处理函数捕获并返回适当的HTTP状态码
  }
}

app.use(bodyParser.json()); // 解析JSON格式的请求体

app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const userExists = await checkUserExistence(username, password);

    if (userExists) {
      res.status(200).json({ status: 'success', message: '登录成功' }); // 用户已注册，登录成功
    } else {
      res.status(401).json({ status: 'error', message: '用户不存在或密码错误' }); // 用户未注册，登录失败
    }
  } catch (error) {
    console.error('登录验证过程中发生错误:', error);
    res.status(500).json({ status: 'error', message: '服务器内部错误，请稍后再试' }); // 后端处理错误，返回500状态码
  }
});
app.post('/api/register', async (req, res) => {
  const { username, password, email } = req.body;

  try {
    // 检查用户名是否已存在
    const [existingUser] = await pool.query(
      'SELECT * FROM your_users_table WHERE username = ?',
      [username]
    );

    if (existingUser.length > 0) {
      return res.status(409).json({ status: 'error', message: '用户名已存在' });
    }

    // 插入新用户数据到数据库
    await pool.query(
      'INSERT INTO your_users_table (username, password, email) VALUES (?, ?, ?)',
      [username, password, email]
    );

    res.status(201).json({ status: 'success', message: '注册成功' });
  } catch (error) {
    console.error('注册过程中发生错误:', error);
    res.status(500).json({ status: 'error', message: '服务器内部错误，请稍后再试' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});