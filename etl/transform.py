import os
import pandas as pd
import numpy as np

# Folder definitions
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "data_mentah")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

# Master data wilayah untuk standardisasi
master_wilayah = {
    '3501': {'name': 'Pacitan', 'type': 'Kabupaten'},
    '3502': {'name': 'Ponorogo', 'type': 'Kabupaten'},
    '3503': {'name': 'Trenggalek', 'type': 'Kabupaten'},
    '3504': {'name': 'Tulungagung', 'type': 'Kabupaten'},
    '3505': {'name': 'Blitar', 'type': 'Kabupaten'},
    '3506': {'name': 'Kediri', 'type': 'Kabupaten'},
    '3507': {'name': 'Malang', 'type': 'Kabupaten'},
    '3508': {'name': 'Lumajang', 'type': 'Kabupaten'},
    '3509': {'name': 'Jember', 'type': 'Kabupaten'},
    '3510': {'name': 'Banyuwangi', 'type': 'Kabupaten'},
    '3511': {'name': 'Bondowoso', 'type': 'Kabupaten'},
    '3512': {'name': 'Situbondo', 'type': 'Kabupaten'},
    '3513': {'name': 'Probolinggo', 'type': 'Kabupaten'},
    '3514': {'name': 'Pasuruan', 'type': 'Kabupaten'},
    '3515': {'name': 'Sidoarjo', 'type': 'Kabupaten'},
    '3516': {'name': 'Mojokerto', 'type': 'Kabupaten'},
    '3517': {'name': 'Jombang', 'type': 'Kabupaten'},
    '3518': {'name': 'Nganjuk', 'type': 'Kabupaten'},
    '3519': {'name': 'Madiun', 'type': 'Kabupaten'},
    '3520': {'name': 'Magetan', 'type': 'Kabupaten'},
    '3521': {'name': 'Ngawi', 'type': 'Kabupaten'},
    '3522': {'name': 'Bojonegoro', 'type': 'Kabupaten'},
    '3523': {'name': 'Tuban', 'type': 'Kabupaten'},
    '3524': {'name': 'Lamongan', 'type': 'Kabupaten'},
    '3525': {'name': 'Gresik', 'type': 'Kabupaten'},
    '3526': {'name': 'Bangkalan', 'type': 'Kabupaten'},
    '3527': {'name': 'Sampang', 'type': 'Kabupaten'},
    '3528': {'name': 'Pamekasan', 'type': 'Kabupaten'},
    '3529': {'name': 'Sumenep', 'type': 'Kabupaten'},
    '3571': {'name': 'Kota Kediri', 'type': 'Kota'},
    '3572': {'name': 'Kota Blitar', 'type': 'Kota'},
    '3573': {'name': 'Kota Malang', 'type': 'Kota'},
    '3574': {'name': 'Kota Probolinggo', 'type': 'Kota'},
    '3575': {'name': 'Kota Pasuruan', 'type': 'Kota'},
    '3576': {'name': 'Kota Mojokerto', 'type': 'Kota'},
    '3577': {'name': 'Kota Madiun', 'type': 'Kota'},
    '3578': {'name': 'Kota Surabaya', 'type': 'Kota'},
    '3579': {'name': 'Kota Batu', 'type': 'Kota'}
}

def get_kode_wilayah(raw_name):
    name = str(raw_name).strip().replace('\ufeff', '').lower()
    name = name.replace('kabupaten ', '').replace('kab. ', '').replace('kab ', '')
    
    # Direct match
    for code, info in master_wilayah.items():
        std_name = info['name'].lower()
        if name == std_name:
            return code
            
    # Smart match (handling cities)
    for code, info in master_wilayah.items():
        std_name = info['name'].lower()
        if std_name.replace('kota ', '') == name:
            return code
    return None

