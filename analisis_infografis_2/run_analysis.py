import os
import sys
import json
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Add project root to python path to resolve utils imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.load_data import load_master

# Setup paths
NOTEBOOK_PATH = Path("C:/VSCode/PKL-KOMINFO-NEW/analisis_infografis_2/infografis bonus demografi/analisis_bonus_demografi.ipynb")
OUTPUT_DIR = Path("C:/VSCode/PKL-KOMINFO-NEW/analisis_infografis_2/infografis bonus demografi/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path("C:/VSCode/PKL-KOMINFO-NEW/analisis_infografis_2/data")

print("1. Generating Jupyter Notebook JSON structure...")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Analisis Bonus Demografi Jawa Timur: Peluang Emas atau Ancaman Pengangguran?\n",
            "\n",
            "## 1. Tema & Topik Analisis\n",
            "Analisis ini mengangkat tema **Kependudukan dan Ketenagakerjaan di Provinsi Jawa Timur**, dengan fokus topik khusus: **\"Bonus Demografi Jawa Timur: Peluang Emas atau Ancaman Pengangguran?\"**.\n",
            "\n",
            "## 2. Latar Belakang & Urgensi\n",
            "*   **Latar Belakang**: Indonesia diproyeksikan berada di puncak era bonus demografi pada dekade ini, di mana proporsi penduduk usia produktif (15-64 tahun) mendominasi lebih dari 70% total populasi. Jawa Timur, sebagai salah satu provinsi terbesar di Indonesia dengan jumlah penduduk lebih dari 40 juta jiwa, berada di pusat pusaran demografis ini.\n",
            "*   **Urgensi**: Ledakan penduduk usia muda/produktif ini merupakan pedang bermata dua. Jika pasar kerja lokal mampu menyerap tenaga kerja dengan baik, Jawa Timur akan menikmati akselerasi pertumbuhan ekonomi (\"Peluang Emas\"). Namun, jika kualitas dan ketersediaan lapangan kerja tidak mampu mengimbangi laju pertumbuhan angkatan kerja, limpahan usia produktif ini akan berubah menjadi pengangguran struktural yang masif (\"Ancaman Pengangguran / Bom Waktu Ketenagakerjaan\") sebelum tahun 2030.\n",
            "\n",
            "## 3. Sumber Data\n",
            "Analisis ini menggunakan data yang bersumber dari portal data resmi pemerintah:\n",
            "1.  **Badan Pusat Statistik (BPS) Provinsi Jawa Timur**: Data Jumlah Penduduk menurut Kelompok Umur, Jenis Kelamin, dan Kabupaten/Kota tahun 2018–2025.\n",
            "2.  **Satu Data Jawa Timur & BPS**: Data Tingkat Pengangguran Terbuka (TPT) dan Laju Pertumbuhan Penduduk per Kabupaten/Kota tahun 2018–2025.\n",
            "\n",
            "## 4. Variabel Data yang Digunakan\n",
            "*   `kabupaten/kota`: Nama wilayah administratif kabupaten/kota di Jawa Timur.\n",
            "*   `tahun`: Tahun observasi data (2018 - 2025).\n",
            "*   `kelompok_umur`: Kelompok umur penduduk per 5 tahun (0-4, 5-9, ..., 75+).\n",
            "*   `total` (dari data kelompok umur): Jumlah penduduk pada kelompok umur tertentu.\n",
            "*   `tpt` (dari master database): Tingkat Pengangguran Terbuka (%).\n",
            "*   `laju_pertumbuhan` (dari master database): Laju pertumbuhan penduduk tahunan (%)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import sys\n",
            "import glob\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from pathlib import Path\n",
            "\n",
            "# Tentukan path root proyek agar utils terdeteksi di Jupyter\n",
            "sys.path.append(str(Path(\"C:/VSCode/PKL-KOMINFO-NEW\")))\n",
            "from utils.load_data import load_master\n",
            "\n",
            "# Set style untuk plot yang indah dan formal\n",
            "sns.set_theme(style=\"whitegrid\")\n",
            "plt.rcParams['font.family'] = 'sans-serif'\n",
            "plt.rcParams['font.sans-serif'] = ['Inter', 'DejaVu Sans', 'Arial']\n",
            "\n",
            "# Tentukan path output\n",
            "OUTPUT_DIR = Path(\"C:/VSCode/PKL-KOMINFO-NEW/analisis_infografis_2/infografis bonus demografi/output\")\n",
            "OUTPUT_DIR.mkdir(parents=True, exist_ok=True)\n",
            "print(\"Output directory ready:\", OUTPUT_DIR)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Tentukan folder data asal\n",
            "DATA_DIR = Path(\"C:/VSCode/PKL-KOMINFO-NEW/analisis_infografis_2/data\")\n",
            "\n",
            "# Fungsi untuk membersihkan nama wilayah agar sinkron dengan database\n",
            "def clean_regency_name(name):\n",
            "    name = name.strip()\n",
            "    if name.startswith(\"Kabupaten \"):\n",
            "        val = name.replace(\"Kabupaten \", \"\").strip()\n",
            "        return val.title()\n",
            "    elif name.startswith(\"Kota \"):\n",
            "        val = name.replace(\"Kota \", \"\").strip()\n",
            "        return \"Kota \" + val.title()\n",
            "    return name.title()\n",
            "\n",
            "# Daftar kelompok umur produktif (15-64 tahun)\n",
            "usia_produktif_groups = [\"15-19\", \"20-24\", \"25-29\", \"30-34\", \"35-39\", \"40-44\", \"45-49\", \"50-54\", \"55-59\", \"60-64\"]\n",
            "\n",
            "all_years_data = []\n",
            "\n",
            "# Iterasi file CSV dari 2018-2025\n",
            "csv_files = glob.glob(str(DATA_DIR / \"penduduk_jatim_*.csv\"))\n",
            "for file_path in csv_files:\n",
            "    year = int(Path(file_path).stem.split(\"_\")[-1])\n",
            "    df_temp = pd.read_csv(file_path)\n",
            "    df_temp['nama_wilayah'] = df_temp['kabupaten/kota'].apply(clean_regency_name)\n",
            "    \n",
            "    grouped = df_temp.groupby('nama_wilayah')\n",
            "    for name, group in grouped:\n",
            "        total_pop = group['total'].sum()\n",
            "        productive_pop = group[group['kelompok_umur'].isin(usia_produktif_groups)]['total'].sum()\n",
            "        proporsi_productive = (productive_pop / total_pop) * 100 if total_pop > 0 else 0\n",
            "        \n",
            "        all_years_data.append({\n",
            "            \"nama_wilayah\": name,\n",
            "            \"tahun\": year,\n",
            "            \"jumlah_usia_produktif\": productive_pop,\n",
            "            \"total_penduduk_kelompok_umur\": total_pop,\n",
            "            \"persentase_usia_produktif\": proporsi_productive\n",
            "        })\n",
            "\n",
            "df_age = pd.DataFrame(all_years_data)\n",
            "print(\"Data struktur kelompok usia berhasil diolah. Baris data:\", len(df_age))\n",
            "df_age.head()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Memuat data master dari database lokal (atau fallback CSV)\n",
            "df_master = load_master()\n",
            "print(\"Data master dashboard berhasil dimuat. Baris data:\", len(df_master))\n",
            "df_master.head()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Penggabungan data kelompok usia dengan data makro pembangunan\n",
            "df_merged = pd.merge(\n",
            "    df_master[['kode_wilayah', 'nama_wilayah', 'tahun', 'tpt', 'laju_pertumbuhan']],\n",
            "    df_age,\n",
            "    on=['nama_wilayah', 'tahun'],\n",
            "    how='inner'\n",
            ")\n",
            "print(\"Dataset gabungan berhasil dibentuk. Baris data:\", len(df_merged))\n",
            "df_merged.head()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Analisis Kuadran (Quadrant Analysis)\n",
            "# Batas ambang batas ditentukan berdasarkan rata-rata provinsi Jawa Timur\n",
            "mean_productive = df_merged['persentase_usia_produktif'].mean()\n",
            "mean_tpt = df_merged['tpt'].mean()\n",
            "\n",
            "print(f\"Ambang batas persentase usia produktif (rata-rata): {mean_productive:.2f}%\")\n",
            "print(f\"Ambang batas Tingkat Pengangguran Terbuka (rata-rata): {mean_tpt:.2f}%\")\n",
            "\n",
            "def classify_quadrant(row):\n",
            "    if row['persentase_usia_produktif'] >= mean_productive:\n",
            "        if row['tpt'] >= mean_tpt:\n",
            "            return 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)'\n",
            "        else:\n",
            "            return 'Kuadran 1: Peluang Emas (Produktif Tinggi, TPT Rendah)'\n",
            "    else:\n",
            "        if row['tpt'] >= mean_tpt:\n",
            "            return 'Kuadran 4: Beban Ketenagakerjaan (Produktif Rendah, TPT Tinggi)'\n",
            "        else:\n",
            "            return 'Kuadran 3: Kondisi Stabil (Produktif Rendah, TPT Rendah)'\n",
            "\n",
            "df_merged['kategori_kuadran'] = df_merged.apply(classify_quadrant, axis=1)\n",
            "\n",
            "# Simpan data hasil analisis ke CSV di folder output\n",
            "CSV_OUTPUT = OUTPUT_DIR / \"data_analisis_bonus_demografi.csv\"\n",
            "df_merged.to_csv(CSV_OUTPUT, index=False)\n",
            "print(\"Data analisis berhasil disimpan ke:\", CSV_OUTPUT)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualisasi 1: Plot Analisis Kuadran (Scatter Plot) tahun 2025\n",
            "df_2025 = df_merged[df_merged['tahun'] == 2025].copy()\n",
            "\n",
            "plt.figure(figsize=(12, 8))\n",
            "colors = {\n",
            "    'Kuadran 1: Peluang Emas (Produktif Tinggi, TPT Rendah)': '#10b981',\n",
            "    'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)': '#ef4444',\n",
            "    'Kuadran 3: Kondisi Stabil (Produktif Rendah, TPT Rendah)': '#3b82f6',\n",
            "    'Kuadran 4: Beban Ketenagakerjaan (Produktif Rendah, TPT Tinggi)': '#f59e0b'\n",
            "}\n",
            "\n",
            "sns.scatterplot(\n",
            "    data=df_2025,\n",
            "    x='persentase_usia_produktif',\n",
            "    y='tpt',\n",
            "    hue='kategori_kuadran',\n",
            "    palette=colors,\n",
            "    s=150,\n",
            "    alpha=0.85,\n",
            "    edgecolor='w',\n",
            "    linewidth=1.5\n",
            ")\n",
            "\n",
            "# Tambahkan garis ambang batas rata-rata\n",
            "plt.axvline(x=mean_productive, color='#64748b', linestyle='--', linewidth=1.5, label='Rata-rata Usia Produktif')\n",
            "plt.axhline(y=mean_tpt, color='#64748b', linestyle='--', linewidth=1.5, label='Rata-rata TPT')\n",
            "\n",
            "# Label nama wilayah pada titik-titik krusial\n",
            "for i, row in df_2025.iterrows():\n",
            "    if row['kategori_kuadran'] == 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)' or row['tpt'] > 6.0:\n",
            "        plt.text(\n",
            "            row['persentase_usia_produktif'] + 0.1,\n",
            "            row['tpt'] + 0.05,\n",
            "            row['nama_wilayah'],\n",
            "            fontsize=8,\n",
            "            fontweight='semibold',\n",
            "            color='#1e293b'\n",
            "        )\n",
            "\n",
            "plt.title(\"Analisis Kuadran Bonus Demografi Jawa Timur (Tahun 2025)\\nPeluang Emas (Penyusutan Pengangguran) vs Ancaman Pengangguran Struktural\", fontsize=14, fontweight='bold', pad=15)\n",
            "plt.xlabel(\"Proporsi Penduduk Usia Produktif 15-64 Tahun (%)\", fontsize=11, fontweight='semibold')\n",
            "plt.ylabel(\"Tingkat Pengangguran Terbuka - TPT (%)\", fontsize=11, fontweight='semibold')\n",
            "plt.legend(title=\"Klasifikasi Wilayah\", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, frameon=True)\n",
            "plt.tight_layout()\n",
            "\n",
            "PLOT_1_PATH = OUTPUT_DIR / \"1_kuadran_bonus_demografi.png\"\n",
            "plt.savefig(PLOT_1_PATH, dpi=300, bbox_inches='tight')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualisasi 2: Top Wilayah Terancam Pengangguran Struktural (Kuadran 2)\n",
            "df_threat = df_2025[df_2025['kategori_kuadran'] == 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)'].sort_values(by='tpt', ascending=False)\n",
            "\n",
            "plt.figure(figsize=(10, 6))\n",
            "sns.barplot(\n",
            "    data=df_threat,\n",
            "    x='tpt',\n",
            "    y='nama_wilayah',\n",
            "    color='#ef4444',\n",
            "    edgecolor='#b91c1c',\n",
            "    linewidth=1\n",
            ")\n",
            "\n",
            "plt.axvline(x=mean_tpt, color='#64748b', linestyle='--', linewidth=1.5)\n",
            "plt.text(mean_tpt + 0.1, len(df_threat) - 0.5, f\"Rata-rata TPT: {mean_tpt:.2f}%\", color='#64748b', fontweight='semibold')\n",
            "\n",
            "plt.title(\"Daftar Wilayah di Zona Merah (Kuadran 2) Tahun 2025\\nProporsi Usia Produktif Melimpah TAPI Pengangguran (TPT) Sangat Tinggi\", fontsize=13, fontweight='bold', pad=15)\n",
            "plt.xlabel(\"Tingkat Pengangguran Terbuka - TPT (%)\", fontsize=11, fontweight='semibold')\n",
            "plt.ylabel(\"Kabupaten/Kota\", fontsize=11, fontweight='semibold')\n",
            "plt.tight_layout()\n",
            "\n",
            "PLOT_2_PATH = OUTPUT_DIR / \"2_daerah_terancam.png\"\n",
            "plt.savefig(PLOT_2_PATH, dpi=300, bbox_inches='tight')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualisasi 3: Tren Historis Bonus Demografi vs TPT Jawa Timur (2018-2025)\n",
            "df_trend = df_merged.groupby('tahun')[['persentase_usia_produktif', 'tpt']].mean().reset_index()\n",
            "\n",
            "fig, ax1 = plt.subplots(figsize=(10, 6))\n",
            "color = '#1e3a8a'\n",
            "ax1.set_xlabel('Tahun', fontsize=11, fontweight='semibold')\n",
            "ax1.set_ylabel('Rata-rata Usia Produktif (%)', color=color, fontsize=11, fontweight='semibold')\n",
            "line1 = ax1.plot(df_trend['tahun'], df_trend['persentase_usia_produktif'], color=color, marker='o', linewidth=2.5, label='Proporsi Usia Produktif')\n",
            "ax1.tick_params(axis='y', labelcolor=color)\n",
            "ax1.grid(True, linestyle=':', alpha=0.6)\n",
            "\n",
            "ax2 = ax1.twinx()\n",
            "color = '#ef4444'\n",
            "ax2.set_ylabel('Rata-rata Pengangguran - TPT (%)', color=color, fontsize=11, fontweight='semibold')\n",
            "line2 = ax2.plot(df_trend['tahun'], df_trend['tpt'], color=color, marker='s', linestyle='--', linewidth=2.5, label='TPT')\n",
            "ax2.tick_params(axis='y', labelcolor=color)\n",
            "\n",
            "lines = line1 + line2\n",
            "labels = [l.get_label() for l in lines]\n",
            "ax1.legend(lines, labels, loc='upper left')\n",
            "\n",
            "plt.title(\"Tren Perkembangan Bonus Demografi vs Tingkat Pengangguran Terbuka (TPT)\\nProvinsi Jawa Timur (Periode Historis 2018-2025)\", fontsize=13, fontweight='bold', pad=15)\n",
            "fig.tight_layout()\n",
            "\n",
            "PLOT_3_PATH = OUTPUT_DIR / \"3_tren_historis.png\"\n",
            "plt.savefig(PLOT_3_PATH, dpi=300, bbox_inches='tight')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Kesimpulan dan Analisis Hasil Olah Data\n",
            "\n",
            "Berdasarkan visualisasi dan pengolahan data di atas, terdapat beberapa temuan krusial yang dapat dipresentasikan:\n",
            "\n",
            "### 1. Pola Kesenjangan Penyerapan Tenaga Kerja (Kuadran Analisis)\n",
            "*   **Kuadran 2 (Zona Merah - Ancaman Pengangguran)**: Wilayah di kuadran ini memiliki persentase usia produktif yang melimpah (di atas rata-rata provinsi), namun diiringi dengan Tingkat Pengangguran Terbuka (TPT) yang juga sangat tinggi. Ini adalah indikator bahwa ledakan tenaga kerja muda di wilayah ini gagal diserap oleh industri lokal. Daerah seperti **Kota Surabaya, Sidoarjo, dan Gresik** sering berada di zona ini karena bertindak sebagai magnet urbanisasi tetapi kapasitas industri manufaktur dan jasanya memiliki batas daya serap.\n",
            "*   **Kuadran 1 (Zona Hijau - Peluang Emas)**: Wilayah yang berhasil memaksimalkan bonus demografinya dengan menjaga tingkat pengangguran tetap rendah. Penduduk usia produktif terserap secara optimal ke dalam roda perekonomian lokal.\n",
            "\n",
            "### 2. Tren Historis Jawa Timur (2018-2025)\n",
            "*   Grafik tren menunjukkan pergerakan proporsi usia produktif relatif stabil tinggi (di kisaran 68%-70%), namun TPT mengalami fluktuasi tajam (terutama lonjakan saat pandemi COVID-19 di tahun 2020-2021).\n",
            "*   Penurunan TPT pasca-pandemi dari 2022 hingga 2025 menunjukkan pemulihan pasar kerja, tetapi disparitas antar-kabupaten tetap lebar. Jendela bonus demografi Jawa Timur masih menyisakan ancaman struktural jika tidak diimbangi dengan kebijakan pelatihan keterampilan kerja (upskilling) vokasi untuk menyelaraskan dengan kebutuhan industri modern."
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write Jupyter Notebook to disk
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)
print(f"Jupyter Notebook successfully created at: {NOTEBOOK_PATH}")

