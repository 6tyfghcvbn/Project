import pandas as pd

# 读取 Excel 文件
def process_carbon_data(file_path):
    # 读取 Excel 数据
    data = pd.read_excel(file_path)

    # 假设数据有两列：产品名称和排放因子，列名需要根据实际文件调整
    result = []
    for index, row in data.iterrows():
        product = row[0]  # 第一列为产品名称
        emission = row[1]  # 第二列为排放因子
        result.append({
            'product': product,
            'emission': emission
        })

    return result

# 输出结果
if __name__ == "__main__":
    file_path = "Carbon.xlsx"  # 文件路径
    formatted_data = process_carbon_data(file_path)
    for item in formatted_data:
        print(f"{{product: '{item['product']}', emission: '{item['emission']}'}},")