"""
generate_storytelling_pptx.py
Membuat deck presentasi STORYTELLING (16:9) untuk stakeholder SFDPH.

Alur cerita (Situation -> Complication -> Resolution):
  1. Cover
  2. Pertanyaan kunci (peta cerita)
  3. Data & pendekatan
  4. Babak 1 - Kabar baik: kota relatif sehat          (Foto 01 + 02)
  5. Babak 2 - Masalahnya terkonsentrasi              (Foto 03)
  6. Babak 2 - Bahaya yang sesungguhnya               (Foto 04)
  7. Babak 3 - DI MANA risiko berkumpul               (Foto 06)
  8. Babak 3 - KAPAN risiko memuncak                  (Foto 05)
  9. Babak 4 - Apakah intervensi berhasil?            (Foto 07)
 10. Sintesis temuan
 11. Rekomendasi
 12. Roadmap & KPI pemantauan
 13. Dashboard sebagai alat monitoring                (dashboard_mockup)
 14. Penutup
 15. Lampiran: metodologi & catatan data

Semua angka diverifikasi langsung dari data/processed/*.csv.
Setiap slide dilengkapi speaker notes (naskah bicara).
"""

import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ------------------------------------------------------------------ paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FIGS = os.path.join(BASE_DIR, "reports", "figures")
OUT = os.path.join(BASE_DIR, "reports", "Storytelling_SF_Restaurant_Hygiene_Gilang_Anugrah.pptx")

# ------------------------------------------------------------------ palette
NAVY = RGBColor(0x0F, 0x17, 0x2A)
NAVY_2 = RGBColor(0x1E, 0x29, 0x3B)
BLUE = RGBColor(0x25, 0x63, 0xEB)
BLUE_LT = RGBColor(0x93, 0xC5, 0xFD)
BLUE_BG = RGBColor(0xEF, 0xF6, 0xFF)
INK = RGBColor(0x1E, 0x29, 0x3B)
BODY = RGBColor(0x47, 0x55, 0x69)
MUTED = RGBColor(0x94, 0xA3, 0xB8)
LINE = RGBColor(0xE2, 0xE8, 0xF0)
CANVAS = RGBColor(0xF8, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xE1, 0x1D, 0x48)
RED_BG = RGBColor(0xFF, 0xF1, 0xF2)
AMBER = RGBColor(0xD9, 0x77, 0x06)
AMBER_BG = RGBColor(0xFF, 0xFB, 0xEB)
GREEN = RGBColor(0x05, 0x96, 0x69)
GREEN_BG = RGBColor(0xEC, 0xFD, 0xF5)

FONT = "Segoe UI"
SW, SH = Inches(13.333), Inches(7.5)
MX = Inches(0.6)                  # horizontal margin
CW = SW - 2 * MX                  # content width
TOTAL_SLIDES = 15


# ================================================================== helpers
def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=0.75, radius=None):
    s = slide.shapes.add_shape(kind, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def box(slide, x, y, w, h, fill=WHITE, line=LINE, radius=0.04):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, 0.75, radius)


def bar(slide, x, y, w, h, fill):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill)


def text(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, shape_obj=None):
    """paras: list of dict(t=str | list[(str, dict)], size, color, bold, align, after, before)."""
    if shape_obj is None:
        tb = slide.shapes.add_textbox(x, y, w, h)
    else:
        tb = shape_obj
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = p.get("align", PP_ALIGN.LEFT)
        para.space_after = Pt(p.get("after", 0))
        para.space_before = Pt(p.get("before", 0))
        para.line_spacing = p.get("ls", 1.08)
        runs = p["t"] if isinstance(p["t"], list) else [(p["t"], {})]
        for rt, ro in runs:
            r = para.add_run()
            r.text = rt
            f = r.font
            f.name = FONT
            f.size = Pt(ro.get("size", p.get("size", 12)))
            f.bold = ro.get("bold", p.get("bold", False))
            f.italic = ro.get("italic", p.get("italic", False))
            f.color.rgb = ro.get("color", p.get("color", INK))
    return tb


def P(t, size=12, color=INK, bold=False, align=PP_ALIGN.LEFT, after=0, before=0, ls=1.08, italic=False):
    return dict(t=t, size=size, color=color, bold=bold, align=align, after=after, before=before, ls=ls, italic=italic)


def picture(slide, path, x, y, max_w, max_h):
    """Place image centred inside (x, y, max_w, max_h) keeping aspect ratio."""
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w, h = int(iw * ratio), int(ih * ratio)
    slide.shapes.add_picture(path, x + (max_w - w) // 2, y + (max_h - h) // 2, w, h)
    return w, h


def notes(slide, script):
    slide.notes_slide.notes_text_frame.text = script


def chrome(slide, num, eyebrow, title, chapter=None):
    """Standard light slide: background, eyebrow, action title, footer."""
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = CANVAS
    bar(slide, 0, 0, SW, Inches(0.08), NAVY)
    text(slide, MX, Inches(0.42), CW, Inches(0.3), [P(eyebrow.upper(), 10, BLUE, True)])
    text(slide, MX, Inches(0.72), CW, Inches(0.9), [P(title, 24, NAVY, True, ls=1.0)])
    # footer
    bar(slide, MX, Inches(7.0), CW, Inches(0.01), LINE)
    text(slide, MX, Inches(7.08), Inches(9), Inches(0.25),
         [P("SF Restaurant Hygiene & Safety Analytics  |  Gilang Anugrah", 9, MUTED)])
    text(slide, SW - MX - Inches(2), Inches(7.08), Inches(2), Inches(0.25),
         [P(f"{num} / {TOTAL_SLIDES}", 9, MUTED, align=PP_ALIGN.RIGHT)])
    if chapter:
        pill_w = Inches(1.9)
        pill = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, SW - MX - pill_w, Inches(0.36),
                     pill_w, Inches(0.34), BLUE_BG, None, radius=0.5)
        text(slide, 0, 0, 0, 0, [P(chapter, 9, BLUE, True, PP_ALIGN.CENTER)],
             anchor=MSO_ANCHOR.MIDDLE, shape_obj=pill)


