// deno run --allow-net --allow-write --allow-read generate_glyphs.ts

import { Canvas, registerFont } from "https://deno.land/x/gfx_canvas@0.4.0/mod.ts";
import { ensureDir } from "https://deno.land/std/fs/mod.ts";

// Pack ディレクトリ
const RP_DIR = "Pack";
const FONT_DIR = `${RP_DIR}/font`;
await ensureDir(FONT_DIR);

const IMG_SIZE = 64;

// ASCII + d8 文字列
const d8 = `ÀÁÂÈÊËÍÓÔÕÚßãõğİıŒœŞşŴŵžȇ§© !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_\`abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑªº¿®¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αβΓπΣσμτΦΘΩδ∞∅∈∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ `;

// Google Fonts Kosugi Maru を直接取得
const fontUrl = "https://github.com/google/fonts/raw/main/ofl/kosugimaru/KosugiMaru-Regular.ttf";
const fontData = await fetch(fontUrl).then(r => r.arrayBuffer());
const fontPath = `${FONT_DIR}/KosugiMaru-Regular.ttf`;
await Deno.writeFile(fontPath, new Uint8Array(fontData));
registerFont(fontPath, { family: "Kosugi Maru" });

// 描画関数
function drawGlyph(canvas: Canvas, char: string) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, IMG_SIZE, IMG_SIZE);
  ctx.fillStyle = "#ffffff";
  ctx.font = `${IMG_SIZE}px "Kosugi Maru", sans-serif`;
  ctx.textBaseline = "top";
  ctx.fillText(char, 0, 0);
}

// PNG 保存
async function saveGlyph(char: string, filename: string) {
  const canvas = new Canvas(IMG_SIZE, IMG_SIZE);
  drawGlyph(canvas, char);
  await Deno.writeFile(filename, canvas.toBuffer("image/png"));
}

// 文字リスト
const LIST = [-1, ...Array(256).keys()].filter(i => i < 0xd8 || 0xf5 < i);

for (const i of LIST) {
  const char = i < 0 ? d8[i] : String.fromCodePoint(i);
  const filename = `${FONT_DIR}/glyph_${i.toString(16).padStart(2,"0")}.png`;
  await saveGlyph(char, filename);
}

console.log("Pack/ glyph PNGs generated successfully.");
