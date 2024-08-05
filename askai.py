from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

import geopandas as gpd
import fiona
import re



if __name__ == '__main__':
    #星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
    #星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
    SPARKAI_APP_ID = '4910a7ba'
    SPARKAI_API_SECRET = 'OTkwMjZiN2NlODRlM2YxYzBhZGU1NDc5'
    SPARKAI_API_KEY = '9fa4e03083930ff0dbca46740b16631a'
    #星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
    SPARKAI_DOMAIN = 'generalv3.5'

    gpkg_file = r"D:\4\demo\ai地图\gpkg\all_test.gpkg"
    # 获取所有 layer 的名字
    with fiona.Env():
        layers = fiona.listlayers(gpkg_file)
        print(layers)

        # 生成消息内容
    if len(layers) == 0:
        raise ValueError("GeoPackage 文件中没有图层。")
    else:
        layer_names = ", ".join(layers)
        message_content = f'我要做党建风格的地图，请给我{len(layers)}个hex颜色的党建风格的颜色，分别给{layer_names}，按重要性排列，用逗号分隔'


    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )

    messages = [ChatMessage(
        role="user",
        content=message_content
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])

    # 定义一个字典来存储图层名称和对应的颜色代码
    color_dict = {}

    # 使用正则表达式提取颜色代码和对应的图层名称
    pattern = r"(\d+\.\s\S+\s-\s.*?)(#[A-Fa-f0-9]{6})"
    matches = re.findall(pattern, a.generations[0][0].text)

    # 遍历匹配结果并填充字典
    for match in matches:
        layer_info, hex_color = match
        layer_name = layer_info.split(' - ')[0].split('. ')[1]
        color_dict[layer_name] = hex_color

    # 打印结果
    for layer, color in color_dict.items():
        print(f'{layer}: {color}')

