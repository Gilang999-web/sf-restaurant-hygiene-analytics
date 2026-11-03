"""
generate_kesimpulan_pptx.py
Membuat presentasi PowerPoint 11 slide profesional berdasarkan outline
di kesimpulan.md — sesuai best practice Data Analyst presentation ke stakeholder.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
import pptx.oxml.ns as nsmap
from lxml import etree

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(CURRENT_DIR)
FIGS        = os.path.join(BASE_DIR, "reports", "figures")
OUT_PPTX    = os.path.join(BASE_DIR, "reports", "Gilang_Anugrah_SF_Hygiene_Analytics_Presentation.pptx")

# ─────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────
NAVY      = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A  dark background
BLUE      = RGBColor(0x25, 0x63, 0xEB)   # #2563EB  primary blue
BLUE_SOFT = RGBColor(0xEF, 0xF6, 0xFF)   # #EFF6FF  very light blue
SLATE     = RGBColor(0x64, 0x74, 0x8B)   # #64748B  body text grey
SLATE_LT  = RGBColor(0x94, 0xA3, 0xB8)   # #94A3B8  subtitle grey
BORDER    = RGBColor(0xE2, 0xE8, 0xF0)   # #E2E8F0  card border
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
CORAL     = RGBColor(0xE1, 0x1D, 0x48)   # #E11D48  high-risk red
AMBER     = RGBColor(0xF5, 0x9E, 0x0B)   # #F59E0B  warning amber
EMERALD   = RGBColor(0x10, 0xB9, 0x81)   # #10B981  success green
BLUE_LT   = RGBColor(0x60, 0xA5, 0xFA)   # #60A5FA  light blue accent

W   = Inches(13.333)   # 16:9 slide width
H   = Inches(7.5)      # 16:9 slide height


# ─────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ─────────────────────────────────────────────────────────────

def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])   # blank layout


def bg(slide, color):
    """Fill slide background with solid colour."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, l, t, w, h, fill_rgb, line_rgb=None, line_w=Pt(0)):
    """Add a plain rectangle shape."""
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shp.line.color.rgb = line_rgb
        shp.line.width = line_w
    else:
        shp.line.fill.background()
    return shp


def rnd_rect(slide, l, t, w, h, fill_rgb, line_rgb=None, line_w=Pt(1)):
    """Add a rounded-rectangle shape."""
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shp.line.color.rgb = line_rgb
        shp.line.width = line_w
    else:
        shp.line.fill.background()
    return shp


def txbox(slide, l, t, w, h, wrap=True):
    """Add a text box and return its TextFrame."""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf  = box.text_frame
    tf.word_wrap = wrap
    return tf


def add_para(tf, text, size, bold=False, color=None, align=PP_ALIGN.LEFT, space_before=0, space_after=0):
    """Add a paragraph to a TextFrame."""
    p = tf.add_paragraph()
    p.text            = text
    p.font.size       = Pt(size)
    p.font.bold       = bold
    p.font.color.rgb  = color or NAVY
    p.alignment       = align
    p.space_before    = Pt(space_before)
    p.space_after     = Pt(space_after)
    return p


def first_para(tf, text, size, bold=False, color=None, align=PP_ALIGN.LEFT):
    """Set the first (empty) paragraph of a TextFrame."""
    p = tf.paragraphs[0]
    p.text            = text
    p.font.size       = Pt(size)
    p.font.bold       = bold
    p.font.color.rgb  = color or NAVY
    p.alignment       = align
    return p


def accent_bar(slide, l, t, w, h, color):
    """Thin coloured bar used as accent/divider."""
    return rect(slide, l, t, w, h, color)


def eyebrow(slide, text, top=Inches(0.36)):
    """Small ALL-CAPS category label above the main title."""
    tf = txbox(slide, Inches(0.8), top, Inches(11.7), Inches(0.3))
    first_para(tf, text.upper(), 9, bold=True, color=BLUE)


def slide_title(slide, text, top=Inches(0.65), size=24):
    """Main slide heading."""
    tf = txbox(slide, Inches(0.8), top, Inches(11.7), Inches(0.75))
    first_para(tf, text, size, bold=True, color=NAVY)