def numbered_insights(slide, x, y, w, items, gap=Inches(0.14), item_h=Inches(1.0)):
    """items: list of (headline, detail). Numbered circle + text."""
    for i, (head, detail) in enumerate(items):
        iy = y + i * (item_h + gap)
        c = shape(slide, MSO_SHAPE.OVAL, x, iy, Inches(0.36), Inches(0.36), NAVY)
        text(slide, 0, 0, 0, 0, [P(str(i + 1), 11, WHITE, True, PP_ALIGN.CENTER)],
             anchor=MSO_ANCHOR.MIDDLE, shape_obj=c)
        text(slide, x + Inches(0.52), iy - Inches(0.02), w - Inches(0.52), item_h,
             [P(head, 12.5, NAVY, True, after=3), P(detail, 10.5, BODY, ls=1.12)])


def callout(slide, x, y, w, h, label, body, fg=BLUE, bg=BLUE_BG):
    box(slide, x, y, w, h, bg, None, 0.08)
    bar(slide, x, y + Inches(0.12), Inches(0.06), h - Inches(0.24), fg)
    text(slide, x + Inches(0.25), y + Inches(0.14), w - Inches(0.4), h - Inches(0.28),
         [P(label.upper(), 9.5, fg, True, after=4), P(body, 11, INK, ls=1.12)],
         anchor=MSO_ANCHOR.MIDDLE)


def chart_card(slide, path, x, y, w, h, caption=None):
    box(slide, x, y, w, h)
    pad = Inches(0.18)
    cap_h = Inches(0.35) if caption else 0
    picture(slide, path, x + pad, y + pad, w - 2 * pad, h - 2 * pad - cap_h)
    if caption:
        text(slide, x + pad, y + h - pad - Inches(0.28), w - 2 * pad, Inches(0.28),
             [P(caption, 9, MUTED, italic=True, align=PP_ALIGN.CENTER)])


def stat_card(slide, x, y, w, h, value, label, sub, accent=BLUE):
    box(slide, x, y, w, h)
    bar(slide, x + Inches(0.25), y + Inches(0.25), Inches(0.5), Inches(0.05), accent)
    text(slide, x + Inches(0.25), y + Inches(0.4), w - Inches(0.5), h - Inches(0.5),
         [P(value, 30, NAVY, True, after=2), P(label, 11.5, INK, True, after=2), P(sub, 9.5, BODY)])


