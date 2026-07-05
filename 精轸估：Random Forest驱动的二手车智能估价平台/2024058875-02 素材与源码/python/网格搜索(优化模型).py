import pandas as pd
from sklearn2pmml import sklearn2pmml, make_pmml_pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
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

# 6. Choose a model and define parameter grid (assuming a regression task for this example)
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

model = RandomForestRegressor(random_state=42)

# 7. Perform grid search instead of directly initializing the model
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", grid_search),  # Here we use the GridSearchCV instance directly in the pipeline
])

# 8. Train the pipeline with grid search
pipeline.fit(X_train, y_train)

# After the fit, the best parameters are automatically set in the grid_search attribute
best_params = grid_search.best_params_
print(f"Best Parameters found: {best_params}")