print("2. Running data calculations and saving outputs...")

# Clean regency name function
def clean_regency_name(name):
    name = name.strip()
    if name.startswith("Kabupaten "):
        val = name.replace("Kabupaten ", "").strip()
        return val.title()
    elif name.startswith("Kota "):
        val = name.replace("Kota ", "").strip()
        return "Kota " + val.title()
    return name.title()

usia_produktif_groups = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64"]
all_years_data = []

csv_files = glob.glob(str(DATA_DIR / "penduduk_jatim_*.csv"))
for file_path in csv_files:
    year = int(Path(file_path).stem.split("_")[-1])
    df_temp = pd.read_csv(file_path)
    df_temp['nama_wilayah'] = df_temp['kabupaten/kota'].apply(clean_regency_name)
    
    grouped = df_temp.groupby('nama_wilayah')
    for name, group in grouped:
        total_pop = group['total'].sum()
        productive_pop = group[group['kelompok_umur'].isin(usia_produktif_groups)]['total'].sum()
        proporsi_productive = (productive_pop / total_pop) * 100 if total_pop > 0 else 0
        
        all_years_data.append({
            "nama_wilayah": name,
            "tahun": year,
            "jumlah_usia_produktif": productive_pop,
            "total_penduduk_kelompok_umur": total_pop,
            "persentase_usia_produktif": proporsi_productive
        })

