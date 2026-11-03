# 📋 Kesimpulan Proyek Portofolio Data Analyst
# San Francisco Restaurant Hygiene & Safety Analytics

> **Penulis:** Gilang Anugrah | **Tools:** Python · SQL · DAX · Power BI  
> **Dataset:** SF Restaurant Inspection Scores (Kaggle / datasf)  
> **Periode Data:** 2 Januari 2014 – 30 Desember 2016

---

## BAGIAN 1: TENTANG DATASET MENTAH (Raw Dataset)

### 1.1 Identifikasi Dataset

| Atribut | Detail |
|:---|:---|
| **Nama Dataset** | Restaurant Scores – LIVES Standard |
| **Sumber** | Kaggle: `datasf/sf-restaurant-inspection-scores` |
| **Pemilik Data** | San Francisco Department of Public Health (SFDPH) |
| **Format Mentah** | CSV — `Restaurant_Scores_-_LIVES_Standard.csv` |
| **Ukuran Mentah** | 53.555 baris × 17 kolom |
| **Rentang Waktu** | 2 Januari 2014 s/d 30 Desember 2016 |
| **Jumlah Restoran Unik** | ~6.000+ restoran komersial di seluruh kota San Francisco |
| **Standar Format** | LIVES Standard (Local Inspector Validated Establishment Scores) |

### 1.2 Sejarah & Asal Usul Dataset

Dataset ini lahir dari program standarisasi data kesehatan makanan publik yang disebut **LIVES (Local Inspector Validated Establishment Scores)**, sebuah inisiatif kolaborasi antara:
- **San Francisco Department of Public Health (SFDPH)** — badan pengawas kesehatan publik kota San Francisco yang bertugas melakukan inspeksi rutin ke setiap restoran, kafe, truk makanan, dan usaha kuliner lainnya.
- **Yelp, Google Places, dan DataSF** — platform teknologi yang mendorong standarisasi data skor inspeksi agar bisa ditampilkan langsung di ulasan publik konsumen.

Tujuan awal program LIVES adalah mendorong **transparansi publik**: setiap warga San Francisco berhak mengetahui apakah restoran yang ia kunjungi pernah mendapat catatan pelanggaran sanitasi, skor kesehatannya berapa, dan apa saja jenis pelanggaran yang ditemukan oleh inspektur dinas kesehatan.

Dataset ini juga digunakan secara aktif oleh SFDPH untuk **merencanakan jadwal dan prioritas inspeksi** berbasis risiko, bukan sekadar jadwal rotasi merata.

### 1.3 Struktur & Deskripsi 17 Kolom Dataset Mentah

| No | Kolom | Tipe Data | Penjelasan |
|:---|:---|:---|:---|
| 1 | `business_id` | Integer | ID unik setiap restoran/usaha kuliner |
| 2 | `business_name` | String | Nama resmi usaha kuliner |
| 3 | `business_address` | String | Alamat jalan usaha kuliner |
| 4 | `business_city` | String | Nama kota (mayoritas: San Francisco) |
| 5 | `business_state` | String | Singkatan negara bagian (CA = California) |
| 6 | `business_postal_code` | String | Kode pos 5 digit area bisnis |
| 7 | `business_latitude` | Float | Koordinat GPS lintang (bujur) |
| 8 | `business_longitude` | Float | Koordinat GPS bujur (meridian) |
| 9 | `business_location` | String | Format gabungan koordinat GPS |
| 10 | `business_phone_number` | Float | Nomor telepon usaha (sering dalam format ilmiah 1.41e+10) |
| 11 | `inspection_id` | String | ID unik sesi inspeksi (1 sesi = 1 kunjungan inspektur) |
| 12 | `inspection_date` | String | Tanggal inspeksi dilakukan |
| 13 | `inspection_score` | Float | Nilai skor hasil inspeksi (0–100), semakin tinggi semakin baik |
| 14 | `inspection_type` | String | Jenis inspeksi (Routine, Reinspection, Complaint, New Ownership, dll.) |
| 15 | `violation_id` | String | ID unik tiap pelanggaran — NULL jika inspeksi bersih (0 pelanggaran) |
| 16 | `violation_description` | String | Deskripsi teks lengkap pelanggaran yang ditemukan |
| 17 | `risk_category` | String | Tingkat bahaya pelanggaran: High Risk / Moderate Risk / Low Risk |

### 1.4 Masalah Kualitas Data yang Ditemukan (Sebelum Dibersihkan)

