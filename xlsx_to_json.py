import pandas as pd
import json

def xlsx_to_json(excel_file, json_file):
# 读取 Excel 文件
    excel_file = r'D:\4\城市更新\城市更新点位tojson.xlsx'
    df = pd.read_excel(excel_file)

    # 将 DataFrame 转换为 JSON 格式
    json_data = df.to_json(orient='records', force_ascii=False)

    # 将 JSON 数据写入文件
    with open(r'D:\4\城市更新\outputjson.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print("Excel 数据已成功转换为 JSON 格式！")


def xlsx_to_json2():
    # 读取 Excel 文件
    excel_file = r'D:\4\城市更新\城市更新点位tojson.xlsx'
    df = pd.read_excel(excel_file)

    # 按区域分类
    grouped = df.groupby('区域')

    # 创建一个字典，用于存储分组后的数据
    data = {}

    # 遍历每个分组，并将序号列改为 ID 列
    for name, group in grouped:
        # 重命名序号列为 ID
        group = group.rename(columns={'序号': 'id'})
        # 将分组数据转换为字典并添加到 data 字典中
        data[name] = group.to_dict(orient='records')

    # 将数据转换为 JSON 格式
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # 将 JSON 数据写入文件
    with open(r'D:\4\城市更新\outputjson2.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print("Excel 数据已成功转换为 JSON 格式，并按区域分类！")

if __name__ == '__main__':
    xlsx_to_json2()