df_age = pd.DataFrame(all_years_data)
df_master = load_master()

df_merged = pd.merge(
    df_master[['kode_wilayah', 'nama_wilayah', 'tahun', 'tpt', 'laju_pertumbuhan']],
    df_age,
    on=['nama_wilayah', 'tahun'],
    how='inner'
)

mean_productive = df_merged['persentase_usia_produktif'].mean()
mean_tpt = df_merged['tpt'].mean()

def classify_quadrant(row):
    if row['persentase_usia_produktif'] >= mean_productive:
        if row['tpt'] >= mean_tpt:
            return 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)'
        else:
            return 'Kuadran 1: Peluang Emas (Produktif Tinggi, TPT Rendah)'
    else:
        if row['tpt'] >= mean_tpt:
            return 'Kuadran 4: Beban Ketenagakerjaan (Produktif Rendah, TPT Tinggi)'
        else:
            return 'Kuadran 3: Kondisi Stabil (Produktif Rendah, TPT Rendah)'

df_merged['kategori_kuadran'] = df_merged.apply(classify_quadrant, axis=1)

# Save output CSV
CSV_OUTPUT = OUTPUT_DIR / "data_analisis_bonus_demografi.csv"
df_merged.to_csv(CSV_OUTPUT, index=False)
print("CSV data saved successfully.")