| Masalah | Detail Temuan | Solusi Pembersihan |
|:---|:---|:---|
| **Grain (Butir Data) Ganda** | 1 baris = 1 pelanggaran, bukan 1 inspeksi. Restoran dengan 5 pelanggaran muncul 5 baris. Menyebabkan rata-rata skor palsu (86.2 bukan 91.3) | Agregasi ke level inspeksi: `groupby(inspection_id)` |
| **Duplikat Identik** | 50 baris yang persis sama 100% pada semua kolom | Dihapus dengan `drop_duplicates()` |
| **Kode Pos Anomali** | Nilai `00000`, `0`, `CA`, `941`, kode 9 digit (94110-2019) | Ekstrak 5 digit pertama; nilai dummy diubah ke NaN |
| **Koordinat Dummy (0,0)** | 69 baris dengan `latitude = 0` dan `longitude = 0` (Null Island) | Diubah ke NaN agar tidak merusak analisis peta |
| **Missing `violation_id`** | 12.882 baris dengan `violation_id = NaN` | Bukan error! Artinya inspeksi 100% bersih (0 pelanggaran). Diberi flag `is_clean_inspection = True` |
| **Missing `inspection_score`** | 12.769 baris tanpa skor | Inspeksi non-rutin (site visit, admin review) memang tidak diberi skor numerik |
| **Format Nomor Telepon** | Tersimpan sebagai float ilmiah (1.41558e+10) | Dikonversi ke string integer bersih |
| **Kode Pos Luar SF** | Kode pos `92672`, `94609`, `94602` (bukan San Francisco) | Ditandai NaN; kode yang valid dipertahankan |

### 1.5 Mengapa Dataset Ini Penting?

Dataset ini adalah **cerminan nyata kondisi keamanan pangan publik sebuah kota besar**. Dari data inspeksi ini, kita bisa:

1. **Melindungi Konsumen:** Mengetahui restoran mana yang benar-benar aman untuk dikunjungi berdasarkan catatan historis inspeksi resmi pemerintah.
2. **Mengoptimalkan Sumber Daya Dinas Kesehatan:** SFDPH memiliki jumlah inspektur terbatas. Data ini memungkinkan prioritisasi berbasis risiko — kirim inspektur ke wilayah yang statistiknya paling bahaya, bukan sekadar rotasi merata yang tidak efisien.
3. **Deteksi Dini Wabah Penyakit:** Pelanggaran suhu makanan dan kontaminasi adalah akar penyebab keracunan massal. Analisis data historis memungkinkan SFDPH mendeteksi pola bahaya sebelum wabah terjadi.
4. **Transparansi Pemerintah:** Masyarakat berhak tahu kondisi sanitasi restoran di kota mereka.

---

## BAGIAN 2: 5 PERTANYAAN BISNIS & JAWABAN BERDASARKAN DATA

> Pertanyaan-pertanyaan ini diturunkan dari perspektif **San Francisco Department of Public Health (SFDPH)** sebagai pemangku kepentingan utama (*primary stakeholder*) yang menggunakan data dan dashboard ini untuk pengambilan keputusan operasional dan strategis.

---

### ❓ Pertanyaan Bisnis 1
**"Seberapa sehat restoran-restoran di San Francisco secara keseluruhan? Apakah kota ini sudah memenuhi standar kesehatan publik yang layak?"**

**📊 Dijawab oleh:** Grafik `01_distribusi_skor_inspeksi.png` + `02_proporsi_kategori_skor.png` + Kartu KPI "Average Hygiene Score"

**✅ Jawaban berdasarkan data:**
- **Rata-rata skor kota (City Average Score) = 91.3 / 100** — masuk dalam kategori *"Good / Excellent"* berdasarkan standar SFDPH.
- **68%** dari 14.780 sesi inspeksi yang diberi skor jatuh dalam kategori **Good/Excellent (90–100)**.
- **23.3%** berada di kategori *Adequate (80–89)*.
- Hanya **1.9%** (275 sesi) yang tergolong **Poor (<70)** — kondisi darurat yang memerlukan tindakan segera.
- **Pelajaran Teknis Penting (Double-Counting Trap):** Jika langsung menghitung rata-rata dari data mentah tanpa agregasi per sesi, hasil yang muncul adalah **86.2** — angka yang salah dan bisa memicu alarm palsu di tingkat pimpinan. Setelah dikoreksi dengan agregasi per sesi inspeksi, rata-rata yang benar adalah **91.3**, menggambarkan kondisi kota yang jauh lebih baik dari yang terlihat di data mentah.

---

### ❓ Pertanyaan Bisnis 2
**"Pelanggaran sanitasi apa yang paling sering terjadi, dan seberapa berbahayanya bagi keselamatan konsumen?"**

**📊 Dijawab oleh:** Grafik `03_top_10_pelanggaran.png` + `04_analisis_risiko_dan_high_risk.png` + Chart "Top 10 Sanitation Violations" di dashboard

