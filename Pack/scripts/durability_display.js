import { world, system } from "@minecraft/server";

const LOW_DURABILITY_RATIO = 0.1; // 10%以下で警告
const UPDATE_INTERVAL = 20; // 1秒ごと

system.runInterval(() => {
  for (const player of world.getPlayers()) {
    const inv = player.getComponent("minecraft:inventory")?.container;
    const equip = player.getComponent("minecraft:equipment_inventory");
    if (!inv || !equip) continue;

    const data = [];

    // メインハンド
    const main = inv.getItem(player.selectedSlot);
    if (main?.getComponent("minecraft:durability")) {
      const d = main.getComponent("minecraft:durability");
      const now = d.maxDurability - d.damage;
      const ratio = now / d.maxDurability;
      data.push({ name: "Main", now, max: d.maxDurability, ratio });
    }

    // 装備スロット
    const slots = [
      ["Head", "head"],
      ["Chest", "chest"],
      ["Legs", "legs"],
      ["Boots", "feet"]
    ];
    for (const [label, slot] of slots) {
      const item = equip.getEquipment(slot);
      if (item?.getComponent("minecraft:durability")) {
        const d = item.getComponent("minecraft:durability");
        const now = d.maxDurability - d.damage;
        const ratio = now / d.maxDurability;
        data.push({ name: label, now, max: d.maxDurability, ratio });
      }
    }

    // テキスト生成
    let text = "§l§f[Durability]\n";
    for (const d of data) {
      const color = d.ratio <= LOW_DURABILITY_RATIO
        ? (Math.floor(Date.now() / 500) % 2 === 0 ? "§c" : "§4") // 点滅
        : "§7";
      text += `${color}${d.name}: §f${d.now}/${d.max}\n`;
    }
    if (data.length === 0) text += "§8(耐久値なし)";

    // スコアボード代替でtitle表示（HUD固定に近い位置）
    player.onScreenDisplay.setTitle(text, { fadeInDuration: 0, stayDuration: 25, fadeOutDuration: 0 });
  }
}, UPDATE_INTERVAL);