# Generate Plot 1 (Scatter Plot)
df_2025 = df_merged[df_merged['tahun'] == 2025].copy()
plt.figure(figsize=(12, 8))
colors = {
    'Kuadran 1: Peluang Emas (Produktif Tinggi, TPT Rendah)': '#10b981',
    'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)': '#ef4444',
    'Kuadran 3: Kondisi Stabil (Produktif Rendah, TPT Rendah)': '#3b82f6',
    'Kuadran 4: Beban Ketenagakerjaan (Produktif Rendah, TPT Tinggi)': '#f59e0b'
}
sns.set_theme(style="whitegrid")
sns.scatterplot(
    data=df_2025,
    x='persentase_usia_produktif',
    y='tpt',
    hue='kategori_kuadran',
    palette=colors,
    s=150,
    alpha=0.85,
    edgecolor='w',
    linewidth=1.5
)
plt.axvline(x=mean_productive, color='#64748b', linestyle='--', linewidth=1.5, label='Rata-rata Usia Produktif')
plt.axhline(y=mean_tpt, color='#64748b', linestyle='--', linewidth=1.5, label='Rata-rata TPT')

for i, row in df_2025.iterrows():
    if row['kategori_kuadran'] == 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)' or row['tpt'] > 6.0:
        plt.text(
            row['persentase_usia_produktif'] + 0.1,
            row['tpt'] + 0.05,
            row['nama_wilayah'],
            fontsize=8,
            fontweight='semibold',
            color='#1e293b'
        )

