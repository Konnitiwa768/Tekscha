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
TOTAL_PAGES = 256  # 生成するページ数

# ASCII + 拡張文字 D8
D8 = ("ÀÁÂÈÊËÍÓÔÕÚßãõğİıŒœŞşŴŵžȇ§© "
      "!\"#$%&'()*+,-./0123456789:;<=>?@"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
      "abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑ"
      "ªº¿®¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼"
      "╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀"
      "αβΓπΣσμτΦΘΩδ∞∅∈∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ")

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
    filename = OUTPUT_DIR / f"glyph_{page_index:02X}.png"  # 16進数形式
    page_img.save(filename)
    print(f"Generated {filename}")

# -------------------------------
# 文字リスト作成
# -------------------------------
LIST = [-1] + list(range(256))           # -1はD8先頭文字
LIST = [i for i in LIST if i < 0xd8 or i > 0xf5]  # 除外範囲
LIST += list(D8)                         # D8文字を追加

CHARS_PER_PAGE = GRID_SIZE * GRID_SIZE
REQUIRED_LEN = TOTAL_PAGES * CHARS_PER_PAGE

# 足りない分は空白で埋める
full_list = []
for val in LIST:
    if val == -1:
        full_list.append(D8[0])
    elif isinstance(val, int):
        full_list.append(chr(val))
    else:
        full_list.append(val)

while len(full_list) < REQUIRED_LEN:
    full_list.append(" ")

# -------------------------------
# 文字をページに分割して描画
# -------------------------------
for page_index in range(TOTAL_PAGES):
    start = page_index * CHARS_PER_PAGE
    end = start + CHARS_PER_PAGE
    page_chars = full_list[start:end]
    generate_glyph_page(page_chars, page_index)

print("All 256 glyph pages (00-FF) generated successfully.")
