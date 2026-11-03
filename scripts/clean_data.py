"""
Script Pembersihan Data (Data Cleaning)
Dataset: San Francisco Restaurant Inspection Scores (LIVES Standard)
Tujuan: Mengubah data mentah (raw) menjadi data bersih siap analisis (processed),
        serta membuat tabel ringkasan tingkat inspeksi (inspection-level summary).
"""

import os
import pandas as pd
import numpy as np


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)


def load_raw_data():
    # Menentukan path file data mentah secara dinamis terhadap root proyek
    raw_path = os.path.join(BASE_DIR, "data", "raw", "Restaurant_Scores_-_LIVES_Standard.csv")
    if not os.path.exists(raw_path):
        raw_path = os.path.join(BASE_DIR, "data", "Restaurant_Scores_-_LIVES_Standard.csv")

    print(f"[1/8] Membaca data mentah dari: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"      Dimensi awal: {df.shape[0]:,} baris x {df.shape[1]} kolom")
    return df


def remove_duplicates(df):
    # Mendeteksi dan menghapus baris duplikat yang persis sama
    initial_rows = len(df)
    df_clean = df.drop_duplicates().copy()
    dropped = initial_rows - len(df_clean)
    print(f"[2/8] Menghapus {dropped:,} baris duplikat identik.")
    print(f"      Sisa baris: {len(df_clean):,}")
    return df_clean


def clean_dates(df):
    # Mengonversi teks tanggal ke tipe data datetime dan mengekstrak komponen waktu
    print("[3/8] Melakukan standardisasi tipe tanggal & feature engineering waktu...")
    df["inspection_date"] = pd.to_datetime(df["inspection_date"], format="%m/%d/%Y %I:%M:%S %p")
    df["inspection_year"] = df["inspection_date"].dt.year
    df["inspection_month"] = df["inspection_date"].dt.month
    df["inspection_year_month"] = df["inspection_date"].dt.to_period("M").astype(str)
    df["inspection_day_name"] = df["inspection_date"].dt.day_name()
    df["inspection_quarter"] = "Q" + df["inspection_date"].dt.quarter.astype(str)
    print(f"      Rentang tanggal data: {df['inspection_date'].min().date()} s/d {df['inspection_date'].max().date()}")
    return df


def clean_postal_codes(df):
    # Membersihkan anomali kode pos (ekstrak 5 digit awal, ubah 'Ca'/'CA'/'941' jadi NaN)
    print("[4/8] Membersihkan kolom kode pos (business_postal_code)...")

    def _parse_zip(val):
        if pd.isnull(val):
            return np.nan
        val_str = str(val).strip()
        # Mengabaikan input singkatan state ('Ca'/'CA'), kode terpotong ('941'), atau kode dummy ('00000'/'0')
        if val_str.upper() in ["CA", "941", "0", "00000"] or val_str.startswith("0"):
            return np.nan
        # Mengambil 5 digit pertama jika format 9 digit (misal: 941102019 -> 94110)
        if len(val_str) >= 5 and val_str[:5].isdigit():
            return val_str[:5]
        return np.nan

    df["business_postal_code"] = df["business_postal_code"].apply(_parse_zip)
    valid_pc = df["business_postal_code"].notnull().sum()
    print(f"      Kode pos valid: {valid_pc:,} baris | Missing: {df['business_postal_code'].isnull().sum():,} baris")
    return df


def clean_geospatial_coordinates(df):
    # Mengoreksi koordinat dummy (0.0, 0.0 / Null Island) menjadi NaN agar tidak merusak visualisasi peta
    print("[5/8] Mengoreksi koordinat geografis dummy (0.0, 0.0)...")
    zero_coords = (df["business_latitude"] == 0) | (df["business_longitude"] == 0)
    num_zero = zero_coords.sum()
    df.loc[zero_coords, ["business_latitude", "business_longitude", "business_location"]] = np.nan
    print(f"      {num_zero} baris koordinat (0,0) diubah menjadi NaN")
    return df


def clean_text_and_contacts(df):
    # Menghapus spasi berlebih pada nama & alamat serta membersihkan format nomor telepon
    print("[6/8] Membersihkan format teks dan nomor telepon...")
    for text_col in ["business_name", "business_address", "business_city", "business_state"]:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).str.strip()

    # Mengubah format nomor telepon dari float ilmiah (1.41558e+10) menjadi string angka bersih
    def _format_phone(phone):
        if pd.isnull(phone):
            return np.nan
        try:
            return str(int(phone))
        except (ValueError, TypeError):
            return np.nan

    df["business_phone_number"] = df["business_phone_number"].apply(_format_phone)
    return df