def divider(slide, top=Inches(1.38)):
    """Thin horizontal rule below the title."""
    rect(slide, Inches(0.8), top, Inches(11.73), Inches(0.025), BORDER)


def kpi_card(slide, l, t, w, h, label, value, sub="", accent=BLUE):
    """Reusable KPI card with top accent bar."""
    rnd_rect(slide, l, t, w, h, WHITE, BORDER)
    rect(slide, l, t, w, Inches(0.07), accent)   # top accent strip

    tf = txbox(slide, l + Inches(0.18), t + Inches(0.13),
               w - Inches(0.36), h - Inches(0.2))
    first_para(tf, label.upper(), 8.5, bold=True, color=SLATE)
    add_para(tf, value, 24, bold=True, color=accent)
    if sub:
        add_para(tf, sub, 8, color=SLATE_LT)


def content_card(slide, l, t, w, h, title, bullets, title_color=NAVY):
    """White rounded card with title + bullet list."""
    rnd_rect(slide, l, t, w, h, WHITE, BORDER)
    tf = txbox(slide, l + Inches(0.22), t + Inches(0.18),
               w - Inches(0.44), h - Inches(0.36))
    first_para(tf, title, 13, bold=True, color=title_color)
    for b in bullets:
        add_para(tf, "• " + b, 10, color=NAVY, space_before=3)


def rec_card(slide, top, num_text, num_color, title, subtitle, detail):
    """Full-width recommendation row card."""
    h = Inches(1.6)
    rnd_rect(slide, Inches(0.8), top, Inches(11.73), h, WHITE, BORDER)

    # Number badge
    rect(slide, Inches(0.8), top, Inches(1.05), h, num_color)
    tf_n = txbox(slide, Inches(0.8), top + Inches(0.5), Inches(1.05), Inches(0.6))
    first_para(tf_n, num_text, 26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # Text block
    tf = txbox(slide, Inches(2.05), top + Inches(0.1),
               Inches(10.3), h - Inches(0.2))
    first_para(tf, title.upper(), 11.5, bold=True, color=num_color)
    add_para(tf, subtitle, 10, bold=True, color=NAVY, space_before=2)
    add_para(tf, detail, 9.5, color=SLATE, space_before=3)


def img(slide, path, l, t, width):
    """Embed a picture if the file exists."""
    if os.path.exists(path):
        slide.shapes.add_picture(path, l, t, width=width)


def data_table(slide, l, t, w, headers, rows, hdr_color=BLUE, row_colors=None):
    """Simple styled table."""
    ncols = len(headers)
    nrows = len(rows)
    tbl = slide.shapes.add_table(nrows + 1, ncols, l, t, w, Inches(0.35 * (nrows + 1))).table

    # Header row
    for ci, h_text in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = h_text
        cell.fill.solid(); cell.fill.fore_color.rgb = hdr_color
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9); p.font.bold = True; p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    # Data rows
    for ri, row in enumerate(rows):
        rc = (row_colors[ri] if row_colors else WHITE)
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = str(val)
            cell.fill.solid(); cell.fill.fore_color.rgb = rc
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9); p.font.color.rgb = NAVY
            p.alignment = PP_ALIGN.CENTER


