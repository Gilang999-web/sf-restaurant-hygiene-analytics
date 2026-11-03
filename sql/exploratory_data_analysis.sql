-- ==============================================================================
-- PROJECT: San Francisco Restaurant Hygiene & Safety Analytics
-- SCRIPT : Exploratory Data Analysis (EDA) using SQL
-- AUTHOR : Gilang Anugrah (Data Analyst Portfolio)
-- DATABASE ENGINE: SQLite / ANSI SQL Standard
-- TABLES : 
--   1. restaurant_inspections (Grain: 1 row = 1 violation, 53,505 rows)
--   2. inspections_summary   (Grain: 1 row = 1 inspection session, 25,834 rows)
-- ==============================================================================

-- ==============================================================================
-- SECTION 1: DATA OVERVIEW & SANITY CHECK (Ringkasan & Validasi Data)
-- Business Question: Berapa total inspeksi, restoran unik, dan rentang tanggal data?
-- ==============================================================================

-- Query 1.1: Ringkasan Metrik Volume Data Utama
SELECT 
    COUNT(DISTINCT inspection_id) AS total_inspections,
    COUNT(DISTINCT business_id) AS unique_restaurants,
    MIN(inspection_date) AS earliest_inspection,
    MAX(inspection_date) AS latest_inspection,
    ROUND(AVG(inspection_score), 2) AS citywide_avg_score
FROM inspections_summary;

-- Query 1.2: Rasio Sesi Inspeksi Bersih (0 Pelanggaran) vs Ada Pelanggaran
SELECT 
    CASE 
        WHEN is_clean_inspection = 1 THEN 'Clean Inspection (No Violations)'
        ELSE 'Violations Identified'
    END AS inspection_status,
    COUNT(*) AS total_sessions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inspections_summary), 2) AS percentage
FROM inspections_summary
GROUP BY is_clean_inspection;


-- ==============================================================================
-- SECTION 2: HYGIENE SCORE DISTRIBUTION (Distribusi Skor Kesehatan Restoran)
-- Business Question: Bagaimana profil kepatuhan restoran berdasarkan kategori skor?
-- ==============================================================================

-- Query 2.1: Analisis Tendensi Sentral Skor (Min, Max, Rata-rata)
SELECT 
    COUNT(inspection_score) AS scored_inspections,
    MIN(inspection_score) AS lowest_score,
    MAX(inspection_score) AS highest_score,
    ROUND(AVG(inspection_score), 2) AS mean_score
FROM inspections_summary
WHERE inspection_score IS NOT NULL;

-- Query 2.2: Pengelompokan Kepatuhan Skor (Benchmark Standar SFDPH)
SELECT 
    score_category,
    COUNT(*) AS total_sessions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inspections_summary WHERE inspection_score IS NOT NULL), 2) AS percentage
FROM inspections_summary
WHERE inspection_score IS NOT NULL
GROUP BY score_category
ORDER BY total_sessions DESC;


-- ==============================================================================
-- SECTION 3: PARETO ANALYSIS OF SANITATION VIOLATIONS (Pelanggaran Terbanyak)
-- Business Question: Pelanggaran apa yang paling sering terjadi dan berapa kontribusinya?
-- ==============================================================================

-- Query 3.1: Top 10 Pelanggaran dengan Cumulative Percentage (Analisis Pareto)
WITH violation_counts AS (
    SELECT 
        violation_description,
        risk_category,
        COUNT(*) AS violation_count
    FROM restaurant_inspections
    WHERE is_clean_inspection = 0
    GROUP BY violation_description, risk_category
)
SELECT 
    violation_description,
    risk_category,
    violation_count,
    ROUND(violation_count * 100.0 / SUM(violation_count) OVER (), 2) AS pct_of_total_violations,
    ROUND(SUM(violation_count) OVER (ORDER BY violation_count DESC) * 100.0 / SUM(violation_count) OVER (), 2) AS cumulative_pct
FROM violation_counts
ORDER BY violation_count DESC
LIMIT 10;

-- Query 3.2: Top 5 Pelanggaran Khusus Kategori Kritis (High Risk)
SELECT 
    violation_description,
    COUNT(*) AS occurrence_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM restaurant_inspections WHERE risk_category = 'High Risk'), 2) AS pct_within_high_risk
FROM restaurant_inspections
WHERE risk_category = 'High Risk'
GROUP BY violation_description
ORDER BY occurrence_count DESC
LIMIT 5;


