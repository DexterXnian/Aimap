import geopandas as gpd
import os
from PIL import Image
import re
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Patch
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class AImapping:
    def __init__(self, map_name, description, *data_path):
        self.map_name = map_name  # 实例属性
        self.description = description # 可以 img_to_map 也可以 txt_to_map
        self.shapefiles_path = data_path
        self.polygons_dict = {}
        self.lines_dict = {}
        self.points_dict = {}

        for path in data_path:
            flag ,shapefile_dict = self.read_geodata(path)
            if flag == 0:
                self.points_dict.update(shapefile_dict)
            elif flag == 1:
                self.lines_dict.update(shapefile_dict)
            elif flag == 2:
                self.polygons_dict.update(shapefile_dict)
            # print(flag)

        # color = self.get_color(self.description, len(self.polygons_dict)+len(self.lines_dict))
        color_dict = self.get_color_ai()
        print(color_dict)
        self.ai_mapping(color_dict=color_dict, poly=self.polygons_dict, line=self.lines_dict, point=self.points_dict)
        # self.mapping(map_name=self.map_name, colors=color, poly=self.polygons_dict, line=self.lines_dict, point=self.points_dict)
        # print(self.get_color(self.description, len(self.polygons_dict)+len(self.lines_dict)))
       

    def read_geodata(self, shapefiles_path):
        shapefile_dict = {}
        file_name = os.path.basename(shapefiles_path)
        gdf = gpd.read_file(shapefiles_path)
        # 检查 GeoDataFrame 的几何类型
        geometry_types = gdf.geom_type.unique()
        # 判断是否是面数据还是线数据
        if 'Polygon' in geometry_types or 'MultiPolygon' in geometry_types:
            area = sum(gdf.area)
            shapefile_dict[file_name] = {'data': gdf, 'area': area}
            flag = 2
        elif 'LineString' in geometry_types or 'MultiLineString' in geometry_types:
            shapefile_dict[file_name] = {'data': gdf}
            flag = 1
        elif 'Point' in geometry_types or 'MultiPoint' in geometry_types:
            shapefile_dict[file_name] = {'data': gdf}
            flag = 0
        else:
            print("未知的几何类型")
        return flag,shapefile_dict
    
    def get_color(self, description, n_colors):   
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        # 获取文件扩展名并转换为小写
        file_extension = description.lower().split('.')[-1]
        # 判断文件扩展名是否在图像扩展名集合中
        if f".{file_extension}" in image_extensions:
            image = Image.open(description)
            image = image.convert('RGB')
            # image_np = np.array(image)
            # Resize the image to reduce computation
            image_small = image.resize((200, 200))
            image_small_np = np.array(image_small)
            # Reshape image data to a 2D array
            pixels = image_small_np.reshape(-1, 3)
            # Perform KMeans clustering
            # n_colors = 7  # Number of colors to extract
            kmeans = KMeans(n_clusters=n_colors, random_state=42).fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            # Count the frequency of each cluster in the original image
            labels = kmeans.predict(pixels)
            color_counts = Counter(labels)
            # Map the counts to the original colors
            color_weight = {tuple(colors[label]): count for label, count in color_counts.items()}
            # Sort colors by their frequency
            sorted_colors = sorted(colors, key=lambda color: color_weight[tuple(color)], reverse=True)
            # Plot the color palette
            plt.figure(figsize=(8, 6))
            plt.subplot(1, 2, 1)
            plt.imshow(image)
            plt.axis('off')
            plt.title('Original Image')
            plt.subplot(1, 2, 2)
            plt.imshow([sorted_colors])
            plt.axis('off')
            plt.title('Extracted Color Palette')
            # Convert sorted colors to hex
            sorted_colors_hex = [mcolors.rgb2hex(color / 255.0) for color in sorted_colors]
        
        else:
            print("非图像文件，无法提取颜色")
            sorted_colors_hex = []

        return sorted_colors_hex

    def get_color_ai(self):
        try:
            #星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
            SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
            #星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
            SPARKAI_APP_ID = '4910a7ba'
            SPARKAI_API_SECRET = 'OTkwMjZiN2NlODRlM2YxYzBhZGU1NDc5'
            SPARKAI_API_KEY = '9fa4e03083930ff0dbca46740b16631a'
            #星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
            SPARKAI_DOMAIN = 'generalv3.5'

            spark = ChatSparkLLM(
                spark_api_url=SPARKAI_URL,
                spark_app_id=SPARKAI_APP_ID,
                spark_api_key=SPARKAI_API_KEY,
                spark_api_secret=SPARKAI_API_SECRET,
                spark_llm_domain=SPARKAI_DOMAIN,
                streaming=False,
            )
            

            if len(self.polygons_dict) + len(self.lines_dict) == 0:
                raise ValueError("GeoPackage 文件中没有图层。")
            else:
                layer_names = ", ".join(list(self.polygons_dict.keys()) + list(self.lines_dict.keys())).replace("_曹杨新村街道.shp", " ").replace(".shp", "")
                message_content = f'我要做党建风格的地图，请直接给我{len(self.polygons_dict) + len(self.lines_dict)}个hex颜色的党建风格的颜色，分别给{layer_names}。'


            messages = [ChatMessage(
                role="user",
                content=message_content
            )]
            handler = ChunkPrintHandler()
            a = spark.generate([messages], callbacks=[handler])
            print(a.generations[0][0].text)
            color_dict = {}

            # 使用正则表达式提取颜色代码和对应的图层名称
            pattern = r"\d+\.\s*([\u4e00-\u9fa5a-zA-Z0-9]+)[：:：\s-]+\s*#([A-Fa-f0-9]{6})"
            matches = re.findall(pattern, a.generations[0][0].text)

            # 遍历匹配结果并填充字典
            for match in matches:
                layer_name, hex_color = match
                color_dict[layer_name] = f'#{hex_color}'

            if color_dict == {}:
                raise ValueError("没有提取到颜色信息。")

            return color_dict

        except Exception as e:
            print(e)
            return {}
        
    def ai_mapping(self,color_dict,poly=None,line=None,point=None):
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        legend_handles = []

        if poly is not None:
            sorted_poly = sorted(poly.items(), key=lambda item: item[1]['area'], reverse=True)
            
            for i, (key, value) in enumerate(sorted_poly):
                base_layer_name_match = re.match(r"([^\d.]+)", key.replace("_曹杨新村街道", ""))
                if base_layer_name_match:
                    base_layer_name = base_layer_name_match.group(1)
                else:
                    base_layer_name = key


                if '曹杨新村街道.shp' == key:
                    alpha = 0.75
                else: 
                    alpha = 1
                gdf = value['data']
                color = color_dict[base_layer_name]  # 按排序顺序分配颜色
                legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道" 和 ".shp"
                gdf.plot(ax=ax, color=color, edgecolor='none', linewidth=0.5, alpha=alpha, label=legend_label)
                legend_handles.append(Polygon([[0, 0], [1, 1], [1, 0]], closed=True, edgecolor='black', facecolor=color, alpha=alpha, linewidth=0.5, label=legend_label,))
        
        if line is not None:
            # print(enumerate(line))
            for i, (key, value) in enumerate(line.items()):
                gdf = value['data']
                
                base_layer_name_match = re.match(r"([^\d.]+)", key.replace("_曹杨新村街道", ""))
                if base_layer_name_match:
                    base_layer_name = base_layer_name_match.group(1)
                else:
                    base_layer_name = key
                color = color_dict[base_layer_name]

                # 设置样式宽度
                if '河流' in key:
                    linewidth = 4.0
                elif '道路' in key:
                    linewidth = 2
                else:
                    linewidth = 0.5
                legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道" 和 ".shp"
                gdf.plot(ax=ax, color=color, edgecolor='none', linewidth=linewidth, label=legend_label)
                legend_handles.append(Line2D([0], [0], marker='_', color=color, label=legend_label, linewidth=linewidth, markerfacecolor=color))

        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('black')
            spine.set_linewidth(2)

        # 隐藏所有坐标轴的文字和刻度
        ax.xaxis.set_ticks([])  # 这行代码将 x 轴的所有刻度设置为空，因此不会显示任何刻度线。
        ax.yaxis.set_ticks([])  # 这行代码将 y 轴的所有刻度设置为空，因此不会显示任何刻度线。
        ax.xaxis.set_tick_params(labelbottom=False)  # 这行代码禁用了 x 轴下方的刻度标签，因此不会显示任何标签文字。
        ax.yaxis.set_tick_params(labelleft=False)  # 这行代码禁用了 y 轴左侧的刻度标签，因此不会显示任何标签文字。


        plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文
        plt.rcParams['axes.unicode_minus']=False   # 用来正常显示负号
        
        plt.title(self.map_name, fontsize=24)

        # 显示图例
        legend = plt.legend(handles=legend_handles, loc='lower right', title='图例')
        legend.get_title().set_fontsize('x-large') 
                
        # 设置图例框的背景色
        frame = legend.get_frame() 
        frame.set_edgecolor('black')  # 设置图例框背景色
        frame.set_linewidth(1)

        # 绘制每个 Shapefile
        plt.show()



    def mapping(self,map_name,colors,poly=None,line=None,point=None):
        # Plot the color palette
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        legend_handles = []

            
        if poly is not None:
            sorted_poly = sorted(poly.items(), key=lambda item: item[1]['area'], reverse=True)
            for i, (key, value) in enumerate(sorted_poly):
                # print(key)
                if '曹杨新村街道.shp' == key:
                    alpha = 0.75
                else: 
                    alpha = 1
                gdf = value['data']
                color = colors[i]  # 按排序顺序分配颜色
                legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道" 和 ".shp"
                gdf.plot(ax=ax, color=color, edgecolor='none', linewidth=0.5, alpha=alpha, label=legend_label)
                legend_handles.append(Polygon([[0, 0], [1, 1], [1, 0]], closed=True, edgecolor='black', facecolor=color, alpha=alpha, linewidth=0.5, label=legend_label,))

        if line is not None:
            # print(enumerate(line))
            for i, (key, value) in enumerate(line.items()):
                gdf = value['data']
                color = colors[i+len(poly)]  # 按排序顺序分配颜色
                # 设置样式宽度
                if '河流' in key:
                    linewidth = 4.0
                elif '道路' in key:
                    linewidth = 2
                else:
                    linewidth = 0.5
                legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道" 和 ".shp"
                gdf.plot(ax=ax, color=color, edgecolor='none', linewidth=linewidth, label=legend_label)
                legend_handles.append(Line2D([0], [0], marker='_', color=color, label=legend_label, linewidth=linewidth, markerfacecolor=color))



        if point is not None:
            hospital_image = Image.open(r'D:\4\demo\ai地图\pics\hospital (1).png')
            school_image = Image.open(r'D:\4\demo\ai地图\pics\school (2).png')
            # todo: 应该 resize
            def add_icon(ax, xy, image, zoom=0.6):
                imagebox = OffsetImage(image, zoom=zoom)
                ab = AnnotationBbox(imagebox, xy,
                                    xybox=(0, 0),
                                    xycoords='data',
                                    boxcoords="offset points",
                                    pad=0,
                                    frameon=False)
                ax.add_artist(ab)
                
            for i, (key, value) in enumerate(point.items()):
                    gdf = value['data']
                    # 设置样式宽度
                    if 'hospital' in key:
                        for x, y in zip(gdf.geometry.x, gdf.geometry.y):
                            add_icon(ax, (x, y), hospital_image, zoom=0.1)
                    elif 'school' in key:
                        for x, y in zip(gdf.geometry.x, gdf.geometry.y):
                            add_icon(ax, (x, y), school_image, zoom=0.1)
                    elif 'label' in key:
                        for name, x, y in zip(gdf.name, gdf.geometry.x, gdf.geometry.y):
                            plt.annotate(f'{name}', (x, y), textcoords="offset points", xytext=(0,0), ha='center', fontsize=8)
                    else:
                        print(key)
                        
            #         legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道" 和 ".shp"
            #         gdf.plot(ax=ax, color=color, edgecolor='none', linewidth=linewidth, label=legend_label)
            #         legend_handles.append(Line2D([0], [0], marker='_', color=color, label=legend_label, linewidth=linewidth, markerfacecolor=color))
        
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(colors[1])
            spine.set_linewidth(2)

        # 隐藏所有坐标轴的文字和刻度
        ax.xaxis.set_ticks([])  # 这行代码将 x 轴的所有刻度设置为空，因此不会显示任何刻度线。
        ax.yaxis.set_ticks([])  # 这行代码将 y 轴的所有刻度设置为空，因此不会显示任何刻度线。
        ax.xaxis.set_tick_params(labelbottom=False)  # 这行代码禁用了 x 轴下方的刻度标签，因此不会显示任何标签文字。
        ax.yaxis.set_tick_params(labelleft=False)  # 这行代码禁用了 y 轴左侧的刻度标签，因此不会显示任何标签文字。


        plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文
        plt.rcParams['axes.unicode_minus']=False   # 用来正常显示负号
        
        plt.title(map_name, fontsize=24)

        # 显示图例
        legend = plt.legend(handles=legend_handles, loc='lower right', title='图例')
        legend.get_title().set_fontsize('x-large') 
                
        # 设置图例框的背景色
        frame = legend.get_frame() 
        frame.set_edgecolor(colors[1])  # 设置图例框背景色
        frame.set_linewidth(1)

        # 绘制每个 Shapefile
        plt.show()
        




    