def handle_violations_and_scores(df):
    # Menangani logika domain: membedakan inspeksi bersih vs inspeksi dengan pelanggaran,
    # serta membuat kategori skor inspeksi.
    print("[7/8] Membuat label kategori risiko dan kategori skor...")
    
    # Menandai apakah sesi inspeksi bebas pelanggaran (violation_id bernilai NaN)
    df["is_clean_inspection"] = df["violation_id"].isnull()
    
    # Mengisi NaN pada risk_category dengan label 'No Violation' agar jelas saat visualisasi
    df["risk_category_clean"] = df["risk_category"].fillna("No Violation")

    # Mengelompokkan skor inspeksi (0-100) ke dalam standar kepatuhan kesehatan
    def _categorize_score(score):
        if pd.isnull(score):
            return "Unscored / Non-Routine"
        elif score >= 90:
            return "Good / Excellent (90-100)"
        elif score >= 80:
            return "Adequate (80-89)"
        elif score >= 70:
            return "Needs Improvement (70-79)"
        else:
            return "Poor (<70)"

    df["score_category"] = df["inspection_score"].apply(_categorize_score)
    # Mengubah format skor ke integer bersih tanpa desimal .0 agar tidak salah baca di regional Indonesia
    df["inspection_score"] = df["inspection_score"].astype("Int64")
    return df


def create_inspection_summary(df):
    # Mengagregasi data dari level pelanggaran (53k baris) ke level inspeksi (25k baris unik)
    # Ini penting agar analisis skor atau agregasi wilayah tidak terdistorsi oleh duplikasi per pelanggaran
    print("[8/8] Membuat tabel agregasi tingkat inspeksi (grain: 1 baris = 1 sesi inspeksi)...")
    insp_summary = df.groupby("inspection_id").agg(
        business_id=("business_id", "first"),
        business_name=("business_name", "first"),
        business_address=("business_address", "first"),
        business_postal_code=("business_postal_code", "first"),
        business_latitude=("business_latitude", "first"),
        business_longitude=("business_longitude", "first"),
        inspection_date=("inspection_date", "first"),
        inspection_year=("inspection_year", "first"),
        inspection_month=("inspection_month", "first"),
        inspection_year_month=("inspection_year_month", "first"),
        inspection_day_name=("inspection_day_name", "first"),
        inspection_quarter=("inspection_quarter", "first"),
        inspection_type=("inspection_type", "first"),
        inspection_score=("inspection_score", "first"),
        score_category=("score_category", "first"),
        is_clean_inspection=("is_clean_inspection", "first"),
        total_violations=("violation_id", lambda x: x.notnull().sum()),
        high_risk_count=("risk_category", lambda x: (x == "High Risk").sum()),
        moderate_risk_count=("risk_category", lambda x: (x == "Moderate Risk").sum()),
        low_risk_count=("risk_category", lambda x: (x == "Low Risk").sum())
    ).reset_index()

    insp_summary["has_high_risk"] = insp_summary["high_risk_count"] > 0
    insp_summary["inspection_score"] = insp_summary["inspection_score"].astype("Int64")
    # Mengurutkan tabel berdasarkan business_id (angka) dan tanggal inspeksi
    insp_summary = insp_summary.sort_values(by=["business_id", "inspection_date"]).reset_index(drop=True)
    return insp_summary


def export_data(df_clean, df_summary):
    # Menyimpan kedua dataset bersih ke folder data/processed/
    output_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    clean_file = os.path.join(output_dir, "sf_restaurant_inspections_cleaned.csv")
    summary_file = os.path.join(output_dir, "sf_inspections_summary.csv")

    df_clean.to_csv(clean_file, index=False)
    df_summary.to_csv(summary_file, index=False)

    print("\n" + "=" * 60)
    print("PROSES DATA CLEANING SELESAI DENGAN SUKSES!")
    print("=" * 60)
    print(f"1. Dataset Detail Pelanggaran : {clean_file}")
    print(f"   Dimensi                     : {df_clean.shape[0]:,} baris x {df_clean.shape[1]} kolom")
    print(f"2. Dataset Ringkasan Inspeksi : {summary_file}")
    print(f"   Dimensi                     : {df_summary.shape[0]:,} baris x {df_summary.shape[1]} kolom")
    print("=" * 60)


def main():
    df = load_raw_data()
    df = remove_duplicates(df)
    df = clean_dates(df)
    df = clean_postal_codes(df)
    df = clean_geospatial_coordinates(df)
    df = clean_text_and_contacts(df)
    df = handle_violations_and_scores(df)
    df_summary = create_inspection_summary(df)
    export_data(df, df_summary)


if __name__ == "__main__":
    main()