-- ==============================================================================
-- SECTION 4: RISK SEVERITY PROFILING (Proporsi Tingkat Keparahan Risiko)
-- Business Question: Bagaimana distribusi pelanggaran berdasarkan tingkat risiko?
-- ==============================================================================

-- Query 4.1: Proporsi Pelanggaran Berdasarkan Tingkat Risiko (Severity)
SELECT 
    risk_category,
    COUNT(*) AS total_violations,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM restaurant_inspections WHERE is_clean_inspection = 0), 2) AS percentage
FROM restaurant_inspections
WHERE is_clean_inspection = 0
GROUP BY risk_category
ORDER BY total_violations DESC;

-- Query 4.2: Berapa persen sesi inspeksi yang memiliki minimal 1 pelanggaran High Risk?
SELECT 
    has_high_risk,
    COUNT(*) AS total_inspections,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inspections_summary), 2) AS high_risk_rate_pct
FROM inspections_summary
GROUP BY has_high_risk;


-- ==============================================================================
-- SECTION 5: GEOSPATIAL RISK HOTSPOTS (Wilayah Rawan Risiko Tinggi)
-- Business Question: Kode pos / distrik mana yang memiliki rasio bahaya tertinggi?
-- ==============================================================================

-- Query 5.1: Top 5 Kode Pos dengan High Risk Rate Tertinggi (Sample Threshold >= 100)
SELECT 
    CAST(business_postal_code AS INTEGER) AS postal_code,
    COUNT(*) AS total_inspections,
    SUM(has_high_risk) AS high_risk_inspections,
    ROUND(SUM(has_high_risk) * 100.0 / COUNT(*), 2) AS high_risk_rate_pct,
    DENSE_RANK() OVER (ORDER BY SUM(has_high_risk) * 100.0 / COUNT(*) DESC) AS risk_rank
FROM inspections_summary
WHERE business_postal_code IS NOT NULL
GROUP BY postal_code
HAVING total_inspections >= 100
ORDER BY high_risk_rate_pct DESC
LIMIT 5;


-- ==============================================================================
-- SECTION 6: TEMPORAL & SEASONALITY PATTERNS (Pola Musiman Lonjakan Hama)
-- Business Question: Kapan lonjakan bahaya sanitasi terjadi sepanjang tahun?
-- ==============================================================================

-- Query 6.1: Tren Laju Pelanggaran High Risk Bulanan (Januari - Desember)
SELECT 
    inspection_month,
    COUNT(*) AS total_inspections,
    SUM(has_high_risk) AS high_risk_inspections,
    ROUND(SUM(has_high_risk) * 100.0 / COUNT(*), 2) AS monthly_high_risk_rate_pct
FROM inspections_summary
GROUP BY inspection_month
ORDER BY inspection_month;

-- Query 6.2: Analisis Musiman Pelanggaran Hama (Vermin / Rodents / Insects)
SELECT 
    inspection_month,
    COUNT(*) AS vermin_incidents,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_annual_vermin
FROM restaurant_inspections
WHERE LOWER(violation_description) LIKE '%vermin%'
GROUP BY inspection_month
ORDER BY inspection_month;


-- ==============================================================================
-- SECTION 7: ENFORCEMENT & REMEDIATION IMPACT (Dampak Tindakan Korektif SFDPH)
-- Business Question: Apakah inspeksi ulang berhasil memperbaiki skor restoran?
-- ==============================================================================

-- Query 7.1: Analisis Kenaikan Skor Restoran Bermasalah (<80) pada Inspeksi Berikutnya
WITH sequential_inspections AS (
    SELECT 
        business_id,
        inspection_date,
        inspection_score,
        LAG(inspection_score) OVER (PARTITION BY business_id ORDER BY inspection_date) AS prev_score,
        LAG(inspection_date) OVER (PARTITION BY business_id ORDER BY inspection_date) AS prev_date
    FROM inspections_summary
    WHERE inspection_score IS NOT NULL
)
SELECT 
    COUNT(*) AS total_followup_sessions,
    ROUND(AVG(prev_score), 2) AS avg_prior_failed_score,
    ROUND(AVG(inspection_score), 2) AS avg_followup_score,
    ROUND(AVG(inspection_score - prev_score), 2) AS avg_score_improvement_points
FROM sequential_inspections
WHERE prev_score < 80;

