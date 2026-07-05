import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# 加载数据
data = pd.read_excel("new_final_data.xlsx")

# 定义类别和数值列
categorical_cols = ["车牌所在地", "厂商", "变速箱", "燃油形式"]
numerical_cols = [col for col in data.columns if col not in categorical_cols + ["售价"]]

# 数据预处理设置与分割
preprocessor = ColumnTransformer(transformers=[
    ('num', SimpleImputer(strategy='mean'), numerical_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

X = data.drop("售价", axis=1)
y = data["售价"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型选择与管道配置
model = RandomForestRegressor(n_estimators=100, random_state=42)
pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])

# 训练模型
pipeline.fit(X_train, y_train)

# 提取特征重要性
try:
    encoded_columns = pipeline.named_steps['preprocessor'].transformers_[1][1].get_feature_names_out(categorical_cols)
except AttributeError:  # 适配不同版本的sklearn
    encoded_columns = pipeline.named_steps['preprocessor'].transformers_[1][1].get_feature_names(input_features=categorical_cols)
feature_names = numerical_cols + list(encoded_columns)

importances_raw = pipeline.named_steps["model"].feature_importances_
total_importance = sum(importances_raw)
importances_normalized = {feature: imp / total_importance * 100 for feature, imp in zip(feature_names, importances_raw)}

# 简化特征重要性
def aggregate_categorical_importance(importances_normalized, categorical_cols):
    simplified = {}
    for feature, importance in importances_normalized.items():
        for cat_col in categorical_cols:
            if feature.startswith(cat_col + "_"):
                simplified[cat_col] = simplified.get(cat_col, 0) + importance
                break
        else:
            simplified[feature] = importance
    return simplified

simplified_importances = aggregate_categorical_importance(importances_normalized, categorical_cols)

# 输出所有简化后的特征重要性
for feature, importance in simplified_importances.items():
    print(f"特征: {feature}, 重要性: {importance:.2f}%")