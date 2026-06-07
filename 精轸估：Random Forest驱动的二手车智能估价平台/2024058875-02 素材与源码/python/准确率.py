import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# 1. Load Excel data
data = pd.read_excel("new_final_data.xlsx")

# 2. Identify categorical columns
categorical_cols = ["车牌所在地", "厂商", "变速箱", "燃油形式"]

# 3. Configure the categorical transformer with dense output
categorical_transformer = OneHotEncoder(handle_unknown="ignore")

# 4. Create the preprocessor
preprocessor = ColumnTransformer(
    transformers=[("categorical", categorical_transformer, categorical_cols)]
)

# Define target variable
target_col = "售价"
y = data[target_col]
X = data.drop(target_col, axis=1)

# 5. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Since it's a regression problem, use RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)

# 7. Update the pipeline to include the preprocessor
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model),
])

# 8. Train the updated pipeline on the training data and evaluate on the test set
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

# 9. Calculate R² Score and convert it to percentage
r2_score = pipeline.score(X_test, y_test)
r2_score_percentage = r2_score * 100  # Convert R² Score to percentage

# 10. Print the R² Score in percentage form
print(f"模型的R² Score为: {r2_score_percentage:.2f}%")