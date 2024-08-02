import json

# 定义 GeoJSON 数据
School_Data = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6759, 700]}, "properties": {"name": "曹杨第二中学"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6169, 855]}, "properties": {"name": "朝春中心小学"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6688, 240]}, "properties": {"name": "曹杨二中附属学校（分部）"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6295, 247]}, "properties": {"name": "曹杨二中附属学校"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5849, 449]}, "properties": {"name": "兴陇中学"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5663, 510]}, "properties": {"name": "沙田学校"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6078, 247]}, "properties": {"name": "曹杨新村第六小学"}},
    ]
}

Hospital_Data = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6485, 868]}, "properties": {"name": "普陀区中心医院"}}
    ]
}

Label_Data = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6758, 1032]}, "properties": {"name": "曹杨三村"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6233, 1144]}, "properties": {"name": "曹杨二村"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5963, 987]}, "properties": {"name": "曹杨七村"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5337, 755]}, "properties": {"name": "中关村公寓"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6355, 160]}, "properties": {"name": "曹杨四村"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-6142, 53]}, "properties": {"name": "曹杨五村"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5860, 894]}, "properties": {"name": "曹杨新村街道"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-5514, 540]}, "properties": {"name": "曹杨六村"}},
    ]
}

# 将数据写入到 GeoJSON 文件
with open('school_data.geojson', 'w', encoding='utf-8') as f:
    json.dump(School_Data, f, ensure_ascii=False, indent=4)

with open('hospital_data.geojson', 'w', encoding='utf-8') as f:
    json.dump(Hospital_Data, f, ensure_ascii=False, indent=4)

with open('label_data.geojson', 'w', encoding='utf-8') as f:
    json.dump(Label_Data, f, ensure_ascii=False, indent=4)

print("GeoJSON 文件已创建")