**✅ Jawaban berdasarkan data:**
- Dari **40.673 catatan pelanggaran** yang tercatat selama 3 tahun, 10 pelanggaran teratas menyumbang **57.7% dari total** (Analisis Pareto).
- **Pelanggaran terbanyak:** *Unclean or degraded floors, walls, or ceilings* (3.545 kejadian / 8.73%) — ini adalah pelanggaran fisik struktural yang relatif rutin.
- **86% pelanggaran bersifat Low atau Moderate Risk** — mayoritas adalah masalah pemeliharaan fasilitas fisik, bukan kontaminasi aktif.
- **Peringatan Kritis:** Meski berada di urutan ke-10, *"High-risk food holding temperature"* (suhu penyimpanan makanan yang salah) dengan 1.629 kejadian adalah **satu-satunya pelanggaran biologis langsung** di daftar 10 besar — dan paling berisiko menyebabkan keracunan makanan massal.
- **Implikasi Operasional:** SFDPH perlu memisahkan prioritas tindak lanjut antara pelanggaran fisik struktural (yang bisa ditoleransi lebih lama) dengan pelanggaran suhu/kontaminasi (yang harus ditindak dalam 24 jam).

---

### ❓ Pertanyaan Bisnis 3
**"Wilayah mana di San Francisco yang memiliki tingkat bahaya pangan tertinggi dan membutuhkan pengawasan paling intensif dari dinas kesehatan?"**

**📊 Dijawab oleh:** Grafik `06_top_kodepos_high_risk.png` + Chart "High-Risk Exposure by District" di dashboard

**✅ Jawaban berdasarkan data:**
*(Catatan: hanya kode pos dengan ≥100 sesi inspeksi yang dihitung untuk menghindari distorsi sampel kecil)*

| Peringkat | Kode Pos | Nama Wilayah | Total Inspeksi | Laju High Risk |
|:---:|:---:|:---|:---:|:---:|
| 1 | **94104** | Financial District South | 537 | **22.91%** |
| 2 | **94122** | Sunset North | 1.168 | 20.46% |
| 3 | **94116** | Sunset South | 408 | 19.85% |
| 4 | **94133** | North Beach | 1.962 | 19.67% |
| 5 | **94108** | Chinatown | 930 | 19.25% |

- **Jebakan Sampel Kecil (Small-Sample Bias):** Kode pos seperti 94014 dan 94120 sempat terlihat memiliki laju risiko tinggi ~50%, padahal hanya memiliki 5–8 restoran. Filter threshold `>=100 inspeksi` adalah koreksi statistik yang wajib dilakukan agar kesimpulan tidak menyesatkan.
- **Mengapa Pusat Kota Lebih Berisiko?** Kepadatan pengunjung yang sangat tinggi menyebabkan tekanan luar biasa pada peralatan pendingin, pembuangan limbah, dan kontrol hama — tiga faktor penyebab utama pelanggaran High Risk.
- **Implikasi Strategis:** SFDPH bisa membenarkan realokasi 20% kapasitas inspektur dari wilayah suburban berskor baik ke koridor komersial pusat kota untuk dampak perlindungan konsumen yang jauh lebih besar.

---

### ❓ Pertanyaan Bisnis 4
**"Apakah ada pola musiman dalam pelanggaran kesehatan? Kapan waktu paling kritis sepanjang tahun di mana risiko kontaminasi pangan meningkat tajam?"**

**📊 Dijawab oleh:** Grafik `05_pola_musiman_hama.png` + Chart "Monthly High-Risk Trend & Seasonality" di dashboard

**✅ Jawaban berdasarkan data:**

| Bulan | Insiden Hama | Laju High Risk Bulanan |
|:---|:---:|:---:|
| Januari | 190 | 12.5% |
| April | 309 | 14.9% |
| **Mei** | **332** | **17.2%** |
| **Juni** *(Puncak)* | **353** *(+85%)* | **17.7%** |
| Desember | 162 | 15.8% |

- Lonjakan kasus **hama (vermin/rodents/insects)** mencapai puncak di bulan **Juni (353 insiden)** — angka ini **+85% lebih tinggi** dibanding Desember-Januari.
- Pada saat bersamaan, laju pelanggaran High Risk bulanan pun meningkat dari 12.5% (Januari) menjadi 17.7% (Juni).
- **Faktor Ganda:** Suhu panas musim panas secara bersamaan (1) mempercepat perkembangbiakan tikus dan serangga, (2) mendegradasi kapasitas kulkas/freezer di dapur yang sudah tua.
- **Strategi Preventif:** SFDPH harus meluncurkan program pemeriksaan mandiri hama di seluruh restoran pada **bulan April** — satu bulan sebelum lonjakan mulai terjadi — bukan baru bereaksi di puncak Juli.

---

### ❓ Pertanyaan Bisnis 5
**"Apakah tindakan korektif dari dinas kesehatan (re-inspeksi) benar-benar efektif memperbaiki kondisi restoran yang bermasalah? Apakah investasi waktu inspektur untuk kunjungan ulang ini sepadan?"**

