import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns
import warnings
from sklearn.metrics import *
from sklearn.linear_model import *
from sklearn.neighbors import *
from sklearn.tree import *
from sklearn.ensemble import *
from xgboost import *
from sklearn.model_selection import *

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_rows', 100, 'display.max_columns', 1000, "display.max_colwidth", 1000, 'display.width', 1000)

# final_data.xlsx 是上一次最后数据处理后的
data = pd.read_excel("final_data.xlsx", na_values=np.nan)

# 将数据划分输入和结果集
X = data[data.columns[1:]]
y_reg = data[data.columns[0]]

# 切分训练集和测试集， random_state是切分数据集的随机种子
x_train, x_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.3, random_state=42)


# 评价指标函数定义，其中R2的指标可以由模型自身得出，后面的score即为R2
def evaluation(model):
    ypred = model.predict(x_test)
    mae = mean_absolute_error(y_test, ypred)
    mse = mean_squared_error(y_test, ypred)
    rmse = math.sqrt(mse)
    print("MAE: %.2f" % mae)
    print("MSE: %.2f" % mse)
    print("RMSE: %.2f" % rmse)
    return ypred


#  线性回归
model_LR = LinearRegression()
model_LR.fit(x_train, y_train)
print("params: ", model_LR.get_params())
print("train score: ", model_LR.score(x_train, y_train))
print("test score: ", model_LR.score(x_test, y_test))
predict_y = evaluation(model_LR)
test_y = np.array(y_test)
plt.figure(figsize=(10, 10))
plt.title('线性回归-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()
#  K近邻
model_knn = KNeighborsRegressor()
model_knn.fit(x_train, y_train)
print("params: ", model_knn.get_params())
print("train score: ", model_knn.score(x_train, y_train))
print("test score: ", model_knn.score(x_test, y_test))
predict_y = evaluation(model_knn)
plt.figure(figsize=(10, 10))
plt.title('KNN-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()
#  决策树回归
model_dtr = DecisionTreeRegressor(max_depth=38, random_state=30)
model_dtr.fit(x_train, y_train)
print("params: ", model_dtr.get_params())
print("train score: ", model_dtr.score(x_train, y_train))
print("test score: ", model_dtr.score(x_test, y_test))
predict_y = evaluation(model_dtr)
model_dtr.get_depth()
plt.figure(figsize=(10, 10))
plt.title('决策树回归-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()
#  随机森林
model_rfr = RandomForestRegressor(random_state=30)
model_rfr.fit(x_train, y_train)
print("params: ", model_rfr.get_params())
print("train score: ", model_rfr.score(x_train, y_train))
print("test score: ", model_rfr.score(x_test, y_test))
predict_y = evaluation(model_rfr)
plt.figure(figsize=(10, 10))
plt.title('随机森林-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()
#  XGBoost
model_xgbr = XGBRegressor(n_estimators=200, max_depth=5, random_state=1024)
model_xgbr.fit(x_train, y_train)
print("params: ", model_xgbr.get_params())
print("train score: ", model_xgbr.score(x_train, y_train))
print("test score: ", model_xgbr.score(x_test, y_test))
predict_y = evaluation(model_xgbr)
plt.figure(figsize=(10, 10))
plt.title('XGBR-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()
#  集成模型Voting
model_voting = VotingRegressor(estimators=[('model_LR', model_LR),
                                           ('model_knn', model_knn),
                                           ('model_dtr', model_dtr),
                                           ('model_rfr', model_rfr),
                                           ('model_xgbr', model_xgbr)])
model_voting.fit(x_train, y_train)
# print("params: ", model_voting.get_params())
print("train score: ", model_voting.score(x_train, y_train))
print("test score: ", model_voting.score(x_test, y_test))
predict_y = evaluation(model_voting)
plt.figure(figsize=(10, 10))
plt.title('集成模型voting-真实值预测值对比')
plt.plot(predict_y[:50], 'ro-', label='预测值')
plt.plot(test_y[:50], 'go-', label='真实值')
plt.legend()
plt.show()

# 这里的列取final_data中，除0-1和独热编码形式的数据
corr_cols = list(data.columns[:28]) + list(data.columns[43:49])
test_data = data[corr_cols]
test_data_corr = test_data.corr()
price_corr = dict(test_data_corr.iloc[0])
price_corr = sorted(price_corr.items(), key=lambda x: abs(x[1]), reverse=True)
# 输出按绝对值排序后的相关系数
print(price_corr)
price_corr_cols = [r[0] for r in price_corr]
price_data = test_data_corr[price_corr_cols].loc[price_corr_cols]
plt.figure(figsize=(15, 10))
plt.title("相关系数热力图")
ax = sns.heatmap(price_data, linewidths=0.5, cmap='OrRd', cbar=True)
plt.show()
feature_important = sorted(
    zip(x_train.columns, map(lambda x: round(x, 4), model_rfr.feature_importances_)),
    key=lambda x: x[1], reverse=True)

for i in range(33):
    print(feature_important[i])
f1_list = []
f2_list = []

for i in range(33):
    f1_list.append(feature_important[i][0])

for i in range(1, 34):
    f2_list.append(price_corr[i][0])

cnt = 0
for i in range(33):
    if f1_list[i] in f2_list:
        print(f1_list[i])
        cnt += 1
print("共有" + str(cnt) + "个重复特征！")
