import json
from PIL import Image, ImageDraw

# モデル定義
models = {
    "phyle": [
        (0, 0, 8, 4),  # body UV
        (0, 16, 6, 3), # head UV
        (0, 25, 12, 1), # leg1 UV
        (0, 27, 12, 1), # leg2 UV
        (0, 29, 12, 1), # leg3 UV
        (0, 31, 12, 1), # leg4 UV
        (0, 33, 12, 1), # leg5 UV
        (0, 35, 12, 1)  # leg6 UV
    ],
    "troivjuer": [
        (0, 0, 4, 8), # body
        (0, 10, 3, 4), # segment1
        (0, 18, 2, 4), # segment2
        (0, 24, 1, 3), # segment3
        (0, 28, 2, 2)  # tentacle_tip
    ],
    "nihdun": [
        (0, 0, 4, 4), # core
        (0, 10, 7, 7), # shell1
        (0, 28, 10, 10), # shell2
        (0, 48, 13, 13) # shell3
    ]
}

# 画像サイズ
tex_width, tex_height = 64, 64

for name, boxes in models.items():
    img = Image.new('RGB', (tex_width, tex_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for box in boxes:
        x, y, w, h = box
        draw.rectangle([x, y, x+w, y+h], outline=(0,0,0), fill=(150,150,150))
    img.show(title=name)

# .geo.jsonは指定通りの形式を保存
geo_data = {
    "phyle": {
        "format_version": "1.12.0",
        "minecraft:geometry": [{"description": {"identifier": "geometry.phyle", "texture_width": 64, "texture_height": 64, "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0,1,0]}, "bones": []}]
    },
    "troivjuer": {
        "format_version": "1.12.0",
        "minecraft:geometry": [{"description": {"identifier": "geometry.troivjuer", "texture_width": 64, "texture_height": 64, "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0,1,0]}, "bones": []}]
    },
    "nihdun": {
        "format_version": "1.12.0",
        "minecraft:geometry": [{"description": {"identifier": "geometry.nihdun", "texture_width": 64, "texture_height": 64, "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0,1,0]}, "bones": []}]
    }
}

with open('output_models.json', 'w', encoding='utf-8') as f:
    json.dump(geo_data, f, ensure_ascii=False, indent=2)

print('✅ 画像表示および.geo.json準備完了')