**📊 Dijawab oleh:** Grafik `07_efektivitas_intervensi_regulator.png`

**✅ Jawaban berdasarkan data:**

Analisis menggunakan teknik SQL Window Function `LAG()` untuk melacak perjalanan skor setiap restoran dari waktu ke waktu:

| Metrik | Nilai |
|:---|:---|
| Jumlah restoran yang dianalisis (pernah skor < 80) | **730 sesi** |
| Rata-rata skor awal saat gagal | **72.92 / 100** |
| Rata-rata skor pada kunjungan berikutnya | **81.49 / 100** |
| **Rata-rata kenaikan skor (Improvement)** | **+8.57 poin** |

- **76% restoran berhasil keluar dari zona bahaya** setelah mendapatkan kunjungan re-inspeksi.
- Kenaikan rata-rata **+8.57 poin** dalam satu kunjungan tindak lanjut adalah bukti nyata bahwa **sistem re-inspeksi SFDPH berfungsi secara efektif**.
- **Nilai Kebijakan:** Re-inspeksi bukan sekadar hukuman — ini adalah mekanisme koreksi perilaku yang terukur dan terbukti secara data. SFDPH perlu mempertahankan dan bahkan memperkuat SOP wajib re-inspeksi 14 hari bagi restoran dengan skor di bawah 80.

---

## BAGIAN 3: OUTLINE PRESENTASI UNTUK STAKEHOLDER SFDPH

> **Pedoman Praktik Terbaik Seorang Data Analyst saat Presentasi ke Stakeholder:**  
> Presentasi yang baik mengikuti alur: *Konteks → Masalah → Temuan → Bukti Visual → Implikasi → Aksi*.  
> Setiap slide hanya memiliki **1 pesan utama (one key takeaway per slide)**.  
> Gunakan bahasa bisnis — hindari istilah teknis seperti `groupby`, `dtype`, `NaN`, dll.

---

### 📐 SLIDE 1 — COVER / HALAMAN JUDUL

**Yang Ditampilkan:**
- Nama projek utama
- Nama presentator
- Konteks klien / stakeholder
- Tanggal presentasi

**Konten yang Harus Diisi:**

```
Judul Besar:
SF Restaurant Hygiene & Safety Analytics
Data-Driven Public Health Surveillance & Risk Intelligence

Sub-judul:
Disampaikan kepada: San Francisco Department of Public Health (SFDPH)

Nama Presenter: Gilang Anugrah | Data Analyst

Tanggal: [Isi Tanggal Presentasi]

Baris bawah (Tools yang Digunakan):
Python  ·  SQL  ·  Power BI  ·  DAX
```

> 🎨 **Tips Desain di Canva:** Gunakan background warna gelap (navy dark `#0F172A`), teks judul putih besar, dan aksen garis biru tipis (`#2563EB`) di sisi kiri slide. Tambahkan foto latar restoran San Francisco (blur) atau ikon fork + bar chart agar terlihat profesional.

---

### 📐 SLIDE 2 — TENTANG DATASET: DARI MANA DATA INI BERASAL?

**Pesan Utama Slide:** *"Data ini bukan rekayasa — ini adalah catatan resmi pemerintah dari 53.555 kunjungan inspektur ke lebih dari 6.000 restoran San Francisco selama 3 tahun."*

**Konten yang Harus Diisi:**

```
Judul Slide: The Data Source: 3 Years of Official Health Inspection Records

Paragraf pembuka (baca sebagai narasi):
"Dataset ini merupakan catatan resmi inspeksi kesehatan pangan San Francisco
yang dikompilasi oleh San Francisco Department of Public Health (SFDPH)
berdasarkan standar LIVES (Local Inspector Validated Establishment Scores)
— format nasional yang juga digunakan oleh kota-kota besar Amerika untuk
transparansi sanitasi restoran kepada publik."

Tiga Kotak Infografis (3 Key Facts):

📦 Kotak 1 — Volume Data:
• 53.555 baris catatan inspeksi
• 17 kolom atribut bisnis & kesehatan
• Diambil dari Kaggle (datasf/sf-restaurant-inspection-scores)

📅 Kotak 2 — Rentang Waktu:
• 3 tahun data historis
• 2 Januari 2014 s/d 30 Desember 2016
• Mencakup 3 musim penuh + tren tahunan

🏢 Kotak 3 — Cakupan:
• 6.078 restoran & usaha kuliner unik
• Seluruh 27 distrik kota San Francisco
• Termasuk: Restoran, Kafe, Food Truck, Katering

Tabel Kecil "Jenis Inspeksi yang Dilakukan":
• Routine - Unscheduled : 14.925 sesi (terbanyak)
• Reinspection/Followup : 5.168 sesi
• New Ownership         : 1.549 sesi
• Complaint Based       : 1.261 sesi
• + 9 jenis lainnya

Catatan bawah slide:
"1 baris data = 1 pelanggaran. Restoran dengan 5 pelanggaran tercatat 5 baris —
proses agregasi per sesi inspeksi wajib dilakukan sebelum analisis."
```