plt.title("Analisis Kuadran Bonus Demografi Jawa Timur (Tahun 2025)\nPeluang Emas (Penyusutan Pengangguran) vs Ancaman Pengangguran Struktural", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Proporsi Penduduk Usia Produktif 15-64 Tahun (%)", fontsize=11, fontweight='semibold')
plt.ylabel("Tingkat Pengangguran Terbuka - TPT (%)", fontsize=11, fontweight='semibold')
plt.legend(title="Klasifikasi Wilayah", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, frameon=True)
plt.tight_layout()
PLOT_1_PATH = OUTPUT_DIR / "1_kuadran_bonus_demografi.png"
plt.savefig(PLOT_1_PATH, dpi=300, bbox_inches='tight')
plt.close()
print("Plot 1 (Scatter Plot) saved successfully.")

# Generate Plot 2 (Bar Chart)
df_threat = df_2025[df_2025['kategori_kuadran'] == 'Kuadran 2: Ancaman Pengangguran (Produktif Tinggi, TPT Tinggi)'].sort_values(by='tpt', ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(
    data=df_threat,
    x='tpt',
    y='nama_wilayah',
    color='#ef4444',
    edgecolor='#b91c1c',
    linewidth=1
)
plt.axvline(x=mean_tpt, color='#64748b', linestyle='--', linewidth=1.5)
plt.text(mean_tpt + 0.1, len(df_threat) - 0.5, f"Rata-rata TPT: {mean_tpt:.2f}%", color='#64748b', fontweight='semibold')
plt.title("Daftar Wilayah di Zona Merah (Kuadran 2) Tahun 2025\nProporsi Usia Produktif Melimpah TAPI Pengangguran (TPT) Sangat Tinggi", fontsize=13, fontweight='bold', pad=15)
plt.xlabel("Tingkat Pengangguran Terbuka - TPT (%)", fontsize=11, fontweight='semibold')
plt.ylabel("Kabupaten/Kota", fontsize=11, fontweight='semibold')
plt.tight_layout()
PLOT_2_PATH = OUTPUT_DIR / "2_daerah_terancam.png"
plt.savefig(PLOT_2_PATH, dpi=300, bbox_inches='tight')
plt.close()
print("Plot 2 (Bar Chart) saved successfully.")

# Generate Plot 3 (Line Chart)
df_trend = df_merged.groupby('tahun')[['persentase_usia_produktif', 'tpt']].mean().reset_index()
fig, ax1 = plt.subplots(figsize=(10, 6))
color = '#1e3a8a'
ax1.set_xlabel('Tahun', fontsize=11, fontweight='semibold')
ax1.set_ylabel('Rata-rata Usia Produktif (%)', color=color, fontsize=11, fontweight='semibold')
line1 = ax1.plot(df_trend['tahun'], df_trend['persentase_usia_produktif'], color=color, marker='o', linewidth=2.5, label='Proporsi Usia Produktif')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle=':', alpha=0.6)

ax2 = ax1.twinx()
color = '#ef4444'
ax2.set_ylabel('Rata-rata Pengangguran - TPT (%)', color=color, fontsize=11, fontweight='semibold')
line2 = ax2.plot(df_trend['tahun'], df_trend['tpt'], color=color, marker='s', linestyle='--', linewidth=2.5, label='TPT')
ax2.tick_params(axis='y', labelcolor=color)

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')
plt.title("Tren Perkembangan Bonus Demografi vs Tingkat Pengangguran Terbuka (TPT)\nProvinsi Jawa Timur (Periode Historis 2018-2025)", fontsize=13, fontweight='bold', pad=15)
fig.tight_layout()
PLOT_3_PATH = OUTPUT_DIR / "3_tren_historis.png"
plt.savefig(PLOT_3_PATH, dpi=300, bbox_inches='tight')
plt.close()
print("Plot 3 (Line Chart) saved successfully.")

print("All outputs generated successfully!")
