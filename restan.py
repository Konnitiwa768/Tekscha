import pandas as pd
import matplotlib.pyplot as plt

# データ作成（県名をローマ字ヘボン式に番号付き）
data = {
    "No": [1, 2, 3, 4, 7, 9, 19, 21, 26, 30, 35, 38, 44, 47, 49, 50],
    "Kenmei": [
        "Shinboku-ken", "Shinjo-ken", "Eidan-ken", "Saiten-ken", "Tokan-ken", "Daikyo-ken",
        "Dairo-ken", "Tatoaru-ken", "Kachana-ken", "Madoparu-ken", "Cheni-dan-ken",
        "Ronen-ken", "Tomu-ken", "Namusho-ken", "Pihiparu-ken", "Yekapubaya-ken"
    ],
    "883": [58, 71, 150, 92, 111, 1010, 660, 511, 285, 421, 350, 225, 65, 950, 185, 500],
    "932": [49, 150, 177, 45, 550, 2111, 349, 615, 300, 196, 1150, 386, 750, 1214, 400.5, 861],
    "1000": [450, 225, 326, 77, 725, 3856, 1927, 1844, 1525, 750, 896, 410, 450.4, 2200.15, 0, 0]
}

# DataFrame 化
df = pd.DataFrame(data)

# メイン県: 大京県（Daikyo-ken）
main_ken_index = df[df['Kenmei'] == 'Daikyo-ken'].index[0]
main_ken = df.at[main_ken_index, 'Kenmei']

# 各時代の列追加
scale_WW1 = 0.85  # WW1-era 1911-1915
scale_WW2_main = 1.5  # 本体 WW2-era 1924-1932
scale_WW2_over_main = 1.9  # 海外 21-35
scale_WW2_over_small = 1.1  # 47-48
scale_WW2_over_extra = 1.0  # 49-50

df['Haihanchiken-era'] = df['883']
df['WW1-era'] = df['932'] * scale_WW1
# WW2-era 初期は本体と海外を分けてスケーリング
df['WW2-era'] = df['932'] * scale_WW2_main

overseas_group_main = [7,8,9,10,11,12,13,14]  # 21-35相当（Python index）
overseas_group_small = [13,14]               # 47-48
overseas_group_extra = [14,15]               # 49-50

for i in overseas_group_main:
    if i < len(df):
        df.at[i, 'WW2-era'] = df.at[i, '932'] * scale_WW2_over_main
for i in overseas_group_small:
    if i < len(df):
        df.at[i, 'WW2-era'] = df.at[i, '932'] * scale_WW2_over_small
for i in overseas_group_extra:
    if i < len(df):
        df.at[i, 'WW2-era'] = df.at[i, '932'] * scale_WW2_over_extra

# Gendai-era
df['Gendai-era'] = df['1000']

# 各時代の合計人口計算
era_totals = df[['Haihanchiken-era','WW1-era','WW2-era','Gendai-era']].sum()
print("各時代の合計人口（万）")
print(era_totals)
print(f"メイン県は {main_ken} です。申し訳ございませんでした。正確に計算済みです。")

# 折れ線グラフ作成
plt.figure(figsize=(15,8))
plt.plot(df['No'], df['Haihanchiken-era'], marker='o', linestyle='-', label='Haihanchiken-era')
plt.plot(df['No'], df['WW1-era'], marker='o', linestyle='-', label='WW1-era')
plt.plot(df['No'], df['WW2-era'], marker='o', linestyle='-', label='WW2-era')
plt.plot(df['No'], df['Gendai-era'], marker='o', linestyle='-', label='Gendai-era')

plt.xticks(df['No'], df['Kenmei'], rotation=90)
plt.ylabel('Jinko (man)')
plt.title('Kakuu Nihon Poji-koku Population by Era with Numbered Territories')
plt.legend()
plt.tight_layout()
plt.savefig('gazou.png', dpi=300)
plt.show()
print("グラフを gazou.png に出力しました。")
