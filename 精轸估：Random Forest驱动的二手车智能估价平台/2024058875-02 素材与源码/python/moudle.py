import pandas as pd
from sklearn2pmml import sklearn2pmml, make_pmml_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder

# 1. Load Excel data
data = pd.read_excel("new_final_data(1).xlsx")

# 2. Identify categorical and numeric columns
categorical_cols = ["车牌所在地", "厂商", "变速箱", "燃油形式"]
numeric_cols = ["新车售价", "最大马力(Ps)", "注册日期差（天）","最大扭矩(N·m)","最大功率(kW)","出厂日期差（天）","高度(mm)","最大功率转速(rpm)","宽度(mm)",
"轴距(mm)","工信部综合油耗(L/100km)","最大扭矩转速(rpm)","长度(mm)","后轮距(mm)","整备质量(kg)","行李厢容积(L)","最高车速(km/h)","官方0-100km/h加速(s)","油箱容积(L)","前轮距(mm)","压缩比","排量(L)","商业险过期日期差（天）","最小离地间隙(mm)","交强险过期日期差（天）","行驶里程", ]  # 替换为实际的数值型变量列表

# 3. Configure the categorical transformer with dense output
categorical_transformer = OneHotEncoder(handle_unknown="ignore")

# 4. Configure the numeric transformer (standardization in this example)
numeric_transformer = StandardScaler()

# 5. Create the preprocessor that handles both categorical and numeric variables
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_transformer, categorical_cols),
        ("numeric", numeric_transformer, numeric_cols)
    ]
)

# Define target variable
target_col = "售价"
y = data[target_col]
X = data.drop(target_col, axis=1)

# 6. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 7. Choose a model based on task type
if isinstance(y_train.iloc[0], (int, float)):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
else:
    model = RandomForestClassifier(n_estimators=100, random_state=42)

# 8. Update the pipeline to include the preprocessor
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model),
])

# 9. Train the updated pipeline on the training data
pipeline.fit(X_train, y_train)

# 10. Export the trained pipeline as a PMML file
sklearn2pmml(pipeline, "二手车模型.pmml")
