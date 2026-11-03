"""
Script untuk menghasilkan gambar visual mockup Dashboard Power BI Eksekutif
Desain: 16:9 High Resolution (1920x1080)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Konfigurasi ukuran gambar 16:9 HD
fig = plt.figure(figsize=(16, 9), dpi=120)
fig.patch.set_facecolor('#F1F5F9') # Soft Gray Background

# 1. Header Banner
ax_header = fig.add_axes([0.04, 0.89, 0.92, 0.08])
ax_header.set_facecolor('#FFFFFF')
for spine in ax_header.spines.values():
    spine.set_color('#E2E8F0')
    spine.set_linewidth(1)
ax_header.set_xticks([])
ax_header.set_yticks([])

# Teks Header
ax_header.text(0.02, 0.65, "SF Restaurant Hygiene & Safety Dashboard", fontsize=17, fontweight='bold', color='#0F172A')
ax_header.text(0.02, 0.25, "Analisis Kepatuhan Sanitasi & Profil Risiko Restoran San Francisco (2014 - 2016)", fontsize=10, color='#64748B')

# Slicer Pill Mockup
slicer_box = patches.FancyBboxPatch((0.78, 0.20), 0.20, 0.60, boxstyle="round,pad=0.02", fc="#F8FAFC", ec="#CBD5E1", lw=1)
ax_header.add_patch(slicer_box)
ax_header.text(0.80, 0.45, "Filter: Semua Tahun & Bulan  ▼", fontsize=9, color='#334155', fontweight='semibold')

# 2. Empat Kartu KPI (Row 1)
kpis = [
    {"title": "TOTAL SESI INSPEKSI", "val": "25,834", "sub": "Dari 6,078 Restoran Unik", "color": "#0F172A", "bar_c": "#2563EB"},
    {"title": "RATA-RATA SKOR KOTA", "val": "91.3", "sub": "Kategori: Good / Excellent", "color": "#10B981", "bar_c": "#10B981"},
    {"title": "TOTAL PELANGGARAN", "val": "40,623", "sub": "86% Risiko Rendah / Sedang", "color": "#0F172A", "bar_c": "#F59E0B"},
    {"title": "% INSPEKSI HIGH RISK", "val": "16.0%", "sub": "Min. 1 pelanggaran berisiko tinggi", "color": "#E11D48", "bar_c": "#E11D48"}
]

card_w = 0.215
gap = 0.02
start_x = 0.04
y_cards = 0.74
card_h = 0.125

for i, kpi in enumerate(kpis):
    cx = start_x + i * (card_w + gap)
    ax_card = fig.add_axes([cx, y_cards, card_w, card_h])
    ax_card.set_facecolor('#FFFFFF')
    for spine in ax_card.spines.values():
        spine.set_color('#E2E8F0')
    ax_card.set_xticks([])
    ax_card.set_yticks([])
    
    # Border aksen atas
    top_bar = patches.Rectangle((0, 0.94), 1, 0.06, transform=ax_card.transAxes, color=kpi["bar_c"])
    ax_card.add_patch(top_bar)
    
    ax_card.text(0.08, 0.70, kpi["title"], fontsize=8.5, fontweight='bold', color='#64748B')
    ax_card.text(0.08, 0.36, kpi["val"], fontsize=20, fontweight='bold', color=kpi["color"])
    ax_card.text(0.08, 0.14, kpi["sub"], fontsize=7.5, color='#94A3B8')

# 3. Visual Kiri: Top 10 Pelanggaran Paling Sering (Bar Chart)
ax_left = fig.add_axes([0.04, 0.12, 0.45, 0.58])
ax_left.set_facecolor('#FFFFFF')
for spine in ax_left.spines.values():
    spine.set_color('#E2E8F0')

violations = [
    "High risk food holding temp",
    "Unclean nonfood surfaces",
    "Foods not protected from contam.",
    "Improper food storage",
    "Wiping cloths not clean/stored",
    "Inadequate sanitized surfaces",
    "Unapproved/unmaintained equip",
    "Inaccessible handwashing sinks",
    "Moderate risk food temp",
    "Unclean floors, walls, ceilings"
]
counts = [1629, 1841, 1894, 2142, 2290, 2309, 2423, 2596, 2787, 3545]
colors = ['#E11D48'] + ['#2563EB']*9 # Highlight High Risk in red!

y_pos = np.arange(len(violations))
bars = ax_left.barh(y_pos, counts, color=colors, height=0.62, alpha=0.9)

for bar in bars:
    w = bar.get_width()
    ax_left.text(w + 60, bar.get_y() + bar.get_height()/2, f"{w:,}", va='center', fontsize=8, fontweight='bold', color='#1E293B')

ax_left.set_yticks(y_pos)
ax_left.set_yticklabels(violations, fontsize=8.5, color='#334155')
ax_left.set_xlim(0, 4200)
ax_left.set_xticks([]) # Bersihkan sumbu X
ax_left.grid(False)
ax_left.set_title("Top 10 Pelanggaran Sanitasi Paling Sering Terjadi", fontsize=11, fontweight='bold', pad=12, loc='left', color='#0F172A')

# 4. Visual Kanan Atas: Top 5 Kode Pos Rawan High Risk (% High Risk)
ax_rtop = fig.add_axes([0.51, 0.44, 0.45, 0.26])
ax_rtop.set_facecolor('#FFFFFF')
for spine in ax_rtop.spines.values():
    spine.set_color('#E2E8F0')

districts = ["94108 (Chinatown)", "94133 (North Beach)", "94116 (Parkside)", "94122 (Sunset)", "94104 (Financial District)"]
rates = [19.2, 19.7, 19.9, 20.5, 22.9]

y_d = np.arange(len(districts))
bars_d = ax_rtop.barh(y_d, rates, color='#E11D48', height=0.55, alpha=0.85)

for bar in bars_d:
    w = bar.get_width()
    ax_rtop.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', fontsize=8.5, fontweight='bold', color='#E11D48')

ax_rtop.set_yticks(y_d)
ax_rtop.set_yticklabels(districts, fontsize=8.5, color='#334155')
ax_rtop.set_xlim(0, 27)
ax_rtop.set_xticks([])
ax_rtop.grid(False)
ax_rtop.set_title("Top 5 Wilayah: % Inspeksi High Risk (min. 100 inspeksi)", fontsize=11, fontweight='bold', pad=10, loc='left', color='#0F172A')

# 5. Visual Kanan Bawah: Tren Bulanan High Risk Rate (% Line Chart)
ax_rbot = fig.add_axes([0.51, 0.12, 0.45, 0.27])
ax_rbot.set_facecolor('#FFFFFF')
for spine in ax_rbot.spines.values():
    spine.set_color('#E2E8F0')

months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
trend_rates = [12.5, 16.3, 15.7, 14.9, 17.2, 17.7, 17.0, 16.3, 15.6, 16.3, 15.2, 15.8]

ax_rbot.plot(months, trend_rates, marker='o', color='#2563EB', linewidth=2.5, markersize=5)
ax_rbot.fill_between(months, trend_rates, alpha=0.12, color='#2563EB')

# Highlight peak in Mei-Jun
ax_rbot.scatter([4, 5], [17.2, 17.7], color='#E11D48', s=60, zorder=5)
ax_rbot.annotate("Puncak Mei-Juni", xy=(5, 17.7), xytext=(1.6, 19.3),
                 arrowprops=dict(facecolor='#E11D48', arrowstyle="->", lw=1.2),
                 fontsize=8, fontweight='bold', color='#E11D48')

ax_rbot.set_ylim(8, 21)
ax_rbot.set_yticks([10, 15, 20])
ax_rbot.set_yticklabels(["10%", "15%", "20%"], fontsize=8, color='#64748B')
ax_rbot.tick_params(axis='x', labelsize=8.5, colors='#334155')
ax_rbot.grid(axis='y', linestyle='--', alpha=0.4)
ax_rbot.set_title("Tren Laju Pelanggaran High Risk Bulanan (Pola Musiman)", fontsize=11, fontweight='bold', pad=10, loc='left', color='#0F172A')

# 6. Bottom Strategic Callout Banner
ax_bot = fig.add_axes([0.04, 0.025, 0.92, 0.07])
ax_bot.set_facecolor('#EFF6FF')
for spine in ax_bot.spines.values():
    spine.set_color('#BFDBFE')
ax_bot.set_xticks([])
ax_bot.set_yticks([])

ax_bot.text(0.015, 0.65, "[REKOMENDASI STRATEGIS DINAS KESEHATAN (SFDPH)]", fontsize=9, fontweight='bold', color='#1D4ED8')
ax_bot.text(0.015, 0.22, "1. Prioritaskan inspeksi di 94104, 94122, 94116, 94133 & 94108   |   2. Kampanye pencegahan hama Maret-April   |   3. Inspeksi ulang maks. 14 hari untuk skor < 70", fontsize=8.5, color='#1E40AF')

# Simpan hasil gambar mockup
out_dir = os.path.join("reports", "figures")
os.makedirs(out_dir, exist_ok=True)
mockup_path = os.path.join(out_dir, "dashboard_mockup.png")
plt.savefig(mockup_path, dpi=200, bbox_inches='tight')
plt.close()

# Salin juga ke folder dashboard
dash_mockup = os.path.join("dashboard", "dashboard_mockup.png")
import shutil
shutil.copy2(mockup_path, dash_mockup)

print(f"Mockup dashboard berhasil dibuat di: {mockup_path}")