# ─────────────────────────────────────────────────────────────
# BUILD PRESENTATION
# ─────────────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H

    # ── SLIDE 1: COVER ──────────────────────────────────────────
    s1 = new_slide(prs)
    bg(s1, NAVY)

    # Decorative left accent bar
    rect(s1, Inches(0.75), Inches(1.4), Inches(0.18), Inches(4.8), BLUE)

    tf = txbox(s1, Inches(1.15), Inches(1.4), Inches(11.5), Inches(5.2))
    first_para(tf, "DATA ANALYST PORTFOLIO PROJECT", 11, bold=True, color=BLUE_LT)
    add_para(tf, "SF Restaurant Hygiene & Safety Analytics", 34, bold=True, color=WHITE, space_before=6)
    add_para(tf, "Data-Driven Public Health Surveillance & Risk Intelligence (2014–2016)", 15, color=RGBColor(0xCB,0xD5,0xE1), space_before=4)
    add_para(tf, "", 8)
    add_para(tf, "Presented to: San Francisco Department of Public Health (SFDPH)", 11, color=SLATE_LT)
    add_para(tf, "Author: Gilang Anugrah  |  Data Analyst", 11, color=SLATE_LT, space_before=3)

    # Bottom tool strip
    rect(s1, Inches(0), Inches(6.8), W, Inches(0.7), RGBColor(0x1E,0x29,0x3B))
    tf_t = txbox(s1, Inches(0.8), Inches(6.85), Inches(11.7), Inches(0.55))
    first_para(tf_t, "Python  ·  Pandas  ·  SQL / T-SQL  ·  Power BI  ·  DAX  ·  SSMS",
               11, color=SLATE_LT, align=PP_ALIGN.CENTER)

    # ── SLIDE 2: DATASET OVERVIEW ───────────────────────────────
    s2 = new_slide(prs)
    bg(s2, BLUE_SOFT)
    eyebrow(s2, "Context & Data Source")
    slide_title(s2, "The Data Source: 3 Years of Official SF Health Inspection Records")
    divider(s2)

    # 3 info columns
    cols = [
        ("📦  Volume Data",
         ["53.555 baris catatan inspeksi", "17 kolom atribut bisnis & kesehatan",
          "Sumber: Kaggle (datasf/sf-restaurant-inspection-scores)",
          "Format: CSV – LIVES Standard"]),
        ("📅  Rentang Waktu",
         ["3 tahun data historis penuh", "2 Januari 2014 – 30 Desember 2016",
          "Mencakup 3 siklus musim penuh",
          "Pemilik: SFDPH (Pemerintah Kota SF)"]),
        ("🏢  Cakupan",
         ["6.078 restoran & usaha kuliner unik", "27 distrik kota San Francisco",
          "Termasuk: Restoran, Kafe, Food Truck",
          "Standar LIVES: transparansi publik nasional"]),
    ]
    col_w = Inches(3.7)
    for i, (title, bullets) in enumerate(cols):
        lx = Inches(0.8) + i * (col_w + Inches(0.25))
        content_card(s2, lx, Inches(1.55), col_w, Inches(2.6), title, bullets, BLUE)

    # Inspection type table
    rect(s2, Inches(0.8), Inches(4.35), Inches(11.73), Inches(0.04), BORDER)
    tf_hdr = txbox(s2, Inches(0.8), Inches(4.45), Inches(7), Inches(0.35))
    first_para(tf_hdr, "Jenis Inspeksi yang Dilakukan (Top 5)", 11, bold=True, color=NAVY)

    data_table(
        s2, Inches(0.8), Inches(4.85), Inches(11.73),
        headers=["Jenis Inspeksi", "Jumlah Sesi", "Keterangan"],
        rows=[
            ["Routine – Unscheduled", "14.925", "Inspeksi mendadak rutin tanpa pemberitahuan"],
            ["Reinspection / Followup", "5.168", "Kunjungan ulang setelah sesi sebelumnya bermasalah"],
            ["New Ownership", "1.549", "Wajib saat restoran berganti pemilik"],
            ["Complaint Based", "1.261", "Dipicu laporan dari konsumen atau warga"],
            ["New Construction", "1.684", "Wajib sebelum restoran baru beroperasi"],
        ],
        hdr_color=NAVY,
        row_colors=[BLUE_SOFT, WHITE, BLUE_SOFT, WHITE, BLUE_SOFT]
    )

    # ── SLIDE 3: METHODOLOGY ────────────────────────────────────
    s3 = new_slide(prs)
    bg(s3, BLUE_SOFT)
    eyebrow(s3, "Methodology & Tech Stack")
    slide_title(s3, "End-to-End Analytics Architecture (CRISP-DM Framework)")
    divider(s3)

    stages = [
        ("01", "Data Ingestion", "Download otomatis via kagglehub. 53.555 baris, 17 kolom, format CSV mentah.", "Python · KaggleHub"),
        ("02", "Data Cleaning", "Hapus 50 duplikat. Koreksi kode pos & GPS. Agregasi per sesi inspeksi → 25.834 baris bersih.", "Python · Pandas · NumPy"),
        ("03", "EDA & SQL", "Analisis Pareto, CTE, Window Functions (LAG, DENSE_RANK). Pola musiman & geografis.", "SQLite · T-SQL · SSMS"),
        ("04", "BI & Delivery", "Star-schema data model. Ukuran DAX dinamis. Dashboard eksekutif interaktif 16:9.", "Power BI · DAX"),
    ]
    stg_w = Inches(2.75)
    for i, (num, title, desc, tech) in enumerate(stages):
        lx = Inches(0.8) + i * (stg_w + Inches(0.28))
        # Header badge
        rnd_rect(s3, lx, Inches(1.65), stg_w, Inches(0.55), BLUE)
        tf_n = txbox(s3, lx, Inches(1.65), stg_w, Inches(0.55))
        first_para(tf_n, f"{num}  {title}", 12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

        # Body card
        rnd_rect(s3, lx, Inches(2.2), stg_w, Inches(4.6), WHITE, BORDER)
        tf_b = txbox(s3, lx + Inches(0.18), Inches(2.35), stg_w - Inches(0.36), Inches(4.3))
        first_para(tf_b, desc, 10.5, color=NAVY)
        add_para(tf_b, "", 6)
        add_para(tf_b, "Tools:", 9, bold=True, color=BLUE)
        add_para(tf_b, tech, 9.5, color=SLATE)

        # Connector arrow (except last)
        if i < 3:
            ax = lx + stg_w + Inches(0.04)
            tf_arr = txbox(s3, ax, Inches(2.35), Inches(0.2), Inches(0.4))
            first_para(tf_arr, "→", 18, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

    # ── SLIDE 4: FINDING 1 – SCORE PROFILE ──────────────────────
    s4 = new_slide(prs)
    bg(s4, BLUE_SOFT)
    eyebrow(s4, "Finding 1: Compliance Profile")
    slide_title(s4, "Citywide Compliance: 68% Operate in Good/Excellent Standing")
    divider(s4)

    img(s4, os.path.join(FIGS, "01_distribusi_skor_inspeksi.png"),
        Inches(0.8), Inches(1.6), width=Inches(4.5))
    img(s4, os.path.join(FIGS, "02_proporsi_kategori_skor.png"),
        Inches(5.5), Inches(1.6), width=Inches(3.0))

    # Right narrative
    rnd_rect(s4, Inches(8.75), Inches(1.6), Inches(3.75), Inches(5.6), WHITE, BORDER)
    tf_r = txbox(s4, Inches(8.95), Inches(1.75), Inches(3.4), Inches(5.3))
    first_para(tf_r, "Key Takeaways", 13, bold=True, color=NAVY)
    for b in [
        "Rata-rata skor kota 91.3/100 — kategori Good/Excellent berdasarkan standar SFDPH.",
        "68% dari sesi yang diberi skor masuk kategori Good/Excellent (≥90).",
        "Hanya 1.9% (275 sesi) tergolong Poor (<70) — zona darurat yang memerlukan tindakan segera.",
        "⚠️ Double-Counting Trap: data mentah menunjukkan 86.2 (salah). Setelah agregasi per sesi inspeksi, skor yang benar adalah 91.3.",
        "Kesimpulan: Kota secara umum SEHAT — namun 2% zona berbahaya tidak boleh diabaikan.",
    ]:
        add_para(tf_r, "• " + b, 9.5, color=NAVY, space_before=4)

    # Score tier summary bar at bottom
    tiers = [("Good/Excellent (≥90)", "10.050 sesi", "68.0%", EMERALD),
             ("Adequate (80–89)",     " 3.439 sesi", "23.3%", BLUE),
             ("Needs Improvement",    " 1.016 sesi", " 6.9%", AMBER),
             ("Poor (<70)",           "   275 sesi", " 1.9%", CORAL)]
    tier_w = Inches(11.73) / 4
    for i, (label, count, pct, color) in enumerate(tiers):
        lx = Inches(0.8) + i * tier_w
        rnd_rect(s4, lx, Inches(6.9), tier_w - Inches(0.05), Inches(0.5), color)
        tf_t = txbox(s4, lx, Inches(6.9), tier_w - Inches(0.05), Inches(0.5))
        first_para(tf_t, f"{pct}  {label}", 8.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # ── SLIDE 5: FINDING 2 – PARETO ─────────────────────────────
    s5 = new_slide(prs)
    bg(s5, BLUE_SOFT)
    eyebrow(s5, "Finding 2: Violation Analysis")
    slide_title(s5, "Pareto Principle: Top 10 Infractions Account for 58% of All Violations")
    divider(s5)

    img(s5, os.path.join(FIGS, "03_top_10_pelanggaran.png"),
        Inches(0.8), Inches(1.6), width=Inches(7.2))

    rnd_rect(s5, Inches(8.25), Inches(1.6), Inches(4.25), Inches(5.6), WHITE, BORDER)
    tf_r = txbox(s5, Inches(8.45), Inches(1.75), Inches(3.9), Inches(5.3))
    first_para(tf_r, "Operational vs Critical Hazards", 12, bold=True, color=NAVY)
    for b in [
        "#1 Terbanyak: Lantai/Dinding Kotor (3.545) — masalah pemeliharaan fisik rutin.",
        "86% pelanggaran bersifat Low/Moderate Risk — bukan bahaya biologis langsung.",
        "BAHAYA KRITIS: 'High-risk food holding temperature' (#10, 1.629 kasus) — satu-satunya pelanggaran biologis di 10 besar. Risiko Salmonella & E. coli.",
        "40.673 total pelanggaran tercatat — 10 jenis pertama = 57.7% kumulatif (Analisis Pareto).",
        "Rekomendasi: Buat 2 jalur penanganan — 'pemeliharaan rutin' untuk Low Risk dan 'darurat 24 jam' untuk High Risk.",
    ]:
        add_para(tf_r, "• " + b, 9.5, color=NAVY, space_before=4)

    # Risk distribution mini-cards
    for i, (label, pct, color) in enumerate([
        ("Low Risk",      "51.3%", EMERALD),
        ("Moderate Risk", "35.0%", AMBER),
        ("High Risk",     "13.8%", CORAL),
    ]):
        lx = Inches(8.25) + i * Inches(1.42)
        rnd_rect(s5, lx, Inches(6.85), Inches(1.35), Inches(0.55), color)
        tf_m = txbox(s5, lx, Inches(6.85), Inches(1.35), Inches(0.55))
        first_para(tf_m, f"{pct}\n{label}", 8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # ── SLIDE 6: FINDING 3 – GEO HOTSPOTS ──────────────────────
    s6 = new_slide(prs)
    bg(s6, BLUE_SOFT)
    eyebrow(s6, "Finding 3: Geographic Risk Profiling")
    slide_title(s6, "Risk Hotspot Map: Downtown Corridors Carry Disproportionate Hazard")
    divider(s6)

    img(s6, os.path.join(FIGS, "06_top_kodepos_high_risk.png"),
        Inches(0.8), Inches(1.6), width=Inches(6.8))

    rnd_rect(s6, Inches(7.85), Inches(1.6), Inches(4.65), Inches(5.6), WHITE, BORDER)
    tf_r = txbox(s6, Inches(8.05), Inches(1.75), Inches(4.3), Inches(2.3))
    first_para(tf_r, "Top 5 Wilayah Paling Berisiko\n(sample ≥ 100 inspeksi)", 12, bold=True, color=NAVY)

    # Mini table inside card
    hotspots = [
        ("#1", "94104 – Financial District S", "22.91%"),
        ("#2", "94122 – Sunset North",         "20.46%"),
        ("#3", "94116 – Sunset South",         "19.85%"),
        ("#4", "94133 – North Beach",          "19.67%"),
        ("#5", "94108 – Chinatown",            "19.25%"),
    ]
    for j, (rank, area, rate) in enumerate(hotspots):
        ty = Inches(2.7) + j * Inches(0.47)
        rg = [CORAL, RGBColor(0xFB,0x7B,0x85), RGBColor(0xFB,0xA4,0xAB),
              RGBColor(0xFC,0xC5,0xC9), RGBColor(0xFD,0xE0,0xE2)][j]
        rnd_rect(s6, Inches(8.05), ty, Inches(4.1), Inches(0.42), rg)
        tf_h = txbox(s6, Inches(8.1), ty + Inches(0.04), Inches(4.05), Inches(0.36))
        first_para(tf_h, f"{rank}  {area}  —  {rate}", 9.5, bold=(j==0), color=WHITE)

    tf_n = txbox(s6, Inches(8.05), Inches(5.1), Inches(4.3), Inches(2.0))
    first_para(tf_n, "Mengapa Pusat Kota Lebih Berisiko?", 11, bold=True, color=NAVY)
    for b in [
        "Volume pengunjung sangat tinggi → tekanan berlebih pada peralatan dapur.",
        "Infrastruktur gedung lama → saluran & insulasi rapuh.",
        "Kepadatan perkotaan → populasi hama lebih tinggi.",
        "⚡ Realokasikan 20% kapasitas inspektur ke koridor ini.",
    ]:
        add_para(tf_n, "• " + b, 9.5, color=NAVY, space_before=3)

    # ── SLIDE 7: FINDING 4 – SEASONALITY ────────────────────────
    s7 = new_slide(prs)
    bg(s7, BLUE_SOFT)
    eyebrow(s7, "Finding 4: Temporal Seasonality")
    slide_title(s7, "Early Warning: +85% Surge in Pest Infestations Every Summer (May–June)")
    divider(s7)

    img(s7, os.path.join(FIGS, "05_pola_musiman_hama.png"),
        Inches(0.8), Inches(1.6), width=Inches(7.0))

    rnd_rect(s7, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.6), WHITE, BORDER)
    tf_r = txbox(s7, Inches(8.3), Inches(1.75), Inches(4.0), Inches(5.3))
    first_para(tf_r, "Predictive Public Health Intervention", 12, bold=True, color=NAVY)
    for b in [
        "Insiden hama memuncak di Juni (353 kejadian) — +85% vs Desember–Januari (162–190).",
        "Laju High Risk bulanan naik dari 12.5% (Januari) ke 17.7% (Juni).",
        "Faktor ganda: suhu panas memperburuk performa kulkas & mempercepat perkembangbiakan hama secara bersamaan.",
        "Pola ini konsisten selama 3 tahun berturut-turut — bukan anomali, tapi siklus yang bisa diprediksi.",
    ]:
        add_para(tf_r, "• " + b, 9.5, color=NAVY, space_before=5)

    add_para(tf_r, "", 6)
    add_para(tf_r, "✅ AKSI PREVENTIF", 10.5, bold=True, color=EMERALD)
    add_para(tf_r,
             "Luncurkan audit mandiri hama ke seluruh restoran di bulan APRIL — satu bulan sebelum lonjakan dimulai. Jangan tunggu Juli!",
             9.5, color=NAVY, space_before=3)

    # Month comparison mini-bars
    months_data = [
        ("Jan", 190, 0.125), ("Feb", 249, 0.163), ("Mar", 302, 0.157),
        ("Apr", 309, 0.149), ("Mei", 332, 0.172), ("Jun*", 353, 0.177),
        ("Jul", 231, 0.170), ("Agu", 271, 0.163), ("Sep", 282, 0.156),
        ("Okt", 274, 0.163), ("Nov", 213, 0.152), ("Des", 162, 0.158),
    ]
    bar_area_w = Inches(6.8)
    bar_h_max  = Inches(0.9)
    bar_w      = bar_area_w / 12
    max_vermin = 353
    for i, (m, v, _) in enumerate(months_data):
        bar_h = bar_h_max * (v / max_vermin)
        lx = Inches(0.8) + i * bar_w
        ty = Inches(6.5) - bar_h
        clr = CORAL if m in ("Mei", "Jun*") else BLUE
        rect(s7, lx + Inches(0.05), ty, bar_w - Inches(0.1), bar_h, clr)
        tf_lbl = txbox(s7, lx, Inches(6.55), bar_w, Inches(0.25))
        first_para(tf_lbl, m, 7, color=NAVY, align=PP_ALIGN.CENTER)

    # ── SLIDE 8: FINDING 5 – REMEDIATION ────────────────────────
    s8 = new_slide(prs)
    bg(s8, BLUE_SOFT)
    eyebrow(s8, "Finding 5: Enforcement Efficacy")
    slide_title(s8, "Enforcement Works: Re-Inspection Delivers Average +8.57 Point Recovery")
    divider(s8)

    img(s8, os.path.join(FIGS, "07_efektivitas_intervensi_regulator.png"),
        Inches(0.8), Inches(1.6), width=Inches(6.2))

    # 4 KPI cards
    kpis = [
        ("Restoran Dianalisis", "730", "Pernah skor <80",  BLUE),
        ("Skor Awal (Gagal)",   "72.92", "Sebelum re-inspeksi", CORAL),
        ("Skor Tindak Lanjut",  "81.49", "Setelah kunjungan ulang", AMBER),
        ("Rata-rata Kenaikan",  "+8.57", "Poin pemulihan",  EMERALD),
    ]
    kpi_w = Inches(2.65)
    for i, (lbl, val, sub, clr) in enumerate(kpis):
        lx = Inches(7.4) + i * (kpi_w + Inches(0.08))
        kpi_card(s8, lx, Inches(1.6), kpi_w, Inches(1.5), lbl, val, sub, clr)

    rnd_rect(s8, Inches(7.4), Inches(3.3), Inches(5.75), Inches(3.9), WHITE, BORDER)
    tf_r = txbox(s8, Inches(7.6), Inches(3.45), Inches(5.35), Inches(3.7))
    first_para(tf_r, "Measuring Regulatory Compliance ROI", 12, bold=True, color=NAVY)
    for b in [
        "Analisis menggunakan SQL Window Function LAG() untuk melacak skor setiap restoran dari inspeksi ke inspeksi berikutnya.",
        "76% restoran yang awalnya bermasalah (skor <80) berhasil keluar dari zona bahaya setelah 1 kali kunjungan korektif.",
        "Kenaikan +8.57 poin dalam 1 kunjungan adalah bukti nyata bahwa sistem re-inspeksi SFDPH efektif.",
        "Re-inspeksi bukan sekadar hukuman — ini adalah mekanisme koreksi perilaku yang terukur secara data.",
        "⚡ KEBIJAKAN: Wajibkan SOP re-inspeksi 14 hari bagi setiap restoran dengan skor di bawah 80.",
    ]:
        add_para(tf_r, "• " + b, 9.5, color=NAVY, space_before=4)

    # ── SLIDE 9: DASHBOARD SHOWCASE ─────────────────────────────
    s9 = new_slide(prs)
    bg(s9, BLUE_SOFT)
    eyebrow(s9, "BI Deliverable Showcase")
    slide_title(s9, "Executive Power BI Dashboard: Interactive Surveillance Center")
    divider(s9)

    img(s9, os.path.join(FIGS, "dashboard_mockup.png"),
        Inches(0.8), Inches(1.58), width=Inches(8.0))

    rnd_rect(s9, Inches(9.1), Inches(1.58), Inches(3.42), Inches(5.65), WHITE, BORDER)
    tf_r = txbox(s9, Inches(9.3), Inches(1.75), Inches(3.1), Inches(5.4))
    first_para(tf_r, "Dashboard Highlights", 13, bold=True, color=NAVY)
    for b in [
        "Ukuran 16:9 HD Widescreen — siap digunakan di layar presentasi besar.",
        "4 Kartu KPI Eksekutif dengan kalkulasi DAX dinamis.",
        "Cross-Filtering: klik satu distrik → semua chart langsung menyesuaikan.",
        "Filter Slicer bulan/tahun: analisis tren real-time.",
        "Palet warna 3 level: Hijau (Aman) · Amber (Perhatian) · Merah (Kritis).",
        "Data bisa diperbarui setiap saat dengan satu klik Refresh.",
    ]:
        add_para(tf_r, "• " + b, 9.5, color=NAVY, space_before=5)

    add_para(tf_r, "", 4)
    add_para(tf_r, "Tech Specs:", 9.5, bold=True, color=BLUE)
    add_para(tf_r, "Power BI Desktop · DAX · Star-Schema\n25.834 sesi inspeksi bersih", 9, color=SLATE)

    # ── SLIDE 10: RECOMMENDATIONS ───────────────────────────────
    s10 = new_slide(prs)
    bg(s10, BLUE_SOFT)
    eyebrow(s10, "Strategic Action Plan")
    slide_title(s10, "3 Data-Driven Recommendations to Maximise Public Health Impact")
    divider(s10)

    rec_card(
        s10, top=Inches(1.58),
        num_text="01", num_color=BLUE,
        title="Geographic Resource Reallocation",
        subtitle="Realokasikan 20% kapasitas patroli inspektur ke koridor komersial berisiko tinggi.",
        detail="Prioritaskan Financial District (94104, 22.91%), Sunset North (94122, 20.46%), dan North Beach (94133, 19.67%). "
               "Setiap jam inspektur di zona risiko tinggi melindungi dua kali lebih banyak konsumen dibanding zona suburban berskor baik."
    )
    rec_card(
        s10, top=Inches(3.38),
        num_text="02", num_color=CORAL,
        title="Pre-Summer Pest Abatement Campaign",
        subtitle="Kirim notifikasi wajib ke seluruh restoran berisiko tinggi setiap APRIL — sebelum lonjakan dimulai.",
        detail="Mandatkan audit segel dumpster, perangkap hama preventif, dan pemeriksaan insulasi freezer. "
               "Strategi preventif ini memotong lonjakan +85% kasus hama musim panas secara signifikan tanpa biaya reaktif."
    )
    rec_card(
        s10, top=Inches(5.18),
        num_text="03", num_color=EMERALD,
        title="Standardized 14-Day Re-Inspection Protocol",
        subtitle="Formalisasikan SOP bahwa restoran dengan skor <80 WAJIB mendapat kunjungan ulang dalam 14 hari kerja.",
        detail="Data membuktikan 76% restoran berhasil memperbaiki skor mereka setelah 1 kali kunjungan korektif (+8.57 poin rata-rata). "
               "Re-inspeksi adalah mekanisme koreksi perilaku yang terbukti cost-effective."
    )

    # ── SLIDE 11: CLOSING ────────────────────────────────────────
    s11 = new_slide(prs)
    bg(s11, NAVY)

    rect(s11, Inches(0.75), Inches(0.9), Inches(0.18), Inches(3.8), BLUE)

    tf_l = txbox(s11, Inches(1.2), Inches(0.85), Inches(6.5), Inches(4.2))
    first_para(tf_l, "Thank You!", 40, bold=True, color=WHITE)
    add_para(tf_l, "Questions & Discussion", 20, color=BLUE_LT, space_before=4)
    add_para(tf_l, "", 8)
    add_para(tf_l, "Gilang Anugrah  |  Data Analyst", 12, color=SLATE_LT)
    add_para(tf_l, "GitHub: sf-restaurant-hygiene-analytics", 11, color=SLATE_LT, space_before=2)

    # 5 findings recap
    rnd_rect(s11, Inches(7.8), Inches(0.85), Inches(4.75), Inches(5.7), RGBColor(0x1E,0x29,0x3B), BLUE, Pt(1))
    tf_r = txbox(s11, Inches(8.0), Inches(1.0), Inches(4.35), Inches(5.4))
    first_para(tf_r, "5 Key Findings Summary", 12, bold=True, color=BLUE_LT)
    for b in [
        "✅ Rata-rata skor kota 91.3 — lebih sehat dari tampilan data mentah (86.2).",
        "✅ 10 pelanggaran = 58% masalah — fokus Pareto memberikan dampak terbesar.",
        "✅ Financial District & Sunset North — zona prioritas pengawasan intensif.",
        "✅ Juni = puncak bahaya hama (+85%) — intervensi April adalah kunci.",
        "✅ Re-inspeksi efektif: +8.57 poin recovery pada 76% restoran bermasalah.",
    ]:
        add_para(tf_r, b, 10, color=WHITE, space_before=6)

    # Bottom project info strip
    rect(s11, Inches(0), Inches(6.75), W, Inches(0.75), RGBColor(0x1E,0x29,0x3B))
    tf_b = txbox(s11, Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.55))
    first_para(tf_b,
               "Portfolio Project: SF Restaurant Hygiene & Safety Analytics  |  "
               "Python  ·  Pandas  ·  SQL/T-SQL  ·  Power BI  ·  DAX",
               10, color=SLATE_LT, align=PP_ALIGN.CENTER)

    # ── SAVE ────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUT_PPTX), exist_ok=True)
    prs.save(OUT_PPTX)
    print(f"[OK] PPTX saved -> {OUT_PPTX}")
    return OUT_PPTX


if __name__ == "__main__":
    build()