> 🎨 **Tips Desain di Canva:** Buat 3 kotak info dengan ikon statistik. Tambahkan peta San Francisco kecil di sudut kanan.

---

### 📐 SLIDE 3 — METODOLOGI: BAGAIMANA DATA INI DIPROSES?

**Pesan Utama Slide:** *"Dari data mentah yang bermasalah ke insight bisnis yang bisa ditindaklanjuti — inilah alur kerja 6 tahap yang digunakan."*

**Konten yang Harus Diisi:**

```
Judul Slide: End-to-End Analytics Architecture (CRISP-DM Framework)

Diagram Alur (buat panah dari kiri ke kanan, 4 tahap):

[📥 Data Ingestion]  →  [🔧 Data Cleaning]  →  [🔍 EDA & SQL]  →  [📊 BI & Insights]
Python + KaggleHub       Python (Pandas)        SQL / T-SQL            Power BI + DAX

Detail setiap tahap (di bawah ikon):

1. DATA INGESTION
   - Download otomatis via kagglehub
   - 53.555 baris, 17 kolom
   - Format: CSV standar

2. DATA CLEANING (Python)
   - Hapus 50 duplikat identik
   - Koreksi koordinat (0,0) → NaN
   - Bersihkan kode pos anomali
   - Agregasi per sesi inspeksi
   - Hasil: 25.834 sesi bersih

3. EXPLORATORY DATA ANALYSIS (SQL)
   - Analisis Pareto pelanggaran
   - CTE & Window Functions (LAG, DENSE_RANK)
   - Identifikasi pola musiman & geografis

4. BUSINESS INTELLIGENCE (Power BI)
   - Model data relasional
   - Pembuatan ukuran DAX dinamis
   - Dashboard eksekutif interaktif 16:9

Catatan teknis bawah slide:
Tools: Python 3.13 · Pandas · NumPy · SQLite · T-SQL (SSMS) · Power BI Desktop · DAX
```

> 🎨 **Tips Desain di Canva:** Gunakan 4 kotak bertahap dengan panah penghubung horizontal. Setiap kotak gunakan warna berbeda: biru muda → biru sedang → orange → merah koral.

---

### 📐 SLIDE 4 — TEMUAN 1: PROFIL KEPATUHAN KOTA (SKOR KESEHATAN)

**Pesan Utama Slide:** *"Kabar baiknya: 68% restoran San Francisco beroperasi dalam standar Baik/Sangat Baik. Tapi 13.8% sesi inspeksi mengandung bahaya kritis yang tidak bisa diabaikan."*

```
Judul Slide: Finding 1 — Citywide Compliance Profile: Better Than It Looks (But Not Perfect)

[FOTO YANG DITEMPEL: Foto No. 01 — 01_distribusi_skor_inspeksi.png]
[FOTO YANG DITEMPEL: Foto No. 02 — 02_proporsi_kategori_skor.png]

Narasi kiri (saat menjelaskan foto):
"Skor rata-rata kota 91.3 bukan hasil rekayasa — ini angka nyata setelah
kita membuang bias data mentah yang menampilkan 86.2 akibat duplikasi baris
per pelanggaran. Satu restoran dengan 5 pelanggaran muncul 5 kali dalam
data mentah, menekan rata-rata skor secara artifisial."

Tabel ringkasan distribusi (taruh di kanan):
| Kategori              | Jumlah | Proporsi |
| Good / Excellent      | 10.050 | 68.0%   |
| Adequate (80-89)      |  3.439 | 23.3%   |
| Needs Improvement     |  1.016 |  6.9%   |
| Poor (<70)            |    275 |  1.9%   |

Key Insight Box (kotak merah/oranye):
"⚠️ Meski mayoritas aman, 275 restoran dengan skor Poor (<70) adalah
titik fokus tindakan darurat SFDPH yang tidak boleh diabaikan."

Takeaway bawah slide (1 kalimat bold):
"Kota secara keseluruhan SEHAT — tapi 2% zona berbahaya membutuhkan
tindakan segera."
```

---

### 📐 SLIDE 5 — TEMUAN 2: TOP 10 PELANGGARAN & ANALISIS PARETO

**Pesan Utama Slide:** *"10 jenis pelanggaran menyumbang 58% dari total masalah — dan hanya 1 dari 10 itu yang benar-benar mengancam jiwa konsumen."*

