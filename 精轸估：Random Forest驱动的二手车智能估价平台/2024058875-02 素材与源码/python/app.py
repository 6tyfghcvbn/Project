from flask import Flask, request, jsonify
import pandas as pd
from pypmml import Model
import numpy as np
from flask_cors import CORS

# 加载PMML模型文件
model = Model.load('二手车模型.pmml')

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict_price():
    # 获取前端发送的JSON数据
    data = request.get_json()

    # 将JSON数据转换为Pandas DataFrame
    df = pd.DataFrame([data])

    try:
        # 预测
        predictions = model.predict(df)
        print("Predictions:", predictions)
        
        # 检查预测结果的类型并提取预测值
        if isinstance(predictions, pd.DataFrame):
            # 确保预测结果DataFrame中有数据
            if not predictions.empty:
                # 假设预测值在第一列，根据实际情况调整
                predicted_y_value = predictions.iloc[0, 0]
            else:
                return jsonify({'error': 'Prediction result is empty.'}), 400
        elif isinstance(predictions, np.ndarray):
            # 如果是numpy数组，直接取第一个元素
            predicted_y_value = predictions[0]
        else:
            return jsonify({'error': 'Unexpected prediction result type.'}), 500
    except Exception as e:
        # 捕获并返回任何其他异常
        return jsonify({'error': str(e)}), 500

    return jsonify({'predicted_price': predicted_y_value})

if __name__ == '__main__':
    app.run(debug=True)