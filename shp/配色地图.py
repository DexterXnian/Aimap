import geopandas as gpd
import matplotlib.pyplot as plt
import os
import random
from matplotlib.colors import to_hex
from matplotlib import cm
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import Counter

from sklearn.cluster import KMeans


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


def create_map(shapefile_dir,colors):
    # 设置Shapefile文件路径
    shapefile_dir = 'D:/4/demo/ai地图'

    # 获取目录中所有的Shapefile文件
    shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith('.shp')]

    # print(len(shapefiles))
    random.shuffle(colors)
    shapefile_dict = {}
    for idx, shapefile in enumerate(shapefiles):
        gdf = gpd.read_file(shapefile)
        # color = generate_random_color()
        shapefile_dict[f'Shapefile_{idx + 1}'] = {'data': gdf, 'color': colors[idx % len(colors)]}

    # 创建地图图形
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # 绘制每个 Shapefile
    legend_handles = []
    for key, value in shapefile_dict.items():
        gdf = value['data']
        print(gdf)
        color = value['color']
        gdf.plot(ax=ax, color=color, edgecolor='black', label=key)
        legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', label=key, 
                                        markerfacecolor=color, markersize=10))


    # 隐藏坐标轴
    # ax.set_axis_off()


    # 添加标题
    ax.set_title('田园化风格的地图，每个Shapefile分配不同颜色', fontsize=15)

    plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文
    plt.rcParams['axes.unicode_minus']=False   # 用来正常显示负号
    # 显示地图
    plt.show()


if __name__ == '__main__':
    # create_map('D:/4/demo/ai地图')
    colors = generate_color_from_img(r"D:\4\demo\ai地图\6.jpg")
    print(colors)
    # create_map('D:/4/demo/ai地图',colors)