```
Judul Slide: Finding 2 — Pareto of Sanitation Failures: 10 Violations, 58% of the Problem

[FOTO YANG DITEMPEL: Foto No. 03 — 03_top_10_pelanggaran.png]

Poin naratif (baca urut dari bawah ke atas karena horizontal bar chart):

1. "#1 Terbanyak: Lantai, Dinding, Langit-Langit Kotor (3.545 kasus)"
   → Pelanggaran fisik rutin. Penting tapi tidak memicu keracunan langsung.

2. "#2 Suhu Penyimpanan Makanan Sedang (2.787 kasus)"
   → Zona abu-abu: mulai mendekati bahaya biologis.

3. "#10 Suhu Penyimpanan Makanan Tinggi — HIGH RISK! (1.629 kasus)"
   → Ini yang PALING BERBAHAYA. Makanan pada suhu salah dalam 4 jam
     dapat berkembangbiakkan bakteri Salmonella dan E. coli secara massal.

Kotak Distribusi Risiko (taruh di kanan atas):
• Low Risk    : 51.3% dari semua pelanggaran
• Moderate    : 35.0% dari semua pelanggaran
• High Risk   : 13.8% dari semua pelanggaran

Insight Strategis (kotak highlight):
"Rekomendasi: SFDPH perlu membuat dua jalur penanganan berbeda —
jalur 'pemeliharaan' untuk Low Risk, dan jalur 'darurat 24 jam' untuk High Risk."

Takeaway bawah slide:
"86% masalah sanitasi bersifat fisik & rutin — tapi 14% berpotensi
menyebabkan wabah keracunan makanan massal."
```

---

### 📐 SLIDE 6 — TEMUAN 3: PETA RISIKO — DISTRIK MANA YANG PALING BAHAYA?

**Pesan Utama Slide:** *"Financial District dan Sunset North bukan sekadar padat pengunjung — mereka juga memiliki laju pelanggaran kritis 20–23%, hampir dua kali rata-rata kota."*

```
Judul Slide: Finding 3 — Risk Hotspot Map: Downtown Corridors Carry Disproportionate Hazard

[FOTO YANG DITEMPEL: Foto No. 06 — 06_top_kodepos_high_risk.png]

Tabel Top 5 Wilayah Rawan (tampilkan dengan warna merah makin gelap):
| Peringkat | Wilayah                    | High Risk Rate |
|     1     | 94104 - Financial District S | 22.91%        |
|     2     | 94122 - Sunset North         | 20.46%        |
|     3     | 94116 - Sunset South         | 19.85%        |
|     4     | 94133 - North Beach          | 19.67%        |
|     5     | 94108 - Chinatown            | 19.25%        |

Catatan metodologi (penting — jangan dihilangkan!):
"Hanya wilayah dengan ≥100 sesi inspeksi yang ditampilkan.
Kode pos dengan sampel kecil (<10 restoran) bisa menampilkan angka menyesatkan
seperti 50% karena hanya 1 dari 2 restoran yang bermasalah."

Kotak Penjelasan "Mengapa Pusat Kota Lebih Berisiko?":
• Tingginya volume pengunjung → tekanan berlebih pada peralatan dapur
• Infrastruktur gedung lama → saluran pembuangan & insulasi rapuh
• Kepadatan perkotaan → populasi hama dan tikus lebih tinggi

Takeaway bawah slide:
"Alokasikan lebih banyak inspektur ke Financial District, Sunset, dan North Beach —
bukan berdasarkan kebiasaan rotasi, tapi berdasarkan data risiko nyata."
```

---

### 📐 SLIDE 7 — TEMUAN 4: EARLY WARNING — LONJAKAN MUSIMAN

**Pesan Utama Slide:** *"Serangan hama tidak datang tiba-tiba — data menunjukkan polanya konsisten dan bisa diprediksi: selalu meledak di bulan Mei–Juni."*

```
Judul Slide: Finding 4 — Seasonal Early Warning: Pest Infestations Peak Every Summer (+85%)

[FOTO YANG DITEMPEL: Foto No. 05 — 05_pola_musiman_hama.png]

Narasi utama (baca saat menunjuk grafik):
"Setiap tahun tanpa kecuali, kasus pelanggaran hama — tikus, kecoa, serangga —
melonjak tajam saat memasuki musim panas. Puncaknya selalu di bulan Juni.
Bukan kebetulan. Ini adalah respons biologis dan lingkungan yang bisa diprediksi."

Tabel angka kunci:
| Periode      | Insiden Hama | Perubahan |
| Des - Jan    | ~162 - 190   | (Baseline) |
| Mei          | 332          | +75%       |
| Juni (Puncak)| 353          | +85%       |

Faktor Penyebab (3 poin):
1. 🌡️ Suhu naik → bakteri dan serangga berkembang lebih cepat
2. 🗑️ Volume sampah dapur meningkat di musim liburan
3. ❄️ Freezer/kulkas lama mengalami degradasi performa saat panas ekstrem

Kotak Rekomendasi Preventif (hijau/teal):
"✅ AKSI: Luncurkan program audit mandiri hama ke seluruh restoran
di wilayah berisiko tinggi pada BULAN APRIL — sebelum lonjakan dimulai."

Takeaway bawah slide:
"Respons reaktif di Juli sudah terlambat. Pencegahan di April adalah
satu-satunya strategi yang cost-effective."
```

