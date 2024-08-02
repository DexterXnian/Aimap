import geopandas as gpd
import os
import fiona

def find_files(directory, ext='曹杨新村街道.shp'):
    """
    找到指定目录及其所有子目录下的文件，返回文件路径列表。
    """
    file_paths = []
    for root, directories, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(ext):
                file_paths.append(file_path)
    return file_paths


basicCrs = gpd.read_file(r"D:\4\demo\ai地图\shp\曹杨新村街道.shp").crs

for shpfile in find_files(r"D:\4\demo\ai地图\shp"):

    gdf = gpd.read_file(shpfile)
    outputpath = os.path.join(r"D:\4\demo\ai地图\gpkg", os.path.basename(shpfile).replace('_曹杨新村街道.shp', '.gpkg'))
    gdf.to_file(outputpath, driver='GPKG',encoding='utf-8', crs=basicCrs)

if __name__ == '__main__':

    import os
    import geopandas as gpd
    import fiona

    def list_layers(gpkg_path):
        return fiona.listlayers(gpkg_path)

    def combine_gpkg_files(input_folder, output_gpkg):
        # 遍历输入文件夹中的所有 gpkg 文件
        for file_name in os.listdir(input_folder):
            if file_name.endswith('.gpkg'):
                file_path = os.path.join(input_folder, file_name)
                layers = list_layers(file_path)
                
                # 遍历每个 gpkg 文件中的所有图层
                for layer in layers:
                    gdf = gpd.read_file(file_path, layer=layer)
                    # 将图层写入输出的 gpkg 文件中
                    gdf.to_file(output_gpkg, layer=layer, driver="GPKG")
                    print(f"Layer {layer} from {file_name} added to {output_gpkg}")

    # 示例调用
    input_folder = r"D:\4\demo\ai地图\gpkg"
    output_gpkg = r"D:\4\demo\ai地图\gpkg\combined.gpkg"

    combine_gpkg_files(input_folder, output_gpkg)
