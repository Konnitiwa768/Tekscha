#!/usr/bin/env python3
import os
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

# -------------------------------
# 設定
# -------------------------------
FONT_URL = "https://github.com/satsuyako/YomogiFont/raw/refs/heads/ver3.00/fonts/ttf/Yomogi-Regular.ttf"
FONT_FILE = "KosugiMaru-Regular.ttf"
OUTPUT_DIR = Path("Pack/texts/ja_JP/fon ")
IMG_SIZE = 64  # 1文字の画像サイズ

# ASCII + D8文字列
D8 = ("ÀÁÂÈÊËÍÓÔÕÚßãõğİıŒœŞşŴŵžȇ§© "
      "!\"#$%&'()*+,-./0123456789:;<=>?@"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
      "abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑ"
      "ªº¿®¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼"
      "╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀"
      "αβΓπΣσμτΦΘΩδ∞∅∈∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ")

# 描画する文字リスト
LIST = [-1] + list(range(256))
LIST = [i for i in LIST if i < 0xd8 or i > 0xf5]

# -------------------------------
# 出力フォルダ作成
# -------------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# フォントファイルをダウンロード
# -------------------------------
if not os.path.exists(FONT_FILE):
    print(f"Downloading font from {FONT_URL}...")
    r = requests.get(FONT_URL)
    r.raise_for_status()
    with open(FONT_FILE, "wb") as f:
        f.write(r.content)
    print(f"Font saved to {FONT_FILE}")
else:
    print(f"Font {FONT_FILE} already exists.")

# -------------------------------
# フォント読み込み
# -------------------------------
font = ImageFont.truetype(FONT_FILE, IMG_SIZE)

# -------------------------------
# PNG生成関数
# -------------------------------
def generate_glyph(char, filename):
    img = Image.new("RGBA", (IMG_SIZE, IMG_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), char, font=font, fill=(255, 255, 255, 255))
    img.save(filename)

# -------------------------------
# 文字描画ループ
# -------------------------------
for i in LIST:
    if i < 0:
        char = D8[0]  # -1はD8の最初の文字
    else:
        char = chr(i)
    hex_name = f"{(i + 256 if i < 0 else i):02x}"
    filename = OUTPUT_DIR / f"glyph_{hex_name}.png"
    generate_glyph(char, filename)
    print(f"Generated {filename}")

print("All glyph PNGs generated successfully.")
