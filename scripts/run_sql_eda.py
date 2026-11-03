"""
Script untuk menjalankan seluruh query SQL Exploratory Data Analysis (EDA)
secara otomatis terhadap database SQLite (data/processed/sf_inspections.db)
"""

import os
import sqlite3
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

DB_PATH = os.path.join(BASE_DIR, "data", "processed", "sf_inspections.db")
SQL_FILE = os.path.join(BASE_DIR, "sql", "exploratory_data_analysis.sql")


def init_database_if_needed(conn):
    # Memeriksa apakah tabel sudah ada di database, jika belum buat otomatis dari CSV
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurant_inspections';")
    if not cursor.fetchone():
        print("[INIT] Mengimpor file CSV ke dalam database SQLite...")
        clean_csv = os.path.join(BASE_DIR, "data", "processed", "sf_restaurant_inspections_cleaned.csv")
        summary_csv = os.path.join(BASE_DIR, "data", "processed", "sf_inspections_summary.csv")
        
        df_clean = pd.read_csv(clean_csv)
        df_summary = pd.read_csv(summary_csv)
        
        df_clean.to_sql("restaurant_inspections", conn, if_exists="replace", index=False)
        df_summary.to_sql("inspections_summary", conn, if_exists="replace", index=False)
        print("[INIT] Database siap digunakan!")


def run_sql_eda():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    init_database_if_needed(conn)

    print("=" * 75)
    print(" SAN FRANCISCO RESTAURANT INSPECTIONS - SQL DATA EXPLORATION (EDA)")
    print("=" * 75)

    queries = [
        (
            "1.1 DATASET VOLUME & TIMELINE",
            """
            SELECT 
                COUNT(DISTINCT inspection_id) AS total_inspections,
                COUNT(DISTINCT business_id) AS unique_restaurants,
                MIN(inspection_date) AS earliest_date,
                MAX(inspection_date) AS latest_date,
                ROUND(AVG(inspection_score), 2) AS citywide_avg_score
            FROM inspections_summary;
            """
        ),
        (
            "1.2 CLEAN INSPECTIONS (0 VIOLATIONS) VS WITH VIOLATIONS",
            """
            SELECT 
                CASE 
                    WHEN is_clean_inspection = 1 THEN 'Clean (No Violations)'
                    ELSE 'Violations Identified'
                END AS inspection_status,
                COUNT(*) AS total_sessions,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inspections_summary), 2) AS percentage
            FROM inspections_summary
            GROUP BY is_clean_inspection;
            """
        ),
        (
            "2.2 HYGIENE SCORE COMPLIANCE TIERS",
            """
            SELECT 
                score_category,
                COUNT(*) AS total_sessions,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inspections_summary WHERE inspection_score IS NOT NULL), 2) AS percentage
            FROM inspections_summary
            WHERE inspection_score IS NOT NULL
            GROUP BY score_category
            ORDER BY total_sessions DESC;
            """
        ),
        (
            "3.1 TOP 10 SANITATION VIOLATIONS & CUMULATIVE PARETO %",
            """
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
                ROUND(violation_count * 100.0 / SUM(violation_count) OVER (), 2) AS pct_total,
                ROUND(SUM(violation_count) OVER (ORDER BY violation_count DESC) * 100.0 / SUM(violation_count) OVER (), 2) AS cumulative_pct
            FROM violation_counts
            ORDER BY violation_count DESC
            LIMIT 10;
            """
        ),
        (
            "5.1 TOP 5 HIGH-RISK DISTRICTS (SAMPLE >= 100 INSPECTIONS)",
            """
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
            """
        ),
        (
            "6.2 SEASONALITY OF PEST & VERMIN VIOLATIONS",
            """
            SELECT 
                inspection_month,
                COUNT(*) AS vermin_incidents,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_annual_vermin
            FROM restaurant_inspections
            WHERE LOWER(violation_description) LIKE '%vermin%'
            GROUP BY inspection_month
            ORDER BY inspection_month;
            """
        ),
        (
            "7.1 RE-INSPECTION SCORE IMPROVEMENT (SCORE < 80)",
            """
            WITH sequential_inspections AS (
                SELECT 
                    business_id,
                    inspection_date,
                    inspection_score,
                    LAG(inspection_score) OVER (PARTITION BY business_id ORDER BY inspection_date) AS prev_score
                FROM inspections_summary
                WHERE inspection_score IS NOT NULL
            )
            SELECT 
                COUNT(*) AS re_inspections_analyzed,
                ROUND(AVG(prev_score), 2) AS avg_prior_failed_score,
                ROUND(AVG(inspection_score), 2) AS avg_followup_score,
                ROUND(AVG(inspection_score - prev_score), 2) AS avg_score_improvement
            FROM sequential_inspections
            WHERE prev_score < 80;
            """
        )
    ]

    for title, sql in queries:
        print(f"\n>>> QUERY: {title}")
        print("-" * 75)
        df_result = pd.read_sql_query(sql, conn)
        print(df_result.to_string(index=False))

    conn.close()
    print("\n" + "=" * 75)
    print(" SELURUH QUERY SQL EDA BERHASIL DIEKSEKUSI DENGAN SUKSES!")
    print(f" File query lengkap tersimpan di: {SQL_FILE}")
    print("=" * 75)


if __name__ == "__main__":
    run_sql_eda()