if __name__ == "__main__":
    # AImapping(polygons=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],lines=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],points=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],name='add')
    # AImapping(polygons=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],lines=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],points=[r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp'],name='add')
    # a = AImapping('曹杨新村街道',r"D:\4\demo\ai地图\pics\2.jpg",r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp',
    #               r'D:\4\demo\ai地图\shp\河流_曹杨新村街道.shp', 
    #               r'D:\4\demo\ai地图\shp\曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\公园绿地_曹杨新村街道.shp',
    #               r'D:\4\demo\ai地图\shp\道路_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\湖泊_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\非住宅2_曹杨新村街道.shp', 
    #               r'D:\4\demo\ai地图\geojson\hospital_data.geojson',r'D:\4\demo\ai地图\geojson\school_data.geojson',
    #               r'D:\4\demo\ai地图\geojson\label_data.geojson')
    
    # a = AImapping('曹杨新村街道',r"乡村",r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp',
    #             r'D:\4\demo\ai地图\shp\河流_曹杨新村街道.shp', 
    #             r'D:\4\demo\ai地图\shp\曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\公园绿地_曹杨新村街道.shp',
    #             r'D:\4\demo\ai地图\shp\道路_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\湖泊_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\非住宅_曹杨新村街道.shp', 
    #             r'D:\4\demo\ai地图\geojson\hospital_data.geojson',r'D:\4\demo\ai地图\geojson\school_data.geojson',
    #             r'D:\4\demo\ai地图\geojson\label_data.geojson')
    
    AImapping('曹杨新村街道',r"乡村",r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp',
                r'D:\4\demo\ai地图\shp\河流_曹杨新村街道.shp', 
                r'D:\4\demo\ai地图\shp\曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\住宅_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\公园绿地_曹杨新村街道.shp',
                r'D:\4\demo\ai地图\shp\道路_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\湖泊_曹杨新村街道.shp', r'D:\4\demo\ai地图\shp\非住宅_曹杨新村街道.shp', 
                r'D:\4\demo\ai地图\geojson\hospital_data.geojson',r'D:\4\demo\ai地图\geojson\school_data.geojson',
                r'D:\4\demo\ai地图\geojson\label_data.geojson')
    
