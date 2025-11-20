#!/usr/bin/env python3
import os
import requests
from PIL import Image, ImageDraw, ImageFont

# Pack ディレクトリ
RP_DIR = "Pack"
FONT_DIR = os.path.join(RP_DIR, "font")
os.makedirs(FONT_DIR, exist_ok=True)

IMG_SIZE = 64

# ASCII + D8 文字列
D8 = ("ÀÁÂÈÊËÍÓÔÕÚßãõğİıŒœŞşŴŵžȇ§© "
      "!\"#$%&'()*+,-./0123456789:;<=>?@"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
      "abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑ"
      "ªº¿®¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼"
      "╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀"
      "αβΓπΣσμτΦΘΩδ∞∅∈∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ")

# Google Fonts Kosugi Maru を直接取得
font_url = "https://github.com/google/fonts/raw/main/ofl/kosugimaru/KosugiMaru-Regular.ttf"
font_path = os.path.join(FONT_DIR, "KosugiMaru-Regular.ttf")

if not os.path.exists(font_path):
    r = requests.get(font_url)
    r.raise_for_status()
    with open(font_path, "wb") as f:
        f.write(r.content)

font = ImageFont.truetype(font_path, IMG_SIZE)

# ASCII + D8 の文字リスト
LIST = [-1] + list(range(256))
LIST = [i for i in LIST if i < 0xd8 or i > 0xf5]

for i in LIST:
    if i < 0:
        CHAR = D8[0]  # -1 は D8 の最初の文字
    else:
        CHAR = chr(i)
    
    HEX = f"{(i + 256 if i < 0 else i):02x}"
    filename = os.path.join(FONT_DIR, f"glyph_{HEX}.png")

    img = Image.new("RGBA", (IMG_SIZE, IMG_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), CHAR, font=font, fill=(255, 255, 255, 255))
    img.save(filename)

print("Pack/font/glyph PNGs generated successfully.")
