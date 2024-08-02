import geopandas as gpd
import matplotlib.pyplot as plt
import os
import random
from matplotlib.colors import to_hex
from matplotlib import cm
from PIL import Image
import numpy as np
import matplotlib.colors as mcolors
from sklearn.cluster import KMeans
from collections import Counter
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Patch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def generate_color_from_img(image_path: str):
    # Read the image
    image = Image.open(image_path)
    image = image.convert('RGB')
    image_np = np.array(image)

    # Resize the image to reduce computation
    image_small = image.resize((100, 100))
    image_small_np = np.array(image_small)

    # Reshape image data to a 2D array
    pixels = image_small_np.reshape(-1, 3)
    # Perform KMeans clustering
    n_colors = 7  # Number of colors to extract
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
    return sorted_colors_hex

def generate_random_color():
    return to_hex(cm.gist_rainbow(random.random()))

def create_map(shapefile_dir, colors, geojson_data, icon_path):
    shapefiles = [
        '房屋_曹杨新村街道.shp', '河流_曹杨新村街道.shp', '曹杨新村街道.shp', 
        '住宅_曹杨新村街道.shp', '公园绿地_曹杨新村街道.shp', '道路_曹杨新村街道.shp', 
        '湖泊_曹杨新村街道.shp', '非住宅2_曹杨新村街道.shp', '非住宅_曹杨新村街道.shp'
    ]

    # 颜色映射
    color_mapping = {
        '曹杨新村街道.shp': colors[0],  
        '房屋_曹杨新村街道.shp': colors[1],  # 接近绿色
        '住宅_曹杨新村街道.shp': colors[2],  # 接近绿色
        '河流_曹杨新村街道.shp': '#1f78b4',  # 蓝色系
        '湖泊_曹杨新村街道.shp': '#a6cee3',  # 蓝色系
        '道路_曹杨新村街道.shp': colors[3],  # 其他颜色
        '非住宅2_曹杨新村街道.shp': colors[4],  # 其他颜色
        '非住宅_曹杨新村街道.shp': colors[5],  # 其他颜色
        '公园绿地_曹杨新村街道.shp': colors[6],  # 接近绿色
    }

    # 透明度映射
    alpha_mapping = {
        '曹杨新村街道.shp': 0.6,
        '房屋_曹杨新村街道.shp': 1,
        '住宅_曹杨新村街道.shp': 1,
        '河流_曹杨新村街道.shp': 1,
        '湖泊_曹杨新村街道.shp': 1,
        '道路_曹杨新村街道.shp': 1,
        '非住宅2_曹杨新村街道.shp': 1,
        '非住宅_曹杨新村街道.shp': 1,
        '公园绿地_曹杨新村街道.shp': 1,
    }

    shapefile_dict = {}
    for shapefile in shapefiles:
        gdf = gpd.read_file(os.path.join(shapefile_dir, shapefile))
        color = color_mapping.get(shapefile, '#000000')  # 默认颜色为黑色
        alpha = alpha_mapping.get(shapefile, 1.0)  # 默认透明度为1.0（不透明）
        shapefile_dict[shapefile] = {'data': gdf, 'color': color, 'alpha': alpha}

    # 指定绘图顺序
    plot_order = list(shapefile_dict.keys())
    plot_order.remove('曹杨新村街道.shp')
    plot_order.insert(0, '曹杨新村街道.shp')  # 将其放到最上层

    # 创建地图图形
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # 绘制每个 Shapefile
    legend_handles = []
    for key in plot_order:
        value = shapefile_dict[key]
        gdf = value['data']
        color = value['color']
        alpha = value['alpha']
        
        # 设置样式宽度
        if '河流' in key:
            linewidth = 4.0
        elif '道路' in key:
            linewidth = 2
        else:
            linewidth = 0.5


        legend_label = key.replace('_曹杨新村街道', '').replace('.shp', '')  # 删除 "_曹杨新村街道"
        gdf.plot(ax=ax, color=color, edgecolor='black', alpha=alpha, linewidth=linewidth, label=legend_label)
        
        legend_handles.append(Line2D([0], [0], marker='o', color='w', label=legend_label,
                                     markerfacecolor=color, markersize=10))
    
    # ax.annotate('Local max', xy=(-6759, 700), xytext=(-6759, 700), fontsize=20, color='black',bbox=dict(facecolor='white', alpha=0.5))
    # 添加图标的函数
    def add_icon(ax, xy, image, zoom=0.6):
        imagebox = OffsetImage(image, zoom=zoom)
        ab = AnnotationBbox(imagebox, xy,
                            xybox=(0, 0),
                            xycoords='data',
                            boxcoords="offset points",
                            pad=0,
                            frameon=False)
        ax.add_artist(ab)