def main():
    print("=== Memulai Proses Preprocessing & ETL ===")
    
    # 1. Muat dan bersihkan data Penduduk BPS
    print("Membersihkan data Penduduk BPS...")
    df_pend_raw = pd.read_csv(os.path.join(DATASET_DIR, "Penduduk Jawa Timur 2018-2025.csv"))
    cleaned_pend = []
    for idx, row in df_pend_raw.iterrows():
        name = str(row['Kabupaten_Kota']).strip()
        if name.lower() in ['keterangan', 'jawa timur'] or pd.isna(row['Kabupaten_Kota']):
            continue
        code = get_kode_wilayah(name)
        if code:
            cleaned_pend.append({
                'kode_wilayah': code,
                'nama_wilayah': master_wilayah[code]['name'],
                'tipe_wilayah': master_wilayah[code]['type'],
                'jumlah_penduduk': float(row['Jumlah_Penduduk']),
                'laju_pertumbuhan': float(row['Laju_Pertumbuhan']),
                'persentase_penduduk': float(row['Persentase_Penduduk']),
                'kepadatan_bps': float(row['Kepadatan']),
                'rasio_jenis_kelamin': float(row['Rasio_Jenis_Kelamin']),
                'tahun': int(row['Tahun'])
            })
    df_pend = pd.DataFrame(cleaned_pend)
    
    # 2. Muat dan bersihkan data Kemiskinan BPS
    print("Membersihkan data Kemiskinan BPS...")
    df_miskin_raw = pd.read_csv(os.path.join(DATASET_DIR, "Angka Kemiskinan Jawa Timur 2017-2025.csv"))
    cleaned_miskin = []
    for idx, row in df_miskin_raw.iterrows():
        name = str(row.iloc[0]).strip()
        if name.lower() in ['jawa timur'] or pd.isna(row.iloc[0]):
            continue
        code = get_kode_wilayah(name)
        if code:
            cleaned_miskin.append({
                'kode_wilayah': code,
                'jumlah_penduduk_miskin': float(row.iloc[1]),
                'tahun': int(row.iloc[2])
            })
    df_miskin = pd.DataFrame(cleaned_miskin)
    
    # 3. Muat dan bersihkan data TPT BPS
    print("Membersihkan data TPT BPS...")
    df_tpt_raw = pd.read_csv(os.path.join(DATASET_DIR, "Tingkat Pengangguran Terbuka Jawa Timur 2017-2025.csv"))
    cleaned_tpt = []
    for idx, row in df_tpt_raw.iterrows():
        name = str(row.iloc[0]).strip()
        if name.lower() in ['jawa timur'] or pd.isna(row.iloc[0]):
            continue
        code = get_kode_wilayah(name)
        if code:
            cleaned_tpt.append({
                'kode_wilayah': code,
                'tpt': float(row.iloc[1]),
                'tahun': int(row.iloc[2])
            })
    df_tpt = pd.DataFrame(cleaned_tpt)
    
    # 4. Muat dan bersihkan data IPM BPS (Imputasi Pacitan dan Ponorogo)
    print("Membersihkan data IPM BPS...")
    df_ipm_raw = pd.read_csv(os.path.join(DATASET_DIR, "Indeks Pembangunan Manusia Jawa Timur 2017-2025.csv"))
    cleaned_ipm = []
    for idx, row in df_ipm_raw.iterrows():
        name = str(row.iloc[0]).strip()
        if name.lower() in ['jawa timur'] or pd.isna(row.iloc[0]):
            continue
        code = get_kode_wilayah(name)
        if code:
            cleaned_ipm.append({
                'kode_wilayah': code,
                'ipm': float(row.iloc[1]),
                'tahun': int(row.iloc[2])
            })
            
    # Input data IPM Pacitan (3501) dan Ponorogo (3502) dari BPS Jatim karena tidak lengkap
    pacitan_ipm = {2017: 66.51, 2018: 67.33, 2019: 68.16, 2020: 68.39, 2021: 69.45, 2022: 70.59, 2023: 70.84, 2024: 71.49, 2025: 71.90}
    ponorogo_ipm = {2017: 69.26, 2018: 69.91, 2019: 70.56, 2020: 70.81, 2021: 70.93, 2022: 71.71, 2023: 71.98, 2024: 72.40, 2025: 72.80}
    
    # Filter agar tidak duplikat jika data sudah ada
    existing_ipm_codes = {(r['kode_wilayah'], r['tahun']) for r in cleaned_ipm}
    for yr, val in pacitan_ipm.items():
        if ('3501', yr) not in existing_ipm_codes:
            cleaned_ipm.append({'kode_wilayah': '3501', 'ipm': val, 'tahun': yr})
    for yr, val in ponorogo_ipm.items():
        if ('3502', yr) not in existing_ipm_codes:
            cleaned_ipm.append({'kode_wilayah': '3502', 'ipm': val, 'tahun': yr})
            
    df_ipm = pd.DataFrame(cleaned_ipm)
    
    # 5. Muat dan bersihkan data kepadatan penduduk Dispendukcapil (SMT I & SMT II)
    print("Membersihkan data Kepadatan Penduduk Dispendukcapil...")
    df_kepadatan_smt1_raw = pd.read_csv(os.path.join(DATASET_DIR, "Kepadatan Penduduk Jawa Timur SMT I 2018-2025.csv"))
    df_kepadatan_smt2_raw = pd.read_csv(os.path.join(DATASET_DIR, "Kepadatan Penduduk Jawa Timur SMT II 2018-2025.csv"))
    
    standard_code_sequence = [
        '3501', '3502', '3503', '3504', '3505', '3506', '3507', '3508', '3509', '3510',
        '3511', '3512', '3513', '3514', '3515', '3516', '3517', '3518', '3519', '3520',
        '3521', '3522', '3523', '3524', '3525', '3526', '3527', '3528', '3529',
        '3571', '3572', '3573', '3574', '3575', '3576', '3577', '3578', '3579'
    ]
    
    mirror_code_sequence = [
        '3501', '3579', '3578', '3577', '3576', '3575', '3574', '3573', '3572', '3571',
        '3529', '3528', '3527', '3526', '3525', '3524', '3523', '3522', '3521', '3520',
        '3519', '3518', '3517', '3516', '3515', '3514', '3513', '3512', '3511', '3510',
        '3509', '3508', '3507', '3506', '3505', '3504', '3503', '3502'
    ]
    
    def clean_kepadatan(df, semester):
        cleaned = []
        for year, group in df.groupby('tahun'):
            group = group.reset_index(drop=True)
            year_val = int(year)
            
            # Align sequences based on known typos in data_mentah
            if semester == 1:
                if year_val in [2021, 2022]:
                    seq = mirror_code_sequence
                elif year_val == 2018:
                    seq = ['3579'] + standard_code_sequence[:29] + ['3571','3572','3573','3574','3575','3576','3577','3578']
                else:
                    seq = standard_code_sequence
            else: # semester == 2
                if year_val in [2020, 2024]:
                    seq = mirror_code_sequence
                elif year_val == 2019:
                    seq = ['3520'] + standard_code_sequence[1:19] + ['3501'] + standard_code_sequence[20:29] + ['3571','3572','3573','3574','3575','3576','3577','3578','3579']
                else:
                    seq = standard_code_sequence
                    
            for idx, row in group.iterrows():
                code = str(row['kode_kabupaten_kota'])
                if idx < len(seq):
                    code = seq[idx]
                
                density = float(row['jumlah_penduduk_per_km2'])
                cleaned.append({
                    'kode_wilayah': code,
                    f'kepadatan_sipil_smt{semester}': density,
                    'tahun': year_val
                })
        return pd.DataFrame(cleaned)
        
    df_kepadatan_smt1 = clean_kepadatan(df_kepadatan_smt1_raw, 1)
    df_kepadatan_smt2 = clean_kepadatan(df_kepadatan_smt2_raw, 2)
    
    df_kepadatan_sipil = pd.merge(df_kepadatan_smt1, df_kepadatan_smt2, on=['kode_wilayah', 'tahun'], how='outer')
    
    # Calculate yearly average density
    df_kepadatan_sipil['kepadatan_sipil_tahunan'] = df_kepadatan_sipil.apply(
        lambda r: r['kepadatan_sipil_smt1'] if pd.isna(r['kepadatan_sipil_smt2']) or r['kepadatan_sipil_smt2'] == 0 
                  else (r['kepadatan_sipil_smt1'] + r['kepadatan_sipil_smt2']) / 2,
        axis=1
    )
    
    # 6. Menggabungkan semua data menjadi satu Master Data
    print("Mengintegrasikan seluruh indikator menjadi Master Data...")
    df_master = pd.merge(df_pend, df_miskin, on=['kode_wilayah', 'tahun'], how='outer')
    df_master = pd.merge(df_master, df_tpt, on=['kode_wilayah', 'tahun'], how='outer')
    df_master = pd.merge(df_master, df_ipm, on=['kode_wilayah', 'tahun'], how='outer')
    df_master = pd.merge(df_master, df_kepadatan_sipil, on=['kode_wilayah', 'tahun'], how='outer')
    
    # Isi kembali informasi wilayah yang hilang setelah outer join
    for idx, row in df_master.iterrows():
        code = row['kode_wilayah']
        if code in master_wilayah:
            df_master.at[idx, 'nama_wilayah'] = master_wilayah[code]['name']
            df_master.at[idx, 'tipe_wilayah'] = master_wilayah[code]['type']
            
    df_master = df_master.sort_values(by=['kode_wilayah', 'tahun']).reset_index(drop=True)
    
    # Simpan master data kependudukan awal
    df_master.to_csv(os.path.join(OUTPUT_DIR, "master_data_kependudukan.csv"), index=False)
    print(f"Master Data awal disimpan ke: {os.path.join(OUTPUT_DIR, 'master_data_kependudukan.csv')}")
    
    # Filter data mulai dari tahun 2018 (agar tidak ada missing value demografi)
    df_final = df_master[df_master['tahun'] >= 2018].copy().reset_index(drop=True)
    df_final.to_csv(os.path.join(OUTPUT_DIR, "master_dashboard_final.csv"), index=False)
    print(f"Master Dashboard Final disimpan ke: {os.path.join(OUTPUT_DIR, 'master_dashboard_final.csv')}")
    
    # 7. Ekspor Relasional Data untuk Database
    print("Mengekspor tabel relasional untuk database SQL...")
    
    # Tabel Wilayah
    df_wilayah = pd.DataFrame([
        {'kode_wilayah': k, 'nama_wilayah': v['name'], 'tipe_wilayah': v['type']}
        for k, v in master_wilayah.items()
    ])
    df_wilayah.to_csv(os.path.join(OUTPUT_DIR, "wilayah.csv"), index=False)
    
    # Tabel Kependudukan BPS
    df_pend.to_csv(os.path.join(OUTPUT_DIR, "bps_kependudukan.csv"), index=False)
    
    # Tabel Kemiskinan BPS
    df_miskin.to_csv(os.path.join(OUTPUT_DIR, "bps_kemiskinan.csv"), index=False)
    
    # Tabel IPM BPS
    df_ipm.to_csv(os.path.join(OUTPUT_DIR, "bps_ipm.csv"), index=False)
    
    # Tabel TPT BPS
    df_tpt.to_csv(os.path.join(OUTPUT_DIR, "bps_tpt.csv"), index=False)
    
    # Tabel Kepadatan Dispendukcapil (Format Database Long)
    kepadatan_db_rows = []
    for idx, r in df_kepadatan_sipil.iterrows():
        if not pd.isna(r['kepadatan_sipil_smt1']):
            kepadatan_db_rows.append({
                'kode_wilayah': r['kode_wilayah'],
                'kepadatan': r['kepadatan_sipil_smt1'],
                'semester': 1,
                'tahun': int(r['tahun'])
            })
        if not pd.isna(r['kepadatan_sipil_smt2']):
            kepadatan_db_rows.append({
                'kode_wilayah': r['kode_wilayah'],
                'kepadatan': r['kepadatan_sipil_smt2'],
                'semester': 2,
                'tahun': int(r['tahun'])
            })
    df_kepadatan_db = pd.DataFrame(kepadatan_db_rows)
    df_kepadatan_db.to_csv(os.path.join(OUTPUT_DIR, "dispenduk_kepadatan.csv"), index=False)
    
    print("Seluruh file CSV database berhasil ditulis.")
    
    # 8. Generasikan File Dump SQL untuk phpMyAdmin
    print("Menggenerasikan file SQL dump untuk phpMyAdmin...")
    generate_sql_dump(df_wilayah, df_pend, df_miskin, df_ipm, df_tpt, df_kepadatan_db)
    
    print("=== Proses ETL Selesai dengan Sukses ===")

