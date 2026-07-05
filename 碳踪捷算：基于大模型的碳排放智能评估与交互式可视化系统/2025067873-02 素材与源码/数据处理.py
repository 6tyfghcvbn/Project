
import pandas as pd
from difflib import SequenceMatcher
from tqdm import tqdm

def text_similarity(a, b):
    """优化后的相似度计算函数"""
    return SequenceMatcher(None, str(a), str(b)).ratio()

def cluster_products(df, threshold=0.75):
    """稳健型聚类函数"""
    clusters = []
    texts = df['产品类型'].astype(str).unique()

    with tqdm(total=len(texts), desc='聚类进度') as pbar:
        for text in texts:
            matched = False
            for cluster in clusters:
                if text_similarity(text, cluster[0]) >= threshold:
                    cluster.append(text)
                    matched = True
                    break
            if not matched:
                clusters.append([text])
            pbar.update(1)
    return {c[0] :c for c in clusters}

try:
    # 读取数据（处理中文路径）
    df = pd.read_excel('中国产品全生命周期温室气体排放系数库.xlsx', engine='openpyxl')
    df['产品类型'] = df['产品类型'].fillna('未知类型')

    # 执行聚类
    clusters = cluster_products(df)

    # 生成映射关系
    df['_group'] = df['产品类型'].map(
        lambda x: next(k for k ,v in clusters.items() if str(x) in v)
    )

    # 保留首条数据并保存
    df.groupby('_group').first().reset_index().drop('_group', axis=1) \
        .to_excel('处理后_排放系数库.xlsx', index=False)

    print(f"处理成功：原始数据 {len(df)} 条 → 去重后 {len(clusters)} 条")

except Exception as e:
    print(f"错误详情：{str(e)}")
    print("排查建议：\n1. 确认文件未被其他程序打开\n2. 检查产品类型列是否存在特殊字符")