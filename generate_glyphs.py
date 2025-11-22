#!/usr/bin/env python3
import os
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

# -------------------------------
# 設定
# -------------------------------
FONT_URL = "https://github.com/satsuyako/YomogiFont/raw/refs/heads/ver3.00/fonts/ttf/Yomogi-Regular.ttf"
FONT_FILE = "Yomogi-Regular.ttf"
OUTPUT_DIR = Path("Pack/texts/ja_JP/font")
IMG_SIZE = 64      # 1文字のサイズ
GRID_SIZE = 16     # 1ページの横・縦文字数

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
# フォント取得
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
# ページ単位 PNG 生成
# -------------------------------
def generate_glyph_page(chars, page_index):
    page_img = Image.new("RGBA", (GRID_SIZE*IMG_SIZE, GRID_SIZE*IMG_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(page_img)
    for idx, char in enumerate(chars):
        x = (idx % GRID_SIZE) * IMG_SIZE
        y = (idx // GRID_SIZE) * IMG_SIZE
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
    filename = OUTPUT_DIR / f"glyph_page_{page_index:02d}.png"
    page_img.save(filename)
    print(f"Generated {filename}")

# -------------------------------
# 文字をページに分割して描画
# -------------------------------
page_chars = []
page_index = 0
for i, val in enumerate(LIST):
    if val < 0:
        char = D8[0]  # -1はD8の最初の文字
    else:
        char = chr(val)
    page_chars.append(char)
    if len(page_chars) == GRID_SIZE*GRID_SIZE:
        generate_glyph_page(page_chars, page_index)
        page_chars = []
        page_index += 1

# 最後のページ（余り文字）
if page_chars:
    generate_glyph_page(page_chars, page_index)

print("All glyph pages generated successfully.")