def generate_sql_dump(df_wilayah, df_pend, df_miskin, df_ipm, df_tpt, df_kepadatan_db):
    sql_path = os.path.join(DATABASE_DIR, "kominfo_kependudukan.sql")
    
    with open(sql_path, "w", encoding="utf-8") as f:
        # Header SQL
        f.write("-- SQL Dump untuk phpMyAdmin\n")
        f.write("-- Database: `kominfo_kependudukan_new`\n\n")
        f.write("CREATE DATABASE IF NOT EXISTS `kominfo_kependudukan_new`;\n")
        f.write("USE `kominfo_kependudukan_new`;\n\n")
        
        # Drop Tables
        f.write("DROP TABLE IF EXISTS `dispenduk_kepadatan`;\n")
        f.write("DROP TABLE IF EXISTS `bps_tpt`;\n")
        f.write("DROP TABLE IF EXISTS `bps_ipm`;\n")
        f.write("DROP TABLE IF EXISTS `bps_kemiskinan`;\n")
        f.write("DROP TABLE IF EXISTS `bps_kependudukan`;\n")
        f.write("DROP TABLE IF EXISTS `wilayah`;\n\n")
        
        # Create wilayah
        f.write("CREATE TABLE `wilayah` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `nama_wilayah` varchar(100) NOT NULL,\n")
        f.write("  `tipe_wilayah` enum('Kabupaten','Kota') NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # Create bps_kependudukan
        f.write("CREATE TABLE `bps_kependudukan` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `jumlah_penduduk` double NOT NULL,\n")
        f.write("  `laju_pertumbuhan` double NOT NULL,\n")
        f.write("  `persentase_penduduk` double NOT NULL,\n")
        f.write("  `kepadatan_bps` double NOT NULL,\n")
        f.write("  `rasio_jenis_kelamin` double NOT NULL,\n")
        f.write("  `tahun` int(11) NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`,`tahun`),\n")
        f.write("  CONSTRAINT `fk_pend_wilayah` FOREIGN KEY (`kode_wilayah`) REFERENCES `wilayah` (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # Create bps_kemiskinan
        f.write("CREATE TABLE `bps_kemiskinan` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `jumlah_penduduk_miskin` double NOT NULL,\n")
        f.write("  `tahun` int(11) NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`,`tahun`),\n")
        f.write("  CONSTRAINT `fk_miskin_wilayah` FOREIGN KEY (`kode_wilayah`) REFERENCES `wilayah` (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # Create bps_ipm
        f.write("CREATE TABLE `bps_ipm` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `ipm` double NOT NULL,\n")
        f.write("  `tahun` int(11) NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`,`tahun`),\n")
        f.write("  CONSTRAINT `fk_ipm_wilayah` FOREIGN KEY (`kode_wilayah`) REFERENCES `wilayah` (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # Create bps_tpt
        f.write("CREATE TABLE `bps_tpt` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `tpt` double NOT NULL,\n")
        f.write("  `tahun` int(11) NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`,`tahun`),\n")
        f.write("  CONSTRAINT `fk_tpt_wilayah` FOREIGN KEY (`kode_wilayah`) REFERENCES `wilayah` (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # Create dispenduk_kepadatan
        f.write("CREATE TABLE `dispenduk_kepadatan` (\n")
        f.write("  `kode_wilayah` varchar(10) NOT NULL,\n")
        f.write("  `kepadatan` double NOT NULL,\n")
        f.write("  `semester` int(11) NOT NULL,\n")
        f.write("  `tahun` int(11) NOT NULL,\n")
        f.write("  PRIMARY KEY (`kode_wilayah`,`semester`,`tahun`),\n")
        f.write("  CONSTRAINT `fk_kepadatan_wilayah` FOREIGN KEY (`kode_wilayah`) REFERENCES `wilayah` (`kode_wilayah`)\n")
        f.write(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
        
        # INSERT data wilayah
        f.write("-- Dumping data untuk table `wilayah`\n")
        wil_vals = []
        for _, r in df_wilayah.iterrows():
            wil_vals.append(f"('{r['kode_wilayah']}', '{r['nama_wilayah']}', '{r['tipe_wilayah']}')")
        f.write("INSERT INTO `wilayah` (`kode_wilayah`, `nama_wilayah`, `tipe_wilayah`) VALUES\n")
        f.write(",\n".join(wil_vals) + ";\n\n")
        
        # INSERT data bps_kependudukan
        f.write("-- Dumping data untuk table `bps_kependudukan`\n")
        pend_vals = []
        for _, r in df_pend.iterrows():
            pend_vals.append(f"('{r['kode_wilayah']}', {r['jumlah_penduduk']}, {r['laju_pertumbuhan']}, {r['persentase_penduduk']}, {r['kepadatan_bps']}, {r['rasio_jenis_kelamin']}, {r['tahun']})")
        f.write("INSERT INTO `bps_kependudukan` (`kode_wilayah`, `jumlah_penduduk`, `laju_pertumbuhan`, `persentase_penduduk`, `kepadatan_bps`, `rasio_jenis_kelamin`, `tahun`) VALUES\n")
        f.write(",\n".join(pend_vals) + ";\n\n")
        
        # INSERT data bps_kemiskinan
        f.write("-- Dumping data untuk table `bps_kemiskinan`\n")
        misk_vals = []
        for _, r in df_miskin.iterrows():
            misk_vals.append(f"('{r['kode_wilayah']}', {r['jumlah_penduduk_miskin']}, {r['tahun']})")
        f.write("INSERT INTO `bps_kemiskinan` (`kode_wilayah`, `jumlah_penduduk_miskin`, `tahun`) VALUES\n")
        f.write(",\n".join(misk_vals) + ";\n\n")
        
        # INSERT data bps_ipm
        f.write("-- Dumping data untuk table `bps_ipm`\n")
        ipm_vals = []
        for _, r in df_ipm.iterrows():
            ipm_vals.append(f"('{r['kode_wilayah']}', {r['ipm']}, {r['tahun']})")
        f.write("INSERT INTO `bps_ipm` (`kode_wilayah`, `ipm`, `tahun`) VALUES\n")
        f.write(",\n".join(ipm_vals) + ";\n\n")
        
        # INSERT data bps_tpt
        f.write("-- Dumping data untuk table `bps_tpt`\n")
        tpt_vals = []
        for _, r in df_tpt.iterrows():
            tpt_vals.append(f"('{r['kode_wilayah']}', {r['tpt']}, {r['tahun']})")
        f.write("INSERT INTO `bps_tpt` (`kode_wilayah`, `tpt`, `tahun`) VALUES\n")
        f.write(",\n".join(tpt_vals) + ";\n\n")
        
        # INSERT data dispenduk_kepadatan
        f.write("-- Dumping data untuk table `dispenduk_kepadatan`\n")
        kep_vals = []
        for _, r in df_kepadatan_db.iterrows():
            kep_vals.append(f"('{r['kode_wilayah']}', {r['kepadatan']}, {r['semester']}, {r['tahun']})")
        f.write("INSERT INTO `dispenduk_kepadatan` (`kode_wilayah`, `kepadatan`, `semester`, `tahun`) VALUES\n")
        f.write(",\n".join(kep_vals) + ";\n")
        
    print(f"Dump SQL berhasil digenerasikan di: {sql_path}")

if __name__ == "__main__":
    main()
