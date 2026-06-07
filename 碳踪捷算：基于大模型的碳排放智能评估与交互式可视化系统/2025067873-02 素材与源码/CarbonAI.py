from fastapi import FastAPI, HTTPException, File, Response, UploadFile
from pydantic import BaseModel
import websockets
import json
import base64
import hashlib
import hmac
from datetime import datetime, time, timezone
from urllib.parse import urlparse, urlencode
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
import gzip

APP_ID = "your_app_id_here"  # 替换为你的APP ID
API_KEY = "your_api_key_here"  # 替换为你的API Key
API_SECRET = "your_api_secret_here"  # 替换为你的API Secret
SPARK_URL = "your_spark_url_here"  # 替换为你的Spark URL

app = FastAPI()

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问，生产环境应限制为具体域名
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

class ChatRequest(BaseModel):
    message: str
    data: list = None  # 添加数据字段

class CarbonExpertSystem:
    """碳足迹专业处理系统"""

    def __init__(self):
        self.host = urlparse(SPARK_URL).netloc
        self.path = urlparse(SPARK_URL).path
        self.system_prompt = {
            "role": "system",
            "content": """您是全球碳足迹管理专家CarbonAI，具备ISO 14064认证资质。主要职责包括：
1. 基于生命周期法(LCA)和排放因子法计算碳排放
2. 解析范围1/2/3排放源（参照GHG Protocol标准）
3. 对接CPCD数据库
4. 生成符合ISO 14040标准的报告

对话原则：
- 使用专业术语但解释清晰（如：tCO2e、GWP100）
- 数据需标注来源（例：IPCC 2023排放因子）
- 复杂计算分步展示并验证假设条件"""
        }

    def _generate_auth_url(self):
        """生成鉴权URL"""
        from datetime import datetime, timezone
        cur_time = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        signature_origin = f"host: {self.host}\ndate: {cur_time}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(API_SECRET.encode(), signature_origin.encode(), hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode()
        authorization = base64.b64encode(
            f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'.encode()
        ).decode()
        return f"{SPARK_URL}?{urlencode({'authorization': authorization, 'date': cur_time, 'host': self.host})}"

    async def chat(self, messages, temperature=0.3, max_tokens=3072, retry_count=3):
        """增强版专业对话"""
        last_error = None

        for attempt in range(retry_count):
            try:
                ws_url = self._generate_auth_url()
                print(f"尝试连接WebSocket (第{attempt+1}次): {ws_url}")

                async with websockets.connect(ws_url, open_timeout=10) as ws:
                    # 注入系统提示词并保留最近3轮对话
                    enhanced_msg = [self.system_prompt] + messages[-3:]
                    print(f"发送到 WebSocket 的消息: {json.dumps(enhanced_msg, ensure_ascii=False)}")

                    request = {
                        "header": {"app_id": APP_ID, "uid": "carbon_expert"},
                        "parameter": {"chat": {"domain": "lite", "temperature": temperature, "max_tokens": max_tokens}},
                        "payload": {"message": {"text": enhanced_msg}}
                    }

                    await ws.send(json.dumps(request, ensure_ascii=False))
                    print("WebSocket 请求已发送")

                    full_response = ""
                    async for resp in ws:
                        data = json.loads(resp)
                        print(f"WebSocket 响应: {data}")

                        if data["header"]["code"] != 0:
                            raise Exception(f"API Error: {data['header']['message']}")

                        # 拼接流式响应
                        texts = data["payload"]["choices"]["text"]
                        if texts and isinstance(texts, list):
                            for text_item in texts:
                                if "content" in text_item and text_item["content"].strip():
                                    full_response += text_item["content"]

                        # 如果流式响应结束，跳出循环
                        if data["header"]["status"] == 2:
                            break

                    if not full_response.strip():
                        print("WebSocket 返回空响应")
                        last_error = "WebSocket 返回空响应，请检查对话逻辑或输入内容"
                        continue  # 重试

                    return full_response

            except websockets.exceptions.ConnectionClosedError as e:
                last_error = f"WebSocket连接意外关闭: {str(e)}"
                print(f"尝试 {attempt+1}/{retry_count} 失败: {last_error}")
                await asyncio.sleep(1)  # 等待1秒后重试
                continue
            except asyncio.TimeoutError:
                last_error = "WebSocket连接超时"
                print(f"尝试 {attempt+1}/{retry_count} 失败: {last_error}")
                await asyncio.sleep(1)
                continue
            except Exception as e:
                last_error = f"WebSocket处理出错: {str(e)}"
                print(f"尝试 {attempt+1}/{retry_count} 失败: {last_error}")
                await asyncio.sleep(1)
                continue

        error_details = {
            "error": last_error if last_error else "未知错误",
            "retry_count": retry_count,
            "suggestion": "请检查网络连接或稍后重试"
        }
        raise HTTPException(
            status_code=503,
            detail=error_details,
            headers={"Retry-After": "10"}
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        expert = CarbonExpertSystem()
        messages = [{"role": "user", "content": request.message}]

        # 如果请求中包含 useFileData 且为 True，则加载 Excel 数据
        if hasattr(request, 'useFileData') and request.useFileData:
            excel_path = os.path.join(os.path.dirname(__file__), '处理后_排放系数库.xlsx')
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"文件 {excel_path} 不存在")

            excel_data = pd.read_excel(excel_path)
            excel_context = "\n".join([f"{row}" for row in excel_data.to_dict(orient="records")])
            messages.append({"role": "system", "content": f"以下是相关的 Excel 数据内容：\n{excel_context}"})

        # 处理聊天请求
        response = await expert.chat(messages, temperature=0.3, max_tokens=3072)
        if not response.strip():
            error_msg = "AI回复为空，可能是输入内容不明确或API限制"
            print(error_msg)
            raise HTTPException(
                status_code=502,
                detail=error_msg,
                headers={"Retry-After": "5"}
            )

        return {"response": response}

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"处理请求时出错: {str(e)}"
        print(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg,
            headers={"X-Error-Code": "API_CONNECTION_FAILURE"}
        )

@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        # 读取上传的 Excel 文件
        content = await file.read()
        excel_data = pd.read_excel(content)

        # 将数据转换为 JSON 格式
        json_data = excel_data.to_dict(orient="records")

        # 压缩 JSON 数据
        compressed_data = gzip.compress(json.dumps(json_data).encode('utf-8'))

        return Response(content=compressed_data, media_type="application/gzip")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)