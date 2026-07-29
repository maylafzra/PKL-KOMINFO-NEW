# Panduan Aplikasi: Dashboard Monitoring Pembangunan Jawa Timur

Panduan ini berisi langkah-langkah untuk menyiapkan lingkungan kerja, memproses data (ETL), melakukan konfigurasi database MySQL pada phpMyAdmin, dan menjalankan dashboard Streamlit menggunakan Visual Studio Code (VSCode).

Sistem ini didesain menggunakan tema terang (Light Mode) yang formal dan bersih untuk kebutuhan dinas instansi pemerintahan (Dinas Komunikasi dan Informatika Provinsi Jawa Timur).

---

## 1. Struktur Proyek

Proyek ini terstruktur sebagai berikut:
- **`data_mentah/`**: Berisi file CSV mentah historis dari BPS dan Dispendukcapil Jatim (tidak menggunakan data bangunan liar).
- **`assets/`**: Berisi aset gambar resmi (Logo Kominfo Jatim, Logo Airlangga, Logo FTMM, dan gambar latar belakang).
- **`etl/`**: Script Python `transform.py` untuk preprocessing, integrasi data, dan otomatisasi pembuatan dump SQL database.
- **`database/`**: Berisi berkas SQL dump `kominfo_kependudukan.sql` hasil pembersihan untuk phpMyAdmin.
- **`output/`**: Menyimpan file CSV hasil pembersihan data relasional dan master dashboard.
- **`utils/`**: Utilitas untuk koneksi data (`load_data.py` dengan fallback otomatis database-ke-CSV) dan CSS kustom (`styling.py`).
- **`pages/`**: Kode antarmuka setiap halaman dashboard Streamlit (Home, Monitoring, Spasial, Prediksi, SPK).
- **`app.py`**: Berkas utama sebagai gerbang masuk aplikasi.
- **`requirements.txt`**: Daftar dependensi library Python.

---

## 2. Persyaratan Sistem dan Instalasi Dependensi

Langkah-langkah menyiapkan virtual environment di VSCode:

1. Buka folder `C:\VSCode\PKL-KOMINFO-NEW` di VSCode.
2. Buka terminal baru di VSCode (Terminal -> New Terminal).
3. Buat Virtual Environment baru dengan mengetikkan perintah berikut:
   ```bash
   python -m venv .venv
   ```
4. Aktifkan Virtual Environment tersebut:
   - **Command Prompt (cmd)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **PowerShell**:
     ```powershell
     .venv\Scripts\activate.ps1
     ```
5. Instal seluruh library yang diperlukan dengan perintah:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Eksekusi Proses ETL (Extract, Transform, Load)

Sebelum menjalankan aplikasi, pastikan Anda telah memproses data mentah terlebih dahulu untuk menghasilkan data master yang bersih serta file skema database SQL.

Jalankan perintah berikut di terminal:
```bash
python etl/transform.py
```
Proses ini akan otomatis menghasilkan:
1. File master bersih di folder `output/`.
2. File SQL dump `database/kominfo_kependudukan.sql` yang berisi pembuatan database, tabel, serta data baris yang siap di-import.

---

## 4. Konfigurasi Database pada phpMyAdmin

Untuk menghubungkan aplikasi dengan database relasional MySQL:

1. Jalankan panel kontrol XAMPP dan aktifkan modul **Apache** serta **MySQL**.
2. Buka peramban (browser) dan ketikkan alamat: `http://localhost/phpmyadmin/`.
3. Buat database baru:
   - Klik menu **New** pada panel sebelah kiri.
   - Ketik nama database: `kominfo_kependudukan_new`.
   - Klik tombol **Create**.
4. Impor data SQL:
   - Klik pada database `kominfo_kependudukan_new` yang baru dibuat.
   - Pilih tab **Import** pada menu bagian atas.
   - Klik **Choose File** dan pilih file `kominfo_kependudukan.sql` yang berada di direktori `C:\VSCode\PKL-KOMINFO-NEW\database\`.
   - Gulir ke bawah lalu klik tombol **Import** (atau **Go**).
   - Tunggu hingga proses impor selesai dengan pesan sukses.

*Catatan: Utilitas data pada aplikasi (`utils/load_data.py`) dilengkapi dengan fitur fallback otomatis. Jika database MySQL Anda mati atau belum dikonfigurasi, aplikasi akan otomatis membaca file CSV lokal pada folder `output/` sehingga aplikasi tidak akan mengalami crash dan tetap dapat digunakan.*

---

## 5. Menjalankan Dashboard Streamlit

Untuk menjalankan aplikasi web dashboard:

1. Pastikan Virtual Environment Anda dalam keadaan aktif.
2. Jalankan perintah Streamlit berikut pada terminal VSCode:
   ```bash
   streamlit run app.py
   ```
3. Aplikasi akan otomatis terbuka di peramban web default Anda pada alamat `http://localhost:8501`.
4. Gunakan panel navigasi samping di sebelah kiri untuk berpindah halaman:
   - **Home**: Halaman selamat datang dengan ringkasan informasi.
   - **Monitoring Pembangunan**: Visualisasi grafik tren historis makro dan profil kabupaten/kota.
   - **Analisis Spasial**: Peta sebaran spasial choropleth, nilai autokorelasi Moran's I, serta pengelompokan LISA Hotspot/Coldspot.
   - **Prediksi Kemiskinan**: Proyeksi jumlah penduduk miskin tahun 2026-2028 menggunakan machine learning serta metrik evaluasi model.
   - **Sistem Pendukung Keputusan**: Pengelompokan tingkat urgensi prioritas pembangunan berdasarkan proyeksi kemiskinan dan usulan rekomendasi kebijakan.
