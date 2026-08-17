import os
import pandas as pd
import mysql.connector
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "output" / "master_dashboard_final.csv"

def load_master():
    """
    Memuat data pembangunan terpadu Jawa Timur.
    Mencoba mengambil data dari database MySQL lokal (phpMyAdmin) terlebih dahulu.
    Jika koneksi database gagal atau database belum di-impor, data akan diambil dari file CSV lokal (fallback).
    """
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",  # Default XAMPP/phpMyAdmin password kosong
        "database": "kominfo_kependudukan_new"
    }
    
    conn = None
    try:
        # Mencoba membuat koneksi database
        conn = mysql.connector.connect(**db_config)
        
        # Query untuk menggabungkan tabel-tabel relasional sesuai dengan struktur preprocessing
        query = """
            SELECT 
                w.kode_wilayah, 
                w.nama_wilayah, 
                w.tipe_wilayah,
                p.jumlah_penduduk, 
                p.laju_pertumbuhan, 
                p.persentase_penduduk, 
                p.kepadatan_bps, 
                p.rasio_jenis_kelamin, 
                p.tahun,
                m.jumlah_penduduk_miskin,
                t.tpt,
                i.ipm,
                k.kepadatan_sipil_smt1,
                k.kepadatan_sipil_smt2,
                k.kepadatan_sipil_tahunan
            FROM wilayah w
            INNER JOIN bps_kependudukan p ON w.kode_wilayah = p.kode_wilayah
            LEFT JOIN bps_kemiskinan m ON w.kode_wilayah = m.kode_wilayah AND p.tahun = m.tahun
            LEFT JOIN bps_tpt t ON w.kode_wilayah = t.kode_wilayah AND p.tahun = t.tahun
            LEFT JOIN bps_ipm i ON w.kode_wilayah = i.kode_wilayah AND p.tahun = i.tahun
            LEFT JOIN (
                SELECT 
                    kode_wilayah, 
                    tahun,
                    MAX(CASE WHEN semester = 1 THEN kepadatan ELSE NULL END) AS kepadatan_sipil_smt1,
                    MAX(CASE WHEN semester = 2 THEN kepadatan ELSE NULL END) AS kepadatan_sipil_smt2,
                    AVG(kepadatan) AS kepadatan_sipil_tahunan
                FROM dispenduk_kepadatan
                GROUP BY kode_wilayah, tahun
            ) k ON w.kode_wilayah = k.kode_wilayah AND p.tahun = k.tahun
            WHERE p.tahun >= 2018
            ORDER BY w.kode_wilayah, p.tahun;
        """
        df = pd.read_sql(query, conn)
        # Perbaikan skala data jumlah penduduk tahun 2025 yang salah input (satuan vs ribuan)
        if 'jumlah_penduduk' in df.columns:
            df.loc[df['jumlah_penduduk'] > 10000, 'jumlah_penduduk'] /= 1000
        return df
    except Exception as e:
        # Jika koneksi gagal, gunakan fallback ke file CSV lokal
        # (Sangat membantu ketika pengguna belum setup phpMyAdmin)
        if CSV_PATH.exists():
            df_csv = pd.read_csv(CSV_PATH)
            if 'jumlah_penduduk' in df_csv.columns:
                df_csv.loc[df_csv['jumlah_penduduk'] > 10000, 'jumlah_penduduk'] /= 1000
            return df_csv
        else:
            raise FileNotFoundError(
                f"Data master tidak dapat ditemukan. \n"
                f"Koneksi Database Gagal: {e} \n"
                f"File Fallback CSV juga tidak ditemukan di: {CSV_PATH}"
            )
    finally:
        if conn and conn.is_connected():
            conn.close()
