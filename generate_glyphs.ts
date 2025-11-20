// deno run --allow-net --allow-write --allow-read generate_glyphs.ts

import { createCanvas, registerFont, CanvasRenderingContext2D } from "https://deno.land/x/canvas@1.0.0/mod.ts";
import { ensureDir } from "https://deno.land/std/fs/mod.ts";

// RP ディレクトリ
const RP_DIR = "RP";
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

// canvas に描画する関数
function drawGlyph(ctx: CanvasRenderingContext2D, char: string) {
  ctx.clearRect(0, 0, IMG_SIZE, IMG_SIZE);
  ctx.fillStyle = "#ffffff";
  ctx.font = `${IMG_SIZE}px "Kosugi Maru", sans-serif`;
  ctx.textBaseline = "top";
  ctx.fillText(char, 0, 0);
}

// PNG 保存
async function saveGlyph(char: string, filename: string) {
  const canvas = createCanvas(IMG_SIZE, IMG_SIZE);
  const ctx = canvas.getContext("2d");
  drawGlyph(ctx, char);
  await Deno.writeFile(filename, canvas.toBuffer("image/png"));
}

// 256 文字ループ
const LIST = [-1, ...Array(256).keys()].filter(i => i < 0xd8 || 0xf5 < i);

for (const i of LIST) {
  const char = i < 0 ? d8[i] : String.fromCodePoint(i);
  const filename = `${FONT_DIR}/glyph_${i.toString(16).padStart(2,"0")}.png`;
  await saveGlyph(char, filename);
}

// manifest.json
await Deno.writeTextFile(`${RP_DIR}/manifest.json`, JSON.stringify({
  name: "font resource pack",
  description: "Generated glyphs",
  version: [1, 0, 0]
}, null, 2));

// pack_icon.png
const iconCanvas = createCanvas(IMG_SIZE, IMG_SIZE);
const iconCtx = iconCanvas.getContext("2d");
iconCtx.fillStyle = "#ffffff";
iconCtx.font = `${IMG_SIZE/2}px "Kosugi Maru", sans-serif`;
iconCtx.textAlign = "center";
iconCtx.textBaseline = "middle";
iconCtx.fillText("Aa", IMG_SIZE/2, IMG_SIZE/2);
await Deno.writeFile(`${RP_DIR}/pack_icon.png`, iconCanvas.toBuffer("image/png"));

console.log("RP/ glyph pack generated");