# ================================================================== slides
def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH
    blank = prs.slide_layouts[6]
    fig = lambda n: os.path.join(FIGS, n)

    # ---------------------------------------------------------- 1 COVER
    s = prs.slides.add_slide(blank)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    shape(s, MSO_SHAPE.OVAL, Inches(9.2), Inches(-1.6), Inches(6.0), Inches(6.0), NAVY_2)
    shape(s, MSO_SHAPE.OVAL, Inches(10.8), Inches(4.4), Inches(3.6), Inches(3.6), NAVY_2)
    bar(s, MX, Inches(1.9), Inches(0.9), Inches(0.07), BLUE)
    text(s, MX, Inches(2.15), Inches(10), Inches(0.4),
         [P("DATA ANALYTICS PORTFOLIO  •  PUBLIC HEALTH", 12, BLUE_LT, True)])
    text(s, MX, Inches(2.6), Inches(12.2), Inches(1.6),
         [P("Dari Inspeksi ke Aksi:", 36, WHITE, True, ls=1.0),
          P("Membuat Restoran San Francisco Lebih Aman", 36, WHITE, True, ls=1.0)])
    text(s, MX, Inches(4.35), Inches(10), Inches(0.8),
         [P("Analisis 25.834 sesi inspeksi kesehatan restoran (2014–2016) untuk membantu "
            "SF Department of Public Health memprioritaskan pengawasan.", 15, BLUE_LT, ls=1.2)])
    bar(s, MX, Inches(5.65), Inches(4.5), Inches(0.01), NAVY_2)
    text(s, MX, Inches(5.8), Inches(8), Inches(0.9),
         [P("Gilang Anugrah", 16, WHITE, True, after=2),
          P("Data Analyst  |  Python · SQL · Power BI · DAX", 11.5, MUTED)])
    notes(s, "Selamat pagi/siang. Saya Gilang Anugrah. Hari ini saya akan bercerita bagaimana data "
             "inspeksi restoran bisa membantu Dinas Kesehatan San Francisco bekerja lebih cerdas: "
             "mengirim inspektur ke tempat dan waktu yang paling membutuhkan.")

    # ---------------------------------------------------------- 2 KEY QUESTION
    s = prs.slides.add_slide(blank)
    chrome(s, 2, "Latar Belakang", "Inspektur terbatas, restoran ribuan: di mana kita harus fokus?")
    box(s, MX, Inches(1.75), CW, Inches(1.45), NAVY, None, 0.06)
    text(s, MX + Inches(0.45), Inches(1.75), CW - Inches(0.9), Inches(1.45),
         [P("PERTANYAAN UTAMA", 10, BLUE_LT, True, after=6),
          P("Bagaimana SFDPH bisa melindungi konsumen secara maksimal dengan jumlah inspektur yang terbatas?",
            19, WHITE, True, ls=1.1)], anchor=MSO_ANCHOR.MIDDLE)
    qs = [("01", "Seberapa sehat?", "Bagaimana kondisi kepatuhan restoran di seluruh kota?", "Babak 1"),
          ("02", "Apa masalahnya?", "Pelanggaran apa yang paling sering & paling berbahaya?", "Babak 2"),
          ("03", "Di mana & kapan?", "Wilayah dan bulan mana yang risikonya paling tinggi?", "Babak 3"),
          ("04", "Apakah berhasil?", "Apakah inspeksi ulang benar-benar memperbaiki restoran?", "Babak 4")]
    cw = (CW - Inches(0.3) * 3) / 4
    for i, (n, h, d, ch) in enumerate(qs):
        x = MX + i * (cw + Inches(0.3))
        box(s, x, Inches(3.5), cw, Inches(3.15))
        text(s, x + Inches(0.3), Inches(3.5), cw - Inches(0.6), Inches(3.15),
             [P(n, 36, BLUE, True, after=10), P(h, 18, NAVY, True, after=8),
              P(d, 12.5, BODY, ls=1.15, after=16), P(ch.upper(), 9.5, MUTED, True)],
             anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "SFDPH mengawasi lebih dari 6.000 usaha kuliner dengan jumlah inspektur yang terbatas. "
             "Jadi pertanyaannya bukan 'apakah kita perlu inspeksi', tapi 'ke mana dan kapan inspeksi "
             "paling berdampak'. Presentasi ini dibagi menjadi empat babak yang menjawab empat pertanyaan ini.")

    # ---------------------------------------------------------- 3 DATA
    s = prs.slides.add_slide(blank)
    chrome(s, 3, "Data & Pendekatan", "Tiga tahun catatan inspeksi resmi menjadi dasar analisis ini")
    stats = [("25.834", "Sesi inspeksi", "Setelah dibersihkan & digabung per kunjungan", BLUE),
             ("6.078", "Restoran unik", "Restoran, kafe, food truck, katering", BLUE),
             ("40.623", "Pelanggaran tercatat", "Lengkap dengan tingkat risikonya", AMBER),
             ("3 tahun", "Jan 2014 – Des 2016", "Mencakup tiga siklus musim penuh", GREEN)]
    cw = (CW - Inches(0.25) * 3) / 4
    for i, (v, l, sub, a) in enumerate(stats):
        stat_card(s, MX + i * (cw + Inches(0.25)), Inches(1.75), cw, Inches(1.85), v, l, sub, a)
    text(s, MX, Inches(3.95), CW, Inches(0.35), [P("BAGAIMANA DATA DIOLAH", 10, BLUE, True)])
    steps = [("Kumpulkan", "Data resmi SFDPH (format LIVES) dari Kaggle: 53.555 baris mentah"),
             ("Bersihkan", "Hapus duplikat, perbaiki kode pos & koordinat, gabungkan per sesi inspeksi"),
             ("Eksplorasi", "Analisis Python & SQL: pola pelanggaran, wilayah, musim, dan dampak"),
             ("Sajikan", "Dashboard Power BI interaktif + rekomendasi untuk pengambil keputusan")]
    sw_ = (CW - Inches(0.2) * 3) / 4
    for i, (h, d) in enumerate(steps):
        x = MX + i * (sw_ + Inches(0.2))
        chev = shape(s, MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON, x, Inches(4.4), sw_, Inches(0.55),
                     NAVY if i == 3 else BLUE, None)
        text(s, 0, 0, 0, 0, [P(f"{i + 1}. {h}", 12, WHITE, True, PP_ALIGN.CENTER)],
             anchor=MSO_ANCHOR.MIDDLE, shape_obj=chev)
        text(s, x + Inches(0.1), Inches(5.1), sw_ - Inches(0.3), Inches(0.9), [P(d, 10.5, BODY, ls=1.15)])
    callout(s, MX, Inches(6.0), CW, Inches(0.82), "Kenapa penting",
            "Di data mentah, 1 baris = 1 pelanggaran. Jika dihitung langsung, rata-rata skor terlihat 86,2 "
            "(seolah buruk). Setelah digabung per sesi inspeksi, skor sebenarnya adalah 91,3.")
    notes(s, "Datanya adalah catatan resmi SFDPH selama tiga tahun. Satu hal penting: di data mentah, "
             "satu restoran dengan lima pelanggaran muncul lima kali. Kalau tidak dibersihkan, kita akan "
             "menyimpulkan kota ini lebih kotor dari kenyataannya. Karena itu semua angka di presentasi ini "
             "dihitung per sesi inspeksi.")

    # ---------------------------------------------------------- 4 BABAK 1
    s = prs.slides.add_slide(blank)
    chrome(s, 4, "Babak 1  •  Seberapa sehat?",
           "Kabar baiknya: 2 dari 3 inspeksi berakhir dengan skor Baik/Sangat Baik", "Foto 01 & 02")
    half = (CW - Inches(0.25)) / 2
    chart_card(s, fig("01_distribusi_skor_inspeksi.png"), MX, Inches(1.75), half, Inches(3.2))
    chart_card(s, fig("02_proporsi_kategori_skor.png"), MX + half + Inches(0.25), Inches(1.75), half, Inches(3.2))
    ins = [("Rata-rata skor kota 91,3", "Median 93. Sebagian besar restoran menumpuk di skor 90–100.", GREEN),
           ("68% berstatus Baik/Sangat Baik", "10.050 dari 14.780 inspeksi bernilai ≥ 90.", BLUE),
           ("Tapi 275 inspeksi berskor < 70", "1,9% sesi tergolong 'Poor', kelompok kecil yang butuh tindakan cepat.", RED)]
    cw = (CW - Inches(0.25) * 2) / 3
    for i, (h, d, a) in enumerate(ins):
        x = MX + i * (cw + Inches(0.25))
        box(s, x, Inches(5.2), cw, Inches(1.6))
        bar(s, x, Inches(5.2) + Inches(0.2), Inches(0.06), Inches(1.2), a)
        text(s, x + Inches(0.3), Inches(5.2), cw - Inches(0.5), Inches(1.6),
             [P(h, 14, NAVY, True, after=4), P(d, 10.5, BODY, ls=1.15)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Mari mulai dari kabar baik. Rata-rata skor kota 91,3 dan dua pertiga inspeksi berakhir dengan "
             "skor Baik atau Sangat Baik. Artinya masalah sanitasi BUKAN masalah seluruh kota. "
             "Masalahnya terkonsentrasi pada kelompok kecil, dan itulah yang akan kita kejar di babak berikutnya.")

    # ---------------------------------------------------------- 5 BABAK 2a
    s = prs.slides.add_slide(blank)
    chrome(s, 5, "Babak 2  •  Apa masalahnya?",
           "Hanya 10 jenis pelanggaran menyumbang 58% dari seluruh temuan", "Foto 03")
    lw = Inches(7.7)
    chart_card(s, fig("03_top_10_pelanggaran.png"), MX, Inches(1.75), lw, Inches(5.05))
    rx, rw = MX + lw + Inches(0.3), CW - lw - Inches(0.3)
    text(s, rx, Inches(1.8), rw, Inches(0.3), [P("APA YANG KITA LIHAT", 10, BLUE, True)])
    numbered_insights(s, rx, Inches(2.2), rw, [
        ("Masalah kebersihan fisik dominan", "Lantai, dinding & langit-langit kotor jadi temuan #1 (3.545 kasus)."),
        ("Pola yang berulang", "Suhu makanan, wastafel cuci tangan, dan peralatan muncul terus-menerus."),
        ("Bahaya terbesar ada di urutan #10", "Suhu penyimpanan makanan berisiko tinggi: 1.629 kasus."),
    ], item_h=Inches(0.95))
    callout(s, rx, Inches(5.65), rw, Inches(1.15), "Artinya bagi SFDPH",
            "Fokus edukasi pada 10 pelanggaran ini bisa menekan lebih dari separuh temuan.")
    notes(s, "Dari 40.623 pelanggaran, hanya sepuluh jenis yang menyumbang 58%. Ini prinsip Pareto. "
             "Yang paling sering adalah masalah kebersihan fisik. Tapi perhatikan baris paling bawah: "
             "suhu penyimpanan makanan berisiko tinggi. Frekuensinya paling kecil di daftar ini, "
             "tapi dampaknya paling berbahaya. Itu yang kita bahas di slide berikutnya.")

    # ---------------------------------------------------------- 6 BABAK 2b
    s = prs.slides.add_slide(blank)
    chrome(s, 6, "Babak 2  •  Apa masalahnya?",
           "1 dari 6 inspeksi menemukan pelanggaran berisiko tinggi", "Foto 04")
    chart_card(s, fig("04_analisis_risiko_dan_high_risk.png"), MX, Inches(1.75), CW, Inches(3.55))
    cw = (CW - Inches(0.25) * 2) / 3
    items = [("13,8%", "pelanggaran berstatus High Risk", "5.600+ temuan yang langsung mengancam kesehatan konsumen.", RED, RED_BG),
             ("16,0%", "inspeksi menemukan ≥ 1 High Risk", "Sekitar 1 dari 6 kunjungan menemukan bahaya serius.", AMBER, AMBER_BG),
             ("Top 3", "bahaya kritis", "Suhu penyimpanan makanan, permukaan kontak kotor, dan metode pendinginan.", NAVY, BLUE_BG)]
    for i, (v, l, d, fg, bg) in enumerate(items):
        x = MX + i * (cw + Inches(0.25))
        box(s, x, Inches(5.5), cw, Inches(1.3), bg, None, 0.06)
        text(s, x + Inches(0.3), Inches(5.5), Inches(1.35), Inches(1.3), [P(v, 24, fg, True)], anchor=MSO_ANCHOR.MIDDLE)
        text(s, x + Inches(1.7), Inches(5.5), cw - Inches(1.9), Inches(1.3),
             [P(l, 11.5, NAVY, True, after=3), P(d, 9.5, BODY, ls=1.12)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Mayoritas pelanggaran, sekitar 86%, berisiko rendah atau sedang. Namun 13,8% berstatus High Risk, "
             "dan jika dilihat per kunjungan, 16% inspeksi menemukan setidaknya satu bahaya serius. "
             "Bahaya teratasnya adalah suhu penyimpanan makanan, penyebab klasik keracunan makanan. "
             "Pertanyaan berikutnya: di mana dan kapan bahaya ini paling sering terjadi?")

    # ---------------------------------------------------------- 7 BABAK 3a
    s = prs.slides.add_slide(blank)
    chrome(s, 7, "Babak 3  •  Di mana?",
           "Risiko tidak merata: 5 wilayah mencatat laju High Risk di atas 19%", "Foto 06")
    chart_card(s, fig("06_top_kodepos_high_risk.png"), MX, Inches(1.75), lw, Inches(5.05),
               caption="Hanya kode pos dengan ≥ 100 inspeksi. Rata-rata kota: 16,0%")
    text(s, rx, Inches(1.8), rw, Inches(0.3), [P("5 WILAYAH PRIORITAS", 10, BLUE, True)])
    areas = [("94104", "Financial District", "22,9%"), ("94122", "Sunset", "20,5%"),
             ("94116", "Parkside / Outer Sunset", "19,9%"), ("94133", "North Beach", "19,7%"),
             ("94108", "Chinatown", "19,2%")]
    for i, (zc, name, rate) in enumerate(areas):
        y = Inches(2.2) + i * Inches(0.58)
        box(s, rx, y, rw, Inches(0.5), RED_BG if i == 0 else WHITE, None if i == 0 else LINE, 0.15)
        text(s, rx + Inches(0.2), y, Inches(0.8), Inches(0.5), [P(zc, 11, RED if i == 0 else NAVY, True)], anchor=MSO_ANCHOR.MIDDLE)
        text(s, rx + Inches(1.0), y, rw - Inches(2.0), Inches(0.5), [P(name, 11, INK)], anchor=MSO_ANCHOR.MIDDLE)
        text(s, rx + rw - Inches(1.0), y, Inches(0.8), Inches(0.5), [P(rate, 11, RED, True, PP_ALIGN.RIGHT)], anchor=MSO_ANCHOR.MIDDLE)
    callout(s, rx, Inches(5.25), rw, Inches(1.55), "Artinya bagi SFDPH",
            "Financial District berisiko 1,4× rata-rata kota. Jadwal inspeksi sebaiknya berbasis risiko, bukan rotasi merata.",
            RED, RED_BG)
    notes(s, "Risiko ternyata tidak tersebar merata. Financial District, kode pos 94104, mencatat laju High Risk 22,9%, "
             "sekitar 1,4 kali rata-rata kota yang 16%. Disusul Sunset, Parkside, North Beach, dan Chinatown. "
             "Catatan metodologi: saya hanya memasukkan kode pos dengan minimal 100 inspeksi, karena kode pos "
             "dengan 5-8 restoran saja bisa menunjukkan angka 50% yang menyesatkan.")

    # ---------------------------------------------------------- 8 BABAK 3b
    s = prs.slides.add_slide(blank)
    chrome(s, 8, "Babak 3  •  Kapan?",
           "Temuan hama hampir 2× lipat di Mei–Juni dibanding Desember–Januari", "Foto 05")
    chart_card(s, fig("05_pola_musiman_hama.png"), MX, Inches(1.75), lw, Inches(5.05),
               caption="Jumlah kasus per bulan kalender, akumulasi 2014–2016")
    text(s, rx, Inches(1.8), rw, Inches(0.3), [P("APA YANG KITA LIHAT", 10, BLUE, True)])
    numbered_insights(s, rx, Inches(2.2), rw, [
        ("Puncak di bulan Juni: 353 kasus", "Mei–Juni rata-rata 343 kasus vs 176 di Des–Jan (+95%)."),
        ("Naik terus dari Januari ke Juni", "Kenaikan bertahap 5 bulan: ada waktu untuk bersiap."),
        ("Laju High Risk ikut naik", "Dari 12,5% (Januari) menjadi 17,7% (Juni)."),
    ], item_h=Inches(0.95))
    callout(s, rx, Inches(5.65), rw, Inches(1.15), "Artinya bagi SFDPH",
            "Pola ini bisa diprediksi. Pencegahan harus dimulai SEBELUM Mei, bukan setelahnya.", AMBER, AMBER_BG)
    notes(s, "Sekarang soal waktu. Temuan hama seperti tikus dan serangga naik konsisten sejak Februari dan memuncak "
             "di Juni dengan 353 kasus, hampir dua kali lipat dibanding musim dingin. Laju High Risk secara umum "
             "juga ikut naik. Karena polanya berulang, kita bisa bertindak lebih awal, bukan menunggu kasus meledak.")

    # ---------------------------------------------------------- 9 BABAK 4
    s = prs.slides.add_slide(blank)
    chrome(s, 9, "Babak 4  •  Apakah berhasil?",
           "Inspeksi ulang bekerja: 9 dari 10 restoran berskor buruk membaik", "Foto 07")
    chart_card(s, fig("07_efektivitas_intervensi_regulator.png"), MX, Inches(1.75), lw, Inches(5.05))
    text(s, rx, Inches(1.8), rw, Inches(0.3), [P("HASIL SETELAH INSPEKSI BERIKUTNYA", 10, BLUE, True)])
    half_r = (rw - Inches(0.2)) / 2
    for i, (v, l, a) in enumerate([("66 → 81", "Median skor naik", GREEN), ("91%", "Restoran membaik", BLUE)]):
        x = rx + i * (half_r + Inches(0.2))
        box(s, x, Inches(2.2), half_r, Inches(1.35))
        text(s, x + Inches(0.2), Inches(2.2), half_r - Inches(0.4), Inches(1.35),
             [P(v, 22, a, True, after=2), P(l, 10.5, BODY)], anchor=MSO_ANCHOR.MIDDLE)
    numbered_insights(s, rx, Inches(3.85), rw, [
        ("165 kasus dianalisis", "Restoran berskor < 70 yang punya data inspeksi berikutnya."),
        ("84% keluar dari zona 'Poor'", "Skor inspeksi berikutnya ≥ 70."),
    ], item_h=Inches(0.75))
    callout(s, rx, Inches(5.65), rw, Inches(1.15), "Artinya bagi SFDPH",
            "Kunjungan ulang adalah investasi yang terbukti memberi hasil. Pertahankan & percepat.", GREEN, GREEN_BG)
    notes(s, "Babak terakhir: apakah intervensi bekerja? Saya melacak 165 kasus restoran yang skornya di bawah 70, "
             "lalu melihat skor mereka di inspeksi berikutnya. Hasilnya, 91% membaik, median skor naik dari 66 ke 81, "
             "dan 84% keluar dari zona Poor. Sebagai catatan jujur, sebagian kenaikan bisa juga dipengaruhi faktor lain, "
             "tapi arah perbaikannya sangat konsisten.")

    # ---------------------------------------------------------- 10 SYNTHESIS
    s = prs.slides.add_slide(blank)
    chrome(s, 10, "Sintesis", "Gambaran utuh: risiko terkonsentrasi, bisa diprediksi, dan bisa diperbaiki")
    cols = [("APA", "Suhu makanan & kebersihan", ["10 pelanggaran = 58% temuan", "13,8% pelanggaran High Risk",
                                                  "Bahaya #1: suhu penyimpanan makanan"], RED),
            ("DI MANA", "5 wilayah prioritas", ["Financial District 22,9%", "Sunset, Parkside, North Beach, Chinatown",
                                                "Semua di atas rata-rata kota 16%"], AMBER),
            ("KAPAN", "Musim semi–panas", ["Hama naik dari Januari", "Puncak di bulan Juni",
                                           "Hampir 2× lipat vs musim dingin"], BLUE)]
    cw = (CW - Inches(0.3) * 2) / 3
    for i, (tag, h, pts, a) in enumerate(cols):
        x = MX + i * (cw + Inches(0.3))
        box(s, x, Inches(1.75), cw, Inches(3.45))
        bar(s, x, Inches(1.75), cw, Inches(0.07), a)
        text(s, x + Inches(0.35), Inches(1.85), cw - Inches(0.7), Inches(3.3),
             [P(tag, 11, a, True, after=8), P(h, 20, NAVY, True, after=14)] +
             [P("•  " + p, 13, BODY, after=9, ls=1.12) for p in pts], anchor=MSO_ANCHOR.MIDDLE)
    box(s, MX, Inches(5.45), CW, Inches(1.35), NAVY, None, 0.06)
    text(s, MX + Inches(0.45), Inches(5.45), Inches(2.2), Inches(1.35),
         [P("DAN KABAR BAIKNYA", 10, BLUE_LT, True)], anchor=MSO_ANCHOR.MIDDLE)
    text(s, MX + Inches(2.7), Inches(5.45), CW - Inches(3.1), Inches(1.35),
         [P("Intervensi terbukti efektif: 91% restoran berskor buruk membaik setelah diinspeksi ulang. "
            "Masalahnya bukan kurang tindakan, tetapi tindakan yang belum diarahkan secara presisi.",
            14, WHITE, True, ls=1.15)], anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Kalau semua babak digabung: kita tahu APA bahayanya, DI MANA ia berkumpul, dan KAPAN ia memuncak. "
             "Dan kita tahu intervensi bekerja. Jadi kesimpulannya, SFDPH tidak perlu bekerja lebih keras, "
             "tapi perlu bekerja lebih presisi.")

    # ---------------------------------------------------------- 11 RECOMMENDATIONS
    s = prs.slides.add_slide(blank)
    chrome(s, 11, "Rekomendasi", "Tiga langkah untuk mengarahkan inspeksi ke tempat & waktu yang tepat")
    recs = [("01", "Inspeksi Berbasis Risiko", "Tambah frekuensi inspeksi di 5 kode pos prioritas (94104, 94122, 94116, 94133, 94108).",
             "Laju High Risk 19–23% vs rata-rata kota 16%.", "Bahaya kritis terdeteksi lebih cepat di area paling rawan.", RED),
            ("02", "Kampanye Pencegahan Hama", "Kirim panduan & lakukan audit pengendalian hama setiap Maret–April, sebelum puncak musim.",
             "Temuan hama naik +95% di Mei–Juni.", "Puncak kasus musim panas bisa ditekan sejak awal.", AMBER),
            ("03", "Percepat Inspeksi Ulang", "Wajibkan inspeksi ulang dalam 14 hari untuk setiap restoran berskor < 70.",
             "91% restoran berskor buruk membaik setelah diinspeksi ulang.", "Restoran berbahaya lebih cepat kembali aman.", GREEN)]
    cw = (CW - Inches(0.3) * 2) / 3
    for i, (n, h, act, ev, imp, a) in enumerate(recs):
        x = MX + i * (cw + Inches(0.3))
        box(s, x, Inches(1.75), cw, Inches(5.05))
        bar(s, x, Inches(1.75), cw, Inches(0.07), a)
        text(s, x + Inches(0.35), Inches(2.0), cw - Inches(0.7), Inches(1.3),
             [P(n, 26, a, True, after=4), P(h, 16, NAVY, True)])
        text(s, x + Inches(0.35), Inches(3.25), cw - Inches(0.7), Inches(1.1),
             [P("AKSI", 9, MUTED, True, after=3), P(act, 11, INK, ls=1.15)])
        bar(s, x + Inches(0.35), Inches(4.45), cw - Inches(0.7), Inches(0.01), LINE)
        text(s, x + Inches(0.35), Inches(4.6), cw - Inches(0.7), Inches(0.9),
             [P("BUKTI DATA", 9, MUTED, True, after=3), P(ev, 10.5, BODY, ls=1.15)])
        text(s, x + Inches(0.35), Inches(5.6), cw - Inches(0.7), Inches(1.0),
             [P("DAMPAK YANG DIHARAPKAN", 9, a, True, after=3), P(imp, 10.5, INK, True, ls=1.15)])
    notes(s, "Dari temuan tadi, ada tiga rekomendasi. Pertama, jadwal inspeksi berbasis risiko dengan fokus pada lima kode pos prioritas. "
             "Kedua, kampanye pencegahan hama di Maret-April, sebelum puncak musim. Ketiga, percepat inspeksi ulang "
             "maksimal 14 hari untuk restoran berskor di bawah 70, karena datanya membuktikan langkah ini efektif.")

    # ---------------------------------------------------------- 12 ROADMAP
    s = prs.slides.add_slide(blank)
    chrome(s, 12, "Rencana Implementasi", "Roadmap 12 bulan dan indikator keberhasilan yang dipantau")
    phases = [("Jan – Feb", "Persiapan", "Tetapkan 5 wilayah prioritas & aktifkan dashboard monitoring"),
              ("Mar – Apr", "Pencegahan", "Kampanye & audit pengendalian hama sebelum musim puncak"),
              ("Mei – Jul", "Siaga Puncak", "Tambah frekuensi inspeksi di wilayah prioritas"),
              ("Agu – Des", "Evaluasi", "Bandingkan KPI dengan tahun sebelumnya, sesuaikan prioritas")]
    pw = (CW - Inches(0.2) * 3) / 4
    for i, (when, h, d) in enumerate(phases):
        x = MX + i * (pw + Inches(0.2))
        chev = shape(s, MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON, x, Inches(1.8), pw, Inches(0.6),
                     [BLUE, AMBER, RED, GREEN][i], None)
        text(s, 0, 0, 0, 0, [P(when, 12, WHITE, True, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE, shape_obj=chev)
        text(s, x + Inches(0.15), Inches(2.6), pw - Inches(0.4), Inches(1.2),
             [P(h, 14, NAVY, True, after=4), P(d, 10.5, BODY, ls=1.15)])
    text(s, MX, Inches(4.05), CW, Inches(0.3), [P("KPI YANG DIPANTAU DI DASHBOARD", 10, BLUE, True)])
    kpis = [("% Inspeksi High Risk", "Saat ini 16,0%", "Target: turun di 5 wilayah prioritas"),
            ("Lonjakan hama musiman", "Saat ini ~2× lipat", "Mei–Jun vs Des–Jan. Target: lebih landai"),
            ("Waktu ke inspeksi ulang", "Target ≤ 14 hari", "Untuk restoran skor < 70"),
            ("% Inspeksi skor ≥ 90", "Saat ini 68%", "Target: terus meningkat")]
    for i, (h, v, d) in enumerate(kpis):
        x = MX + i * (pw + Inches(0.2))
        box(s, x, Inches(4.45), pw, Inches(2.35))
        text(s, x + Inches(0.3), Inches(4.45), pw - Inches(0.6), Inches(2.35),
             [P(h, 13, NAVY, True, after=12), P(v, 22, BLUE, True, after=8), P(d, 11, BODY, ls=1.15)],
             anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "Ini contoh roadmap 12 bulan yang mengikuti pola musim dari data. Keberhasilannya diukur dengan empat KPI "
             "yang semuanya bisa dipantau langsung di dashboard Power BI.")

    # ---------------------------------------------------------- 13 DASHBOARD
    s = prs.slides.add_slide(blank)
    chrome(s, 13, "Alat Monitoring", "Dashboard Power BI untuk memantau risiko secara berkala", "Dashboard")
    dw = Inches(8.4)
    chart_card(s, fig("dashboard_powerbi.png"), MX, Inches(1.75), dw, Inches(5.05))
    rx2, rw2 = MX + dw + Inches(0.3), CW - dw - Inches(0.3)
    text(s, rx2, Inches(1.8), rw2, Inches(0.3), [P("YANG BISA DILAKUKAN", 10, BLUE, True)])
    feats = [("Pantau 4 KPI utama", "Inspeksi, skor rata-rata, pelanggaran, % High Risk."),
             ("Filter per periode", "Lihat kondisi per bulan atau tahun."),
             ("Lihat wilayah rawan", "Ranking kode pos berdasarkan laju High Risk."),
             ("Deteksi tren musiman", "Tren bulanan sebagai peringatan dini.")]
    for i, (h, d) in enumerate(feats):
        y = Inches(2.2) + i * Inches(1.15)
        c = shape(s, MSO_SHAPE.OVAL, rx2, y, Inches(0.3), Inches(0.3), BLUE_BG)
        text(s, 0, 0, 0, 0, [P("✓", 10, BLUE, True, PP_ALIGN.CENTER)], anchor=MSO_ANCHOR.MIDDLE, shape_obj=c)
        text(s, rx2 + Inches(0.45), y - Inches(0.03), rw2 - Inches(0.45), Inches(1.0),
             [P(h, 12, NAVY, True, after=3), P(d, 10.5, BODY, ls=1.12)])
    notes(s, "Semua temuan tadi tidak berhenti di slide ini. Saya membangun dashboard Power BI sehingga tim SFDPH bisa "
             "memantau KPI, wilayah rawan, dan tren musiman secara berkala, dan melihat apakah rekomendasi berjalan.")

    # ---------------------------------------------------------- 14 CLOSING
    s = prs.slides.add_slide(blank)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    shape(s, MSO_SHAPE.OVAL, Inches(9.2), Inches(-1.6), Inches(6.0), Inches(6.0), NAVY_2)
    bar(s, MX, Inches(1.6), Inches(0.9), Inches(0.07), BLUE)
    text(s, MX, Inches(1.85), Inches(11), Inches(0.4), [P("PESAN UTAMA", 12, BLUE_LT, True)])
    text(s, MX, Inches(2.3), Inches(11.5), Inches(1.9),
         [P("Inspeksi yang lebih presisi, bukan lebih banyak:", 28, WHITE, True, ls=1.05, after=4),
          P("tempat yang tepat, waktu yang tepat,", 28, BLUE_LT, True, ls=1.05),
          P("tindak lanjut yang cepat.", 28, BLUE_LT, True, ls=1.05)])
    text(s, MX, Inches(4.75), Inches(8), Inches(0.6), [P("Terima kasih. Mari berdiskusi.", 18, WHITE)])
    bar(s, MX, Inches(5.55), Inches(4.5), Inches(0.01), NAVY_2)
    text(s, MX, Inches(5.7), Inches(9), Inches(1.0),
         [P("Gilang Anugrah  |  Data Analyst", 14, WHITE, True, after=4),
          P("Email: [email Anda]   •   LinkedIn: [linkedin Anda]   •   GitHub: sf-restaurant-hygiene-analytics", 11, MUTED)])
    notes(s, "Kesimpulannya: SFDPH tidak perlu menambah inspeksi secara membabi buta. Dengan data, inspeksi bisa "
             "diarahkan ke tempat yang tepat, di waktu yang tepat, dengan tindak lanjut yang cepat. Terima kasih, "
             "saya terbuka untuk pertanyaan.")

    # ---------------------------------------------------------- 15 APPENDIX
    s = prs.slides.add_slide(blank)
    chrome(s, 15, "Lampiran", "Metodologi dan catatan data")
    half = (CW - Inches(0.3)) / 2
    box(s, MX, Inches(1.75), half, Inches(5.05))
    text(s, MX + Inches(0.35), Inches(2.0), half - Inches(0.7), Inches(4.7),
         [P("LANGKAH PEMBERSIHAN DATA", 11, BLUE, True, after=14)] +
         [P("•  " + t, 13, INK, after=12, ls=1.15) for t in [
             "Sumber: SF Restaurant Inspection Scores (LIVES), 53.555 baris × 17 kolom.",
             "50 baris duplikat identik dihapus.",
             "Kode pos dirapikan ke 5 digit; nilai dummy (0, 00000, CA) dijadikan kosong.",
             "Koordinat (0,0) dijadikan kosong agar tidak merusak peta.",
             "violation_id kosong = inspeksi tanpa pelanggaran (bukan data hilang).",
             "Data digabung per sesi inspeksi: 25.834 sesi untuk analisis skor & risiko.",
             "Tools: Python (Pandas), SQL (SQLite / T-SQL), Power BI (DAX)."]])
    x2 = MX + half + Inches(0.3)
    box(s, x2, Inches(1.75), half, Inches(5.05))
    text(s, x2 + Inches(0.35), Inches(2.0), half - Inches(0.7), Inches(4.7),
         [P("CATATAN & BATASAN", 11, AMBER, True, after=14)] +
         [P("•  " + t, 13, INK, after=12, ls=1.15) for t in [
             "Data mencakup 2014–2016; pola perlu divalidasi dengan data terbaru.",
             "Skor hanya diberikan pada inspeksi rutin (14.780 sesi bernilai).",
             "Analisis wilayah hanya untuk kode pos dengan ≥ 100 inspeksi agar tidak bias sampel kecil.",
             "% High Risk dihitung per sesi (16,0%) dan per pelanggaran (13,8%); keduanya dicantumkan jelas.",
             "Perbaikan skor setelah inspeksi ulang menunjukkan asosiasi kuat, belum tentu sebab-akibat murni.",
             "Nama wilayah adalah perkiraan berdasarkan kode pos."]])
    notes(s, "Slide lampiran ini untuk menjawab pertanyaan teknis: bagaimana data dibersihkan dan apa batasan analisisnya.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs.save(OUT)
    print("[OK] saved:", OUT)


if __name__ == "__main__":
    build()