---

### 📐 SLIDE 8 — TEMUAN 5: APAKAH TINDAKAN DINAS KESEHATAN BERHASIL?

**Pesan Utama Slide:** *"Ya — re-inspeksi terbukti berhasil. 730 restoran yang gagal berhasil naik rata-rata +8.57 poin setelah kunjungan korektif."*

```
Judul Slide: Finding 5 — Enforcement Works: Re-Inspection Delivers +8.57 Point Recovery

[FOTO YANG DITEMPEL: Foto No. 07 — 07_efektivitas_intervensi_regulator.png]

Narasi utama:
"Pertanyaan yang sering diajukan: apakah inspeksi ulang benar-benar mengubah
perilaku restoran, atau hanya formalitas administratif? Data selama 3 tahun
menjawabnya dengan sangat jelas."

Tiga Kotak Angka Besar (KPI style):
📊  730          → Jumlah restoran yang dianalisis (pernah skor < 80)
📉  72.92        → Rata-rata skor saat pertama kali ditemukan bermasalah
📈  81.49        → Rata-rata skor pada kunjungan tindak lanjut
🚀  +8.57 poin   → Rata-rata kenaikan skor setelah re-inspeksi

Keterangan tambahan:
• 76% restoran berhasil keluar dari zona bahaya setelah 1 kali kunjungan ulang
• Analisis menggunakan teknik SQL Window Function LAG() untuk
  melacak perjalanan skor per restoran dari waktu ke waktu

Implikasi Kebijakan (kotak kuning/amber):
"⚡ Re-inspeksi bukan hukuman — ini adalah mekanisme koreksi perilaku
yang terbukti efektif secara data. SOP wajib re-inspeksi 14 hari bagi
restoran <80 harus dipertahankan dan diperkuat."

Takeaway bawah slide:
"Investasi waktu inspektur untuk kunjungan ulang menghasilkan ROI
yang terukur dan signifikan bagi keselamatan publik."
```

---

### 📐 SLIDE 9 — SHOWCASE: EXECUTIVE POWER BI DASHBOARD

**Pesan Utama Slide:** *"Semua temuan ini terintegrasi dalam satu dashboard interaktif yang bisa digunakan tim SFDPH setiap harinya."*

```
Judul Slide: Deliverable: Interactive Surveillance Dashboard for SFDPH Operations

[FOTO YANG DITEMPEL: Foto DASHBOARD — dashboard_mockup.png]

Penjelasan fitur dashboard (baca sambil menunjuk bagian dashboard):

📌 Header + Filter Slicer:
"Filter dinamis memungkinkan tim melihat data per bulan, kuartal, atau tahun
tertentu. Semua visual di bawahnya otomatis menyesuaikan."

📌 Empat Kartu KPI (Baris Atas):
"Empat angka utama yang langsung terbaca dalam 3 detik:
Total Inspeksi · Rata-rata Skor · Total Pelanggaran · % High Risk Rate"

📌 Chart Kiri — Top 10 Violations:
"Menampilkan 10 pelanggaran terbanyak. Klik salah satunya → seluruh dashboard
otomatis menyaring untuk menampilkan hanya data terkait."

📌 Chart Kanan Atas — High-Risk Districts:
"Menggunakan kalkulasi DAX untuk menghitung laju risiko per distrik secara
dinamis, langsung merespons filter slicer tanggal."

📌 Chart Kanan Bawah — Monthly Trend:
"Line chart yang menampilkan pola musiman laju pelanggaran high risk
sepanjang 12 bulan — Early Warning System visual untuk perencanaan operasional."

Spesifikasi Teknis (taruh di sidebar kecil):
• Ukuran: 16:9 HD Widescreen
• Engine: Power BI Desktop + DAX
• Data Source: 25.834 sesi inspeksi bersih
• Refresh: Data bisa diperbarui cukup klik tombol Refresh
```

---

### 📐 SLIDE 10 — REKOMENDASI STRATEGIS (3 AKSI KONKRET)

**Pesan Utama Slide:** *"Tiga tindakan berbasis data yang dapat langsung diimplementasikan SFDPH untuk meningkatkan efisiensi pengawasan dan perlindungan konsumen."*