# 为每个点添加图标
    icon_image = Image.open(r'D:\4\demo\ai地图\resized_icon.png')
    # add_icon(ax, (-6759, 700), icon_image)

    # 添加 GeoJSON 点
    if geojson_data:
        geojson_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
        # 绘制点时添加图标
        # for x, y in zip(geojson_gdf.geometry.x, geojson_gdf.geometry.y):
            # ax.scatter(img, extent=(x-0.00000001, x+0.0000001, y-0.00000001, y+0.0000001), aspect='auto', zorder=10)
        ax.scatter(geojson_gdf.geometry.x, geojson_gdf.geometry.y, s=50, c='red', marker='o', zorder=10, label='GeoJSON Points')
        # 加图例
        polygon1 = Polygon([[0, 0], [1, 2], [2, 0]], closed=True, color='blue', label='polygon',)
        legend_handles.append(polygon1)
        # legend_handles.append(Line2D([0], [0], linestyle='-', color="b", label='Points',
        #                              markerfacecolor='red', markersize=10))
    
    # # 调整图标大小
    # img = Image.open(icon_path)
    # img = img.resize((20, 20), Image.LANCZOS)  # 调整图标大小，(20, 20) 可以调整为合适的尺寸
    # img.save('resized_icon.png')  # 保存调整大小后的图标

    # if geojson_data:
    #     geojson_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    # # 绘制GeoJSON点并添加图标
    #     for x, y in zip(geojson_gdf.geometry.x, geojson_gdf.geometry.y):
    #         img = plt.imread('resized_icon.png')
    #         imagebox = OffsetImage(img, zoom=0.1)  # 调整zoom参数以控制图标大小
    #         ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    #         ax.add_artist(ab)

    # # 设置绘图范围（根据需要调整）
    # ax.set_xlim(gdf.geometry.x.min() - 1, gdf.geometry.x.max() + 1)
    # ax.set_ylim(gdf.geometry.y.min() - 1, gdf.geometry.y.max() + 1)
    # 隐藏坐标轴

    # ax.set_axis_off()

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor(colors[1])
        spine.set_linewidth(2)


    # 隐藏所有坐标轴的文字和刻度
    ax.xaxis.set_ticks([])  # 这行代码将 x 轴的所有刻度设置为空，因此不会显示任何刻度线。
    ax.yaxis.set_ticks([])  # 这行代码将 y 轴的所有刻度设置为空，因此不会显示任何刻度线。
    ax.xaxis.set_tick_params(labelbottom=False)  # 这行代码禁用了 x 轴下方的刻度标签，因此不会显示任何标签文字。
    ax.yaxis.set_tick_params(labelleft=False)  # 这行代码禁用了 y 轴左侧的刻度标签，因此不会显示任何标签文字。


    # 添加标题
    # ax.set_title('风格迁移', fontsize=15)

    # ax.set_facecolor(colors[1])  # 设置背景色为指定颜色
    # fig.patch.set_alpha(0.2)



    plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文
    plt.rcParams['axes.unicode_minus']=False   # 用来正常显示负号
    
    # 显示地图
    legend = plt.legend(handles=legend_handles, loc='lower right', title='图例')
    legend.get_title().set_fontsize('x-large') 
            
    # 设置图例框的背景色
    frame = legend.get_frame() 
    frame.set_edgecolor(colors[1])  # 设置图例框背景色
    frame.set_linewidth(1)

    
    
    plt.show()


if __name__ == '__main__':
    # 生成颜色调色板
    image_path = r"D:\4\demo\ai地图\7.jpg"
    colors = generate_color_from_img(image_path)
    print(colors)

    # 定义 GeoJSON 数据
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            # {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6759, 700]}, "properties": {"name": "曹杨第二中学"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6169, 855]}, "properties": {"name": "朝春中心小学"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6688, 240]}, "properties": {"name": "曹杨二中附属学校（分部）"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6295, 247]}, "properties": {"name": "曹杨二中附属学校"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5849, 449]}, "properties": {"name": "兴陇中学"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5663, 510]}, "properties": {"name": "沙田学校"}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6078, 247]}, "properties": {"name": "曹杨新村第六小学"}}
        ]
    }

    

    icon_path = r"D:\4\demo\模仿test3\img\location.png"  # 替换为你的图标路径
    create_map('D:/4/demo/ai地图', colors, geojson_data, icon_path)