import os
import math
import numpy as np
from PIL import Image

INPUT_PATH = "SP5.png"
OUTPUT_DIR = "Pack4/textures/environment/overworld_cubemap"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 出力順序（Bedrock対応）
FACES = [
    ("cubemap_0.png", 0, 0),            # north
    ("cubemap_3.png", math.pi / 2, 0),  # east
    ("cubemap_2.png", math.pi, 0),      # south
    ("cubemap_1.png", -math.pi / 2, 0), # west
    ("cubemap_4.png", 0, -math.pi / 2), # up
    ("cubemap_5.png", 0, math.pi / 2),  # down
]

def clamp(x, a, b):
    return max(a, min(b, x))

def direction_to_uv(x, y, z):
    lon = math.atan2(x, z)
    lat = math.asin(y)
    u = (lon / math.pi + 1) / 2
    v = 0.5 - lat / math.pi
    return u, v

def render_face(img, yaw, pitch, size):
    w, h = img.size
    src = np.asarray(img).astype(np.float32) / 255.0
    face = np.zeros((size, size, 3), dtype=np.float32)

    for i in range(size):
        for j in range(size):
            nx = 2 * (j + 0.5) / size - 1
            ny = 2 * (i + 0.5) / size - 1
            vec = np.array([nx, ny, -1.0])
            x, y, z = vec / np.linalg.norm(vec)

            cos_y, sin_y = math.cos(yaw), math.sin(yaw)
            xz_x = cos_y * x + sin_y * z
            xz_z = -sin_y * x + cos_y * z

            cos_p, sin_p = math.cos(pitch), math.sin(pitch)
            y2 = cos_p * y - sin_p * xz_z
            z2 = sin_p * y + cos_p * xz_z

            u, v = direction_to_uv(xz_x, y2, z2)
            px = clamp(int(u * (w - 1)), 0, w - 1)
            py = clamp(int(v * (h - 1)), 0, h - 1)
            face[i, j] = src[py, px, :3]

    return Image.fromarray((face * 255).astype(np.uint8))

def main():
    print("Loading:", INPUT_PATH)
    img = Image.open(INPUT_PATH).convert("RGB")
    size = 1024  # 出力サイズ

    for fname, yaw, pitch in FACES:
        print("Rendering", fname)
        face_img = render_face(img, yaw, pitch, size)
        face_img.save(os.path.join(OUTPUT_DIR, fname))

    print("✅ Done. Output folder:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