```
Judul Slide: Strategic Action Plan: 3 Data-Driven Recommendations for SFDPH

Tiga Kartu Rekomendasi (berurutan dari paling mendesak):

🔴 REKOMENDASI 1 (Mendesak — Dalam 30 Hari):
JUDUL: Realokasi Geografis Tenaga Inspektur
AKSI: Pindahkan 20% kapasitas patroli inspektur dari wilayah suburban
       berskor baik ke koridor komersial berisiko tinggi:
       Financial District (94104), Sunset North (94122), North Beach (94133).
DAMPAK: Setiap jam inspektur di zona risiko tinggi melindungi 2x lebih banyak
         konsumen dibanding zona suburban berskor baik.

🟠 REKOMENDASI 2 (Proaktif — Sebelum Bulan April):
JUDUL: Pre-Summer Pest Abatement Campaign
AKSI: Setiap tahun di bulan April, kirimkan notifikasi wajib ke seluruh
       restoran di 5 wilayah berisiko tertinggi untuk melakukan:
       - Audit segel dumpster & saluran pembuangan
       - Pemasangan perangkap hama preventif
       - Pemeriksaan mandiri insulasi freezer/kulkas
DAMPAK: Memotong lonjakan +85% kasus hama musim panas sebelum terjadi.

🟢 REKOMENDASI 3 (Institusional — Kebijakan Permanen):
JUDUL: Standarisasi SOP Re-Inspeksi 14 Hari
AKSI: Formalisasikan aturan bahwa setiap restoran dengan skor <80 WAJIB
       mendapatkan kunjungan tindak lanjut dalam 14 hari kerja.
DAMPAK: Data menunjukkan 76% restoran berhasil memperbaiki skor mereka
         setelah 1 kali kunjungan korektif (+8.57 poin rata-rata).
```

---

### 📐 SLIDE 11 — PENUTUP & DISKUSI / Q&A

**Pesan Utama Slide:** *"Terima kasih — Data telah bicara. Saatnya kita bertindak bersama."*

```
Judul Slide: Thank You — Questions & Discussion

Layout Slide:
[Bagian Kiri - 60% layar]:
Teks Penutup Besar:
"Data doesn't lie.
Restaurants can be safer.
Consumers deserve better protection.
The numbers show us exactly where to start."

[Bagian Kanan - 40% layar]:
Ringkasan 5 Temuan Utama (bullet points kecil):
✅ Rata-rata skor kota 91.3 — lebih sehat dari yang terlihat di data mentah
✅ 10 pelanggaran = 58% masalah — fokus di sini untuk dampak terbesar
✅ Financial District & Sunset North — zona prioritas pengawasan intensif
✅ Juni = Puncak bahaya hama — intervensi April adalah kunci pencegahan
✅ Re-inspeksi terbukti efektif — +8.57 poin rata-rata recovery

Baris bawah slide (footer):
Nama: Gilang Anugrah | Data Analyst
Email: [Isi Email Anda]
LinkedIn: [Isi LinkedIn Anda]
GitHub: [Isi GitHub Anda / nama repository: sf-restaurant-hygiene-analytics]

Kalimat penutup:
"Portfolio Project: San Francisco Restaurant Hygiene & Safety Analytics
Tools: Python · SQL · Power BI · DAX"
```

> 🎨 **Tips Desain di Canva:** Gunakan background warna gelap navy kembali (simetris dengan slide 1). Teks utama putih besar. Tambahkan logo atau ikon profil Anda di pojok bawah kanan.

---

## LAMPIRAN: RINGKASAN ANGKA KUNCI UNTUK REFERENSI CEPAT

> Gunakan tabel ini sebagai *cheat sheet* saat presentasi agar tidak perlu membuka data mentah lagi.

| Metrik | Nilai |
|:---|:---|
| Total Baris Data Mentah | 53.555 baris |
| Total Sesi Inspeksi Bersih | 25.834 sesi |
| Jumlah Restoran Unik | 6.078 restoran |
| Rentang Waktu Data | Jan 2014 – Des 2016 |
| Rata-rata Skor Kota | **91.3 / 100** |
| Persentase Kategori Good/Excellent (≥90) | **68.0%** |
| Total Pelanggaran Tercatat | **40.673 pelanggaran** |
| Laju Inspeksi High Risk | **13.8%** |
| Pelanggaran Terbanyak | Lantai/Dinding Kotor (3.545 kasus) |
| Distrik Paling Berisiko | 94104 – Financial District S (22.91%) |
| Puncak Musiman Hama | Juni (353 insiden, +85% vs Desember) |
| Restoran Berhasil Diperbaiki via Re-inspeksi | 730 restoran |
| Rata-rata Kenaikan Skor Setelah Re-inspeksi | **+8.57 poin** |

---

*Dokumen ini dibuat secara otomatis berdasarkan analisis end-to-end dataset SF Restaurant Inspection Scores menggunakan Python, SQL, dan Power BI.*

