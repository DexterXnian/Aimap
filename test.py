import re

# 您提供的消息内容
message_content = """
党建风格的地图通常采用红色、黄色等具有中国特色的颜色。以下是7个hex颜色的建议，分别对应您提供的地点类型：

1. 住宅： #ff6a6a（淡红色）
2. 曹杨新村街道： #ffc34d（金黄色，代表繁荣）
3. 公园绿地： #50de89（绿色，代表自然和生机）
4. 湖泊： #87e0ff（蓝色，代表水的颜色）
5. 非住宅： #ffafcc（浅紫色，表示其他建筑）
6. 河流： #add8e6（另一种蓝色，稍微深一些，表示水体）
7. 道路： #fafad2（米色，表示道路和交通）

这些颜色是根据常见的党建主题颜色进行选择的，您可以根据实际需求进行调整。在设计地图时，确保颜色之间有足够的对比度，以便用户可以清晰地区分不同的地点类型。
"""

# 定义一个字典来存储图层名称和对应的颜色代码
color_dict = {}

# 使用正则表达式提取颜色代码和对应的图层名称
pattern = r"\d+\.\s*([\u4e00-\u9fa5a-zA-Z0-9]+)[：:：\s-]+\s*#([A-Fa-f0-9]{6})"
matches = re.findall(pattern, message_content)

# 遍历匹配结果并填充字典
for match in matches:
    layer_name, hex_color = match
    color_dict[layer_name] = f'#{hex_color}'
    
# 打印结果
for layer, color in color_dict.items():
    print(f'{layer}_____________________{color}')
