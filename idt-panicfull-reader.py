import streamlit as st
import re
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =====================
# Database iPhone Mapping
# =====================
IPHONE_MAP = {
    "iPhone7,2": "iPhone 6",
    "iPhone7,1": "iPhone 6 Plus",
    "iPhone8,1": "iPhone 6s",
    "iPhone8,2": "iPhone 6s Plus",
    "iPhone8,4": "iPhone SE (1st gen)",
    "iPhone9,1": "iPhone 7", "iPhone9,3": "iPhone 7",
    "iPhone9,2": "iPhone 7 Plus", "iPhone9,4": "iPhone 7 Plus",
    "iPhone10,1": "iPhone 8", "iPhone10,4": "iPhone 8",
    "iPhone10,2": "iPhone 8 Plus", "iPhone10,5": "iPhone 8 Plus",
    "iPhone10,3": "iPhone X (China)", "iPhone10,6": "iPhone X (Global)",
    "iPhone11,2": "iPhone XS", "iPhone11,4": "iPhone XS Max",
    "iPhone11,6": "iPhone XS Max (China)", "iPhone11,8": "iPhone XR",
    "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro",
    "iPhone12,5": "iPhone 11 Pro Max", "iPhone12,8": "iPhone SE (2nd gen)",
    "iPhone13,1": "iPhone 12 mini", "iPhone13,2": "iPhone 12",
    "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,4": "iPhone 13 mini", "iPhone14,5": "iPhone 13",
    "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,6": "iPhone SE (3rd gen)", "iPhone14,7": "iPhone 14",
    "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro",
    "iPhone15,3": "iPhone 14 Pro Max", "iPhone15,4": "iPhone 15",
    "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro",
    "iPhone16,2": "iPhone 15 Pro Max", "iPhone17,1": "iPhone 16 Pro",
    "iPhone17,2": "iPhone 16 Pro Max", "iPhone17,3": "iPhone 16",
    "iPhone17,4": "iPhone 16 Plus",
}

# =====================
# Database Panic Full Error (contoh singkat, bisa diperluas)
# Database Panic-Full 📚
# ======================
PANIC_DB = {
    "mic2": {
        "kategori": "Audio / Mic",
        "penyebab_umum": [
            "Sering terjadi setelah kena air bagian bawah",
            "Kerusakan dock flex",
            "Solderan jalur mic retak karena benturan"
        ],
        "checklist": [
            {"bagian": "Dock Flex / Mic Bawah", "letak": "Dock Flex (bawah)", "tindakan": "Coba ganti flex bawah"},
            {"bagian": "Konektor J6300", "letak": "Board bawah", "tindakan": "Bersihkan, re-tin pin konektor"},
            {"bagian": "Jalur SDA / SCL", "letak": "Board bawah → PMIC", "tindakan": "Ukur continuity jalur I²C"},
            {"bagian": "Resistor Pull-up 1.8V", "letak": "Dekat J6300", "tindakan": "Ukur nilai resistor"}
        ],
        "keterangan": "Umumnya muncul di panic log dengan 'missing sensor: mic2'."
    },

    "battery_ntc": {
        "kategori": "Power / Baterai",
        "penyebab_umum": [
            "Baterai KW atau rusak",
            "Flex baterai putus atau korosi",
            "Kena air → jalur NTC short"
        ],
        "checklist": [
            {"bagian": "Baterai", "letak": "Baterai iPhone", "tindakan": "Coba ganti baterai original"},
            {"bagian": "Flexible Baterai", "letak": "Konektor baterai", "tindakan": "Cek kondisi flex"},
            {"bagian": "Jalur NTC", "letak": "Baterai → PMIC", "tindakan": "Continuity test jalur NTC"}
        ],
        "keterangan": "Biasanya panic log menyebut 'missing sensor: battery_ntc'."
    },

    "thermalmonitord": {
        "kategori": "Thermal / Suhu",
        "penyebab_umum": [
            "Flex kamera ada short (kamera ada sensor suhu)",
            "Sensor baterai tidak terbaca",
            "IC PMIC bermasalah"
        ],
        "checklist": [
            {"bagian": "Sensor Suhu Baterai", "letak": "Baterai", "tindakan": "Cek apakah NTC terbaca"},
            {"bagian": "PMIC", "letak": "Board", "tindakan": "Periksa apakah panas/short"},
            {"bagian": "Camera Flex", "letak": "Flex kamera depan/belakang", "tindakan": "Coba ganti flex kamera"}
        ],
        "keterangan": "Ditandai panic log ada kata 'thermalmonitord'."
    },

    "baseband": {
        "kategori": "Sinyal / Baseband",
        "penyebab_umum": [
            "HP terbanting → solderan retak di IC Baseband",
            "Air merusak jalur clock baseband",
            "Update iOS gagal menulis data ke modem firmware"
        ],
        "checklist": [
            {"bagian": "IC Baseband", "letak": "Dekat CPU (iPhone 6s–X)", "tindakan": "Reball/replace IC baseband"},
            {"bagian": "Jalur Clock & Power", "letak": "CPU ↔ Baseband", "tindakan": "Continuity test jalur"},
            {"bagian": "EEPROM Modem", "letak": "Dekat Baseband", "tindakan": "Reprogram / ganti"}
        ],
        "keterangan": "Biasanya muncul panic string: 'No service / modem panic'."
    },

    "userspace_watchdog": {
        "kategori": "System / Boot",
        "penyebab_umum": [
            "iOS corrupt karena update gagal",
            "Aplikasi crash terus → watchdog reset",
            "Kerusakan NAND storage"
        ],
        "checklist": [
            {"bagian": "iOS System", "letak": "Software", "tindakan": "Restore ulang via iTunes"},
            {"bagian": "NAND", "letak": "Board", "tindakan": "Reball/ganti NAND jika error terus"},
            {"bagian": "Cek Aplikasi", "letak": "System", "tindakan": "Pastikan tidak ada app corrupt"}
        ],
        "keterangan": "Ditandai panic log ada 'userspace watchdog timeout'."
    },

    "tristar_tigris": {
        "kategori": "Power / Charging",
        "penyebab_umum": [
            "Menggunakan charger non-original",
            "IC Tristar/Tigris rusak akibat tegangan tidak stabil",
            "HP sering mati hidup saat di-charge"
        ],
        "checklist": [
            {"bagian": "IC Tristar", "letak": "Dekat konektor lightning", "tindakan": "Ganti IC Tristar"},
            {"bagian": "IC Tigris", "letak": "Board bawah", "tindakan": "Cek tegangan, ganti jika rusak"},
            {"bagian": "Konektor Lightning", "letak": "Board bawah", "tindakan": "Coba ganti dock flex"}
        ],
        "keterangan": "Biasanya panic log terkait charging / USB detect error."
    },

    "audio_ic": {
        "kategori": "Audio / Speaker",
        "penyebab_umum": [
            "Umumnya di iPhone 7/7 Plus",
            "Sering terbanting → jalur C12/C14 retak",
            "Audio IC rusak (U3101)"
        ],
        "checklist": [
            {"bagian": "IC Audio", "letak": "Dekat CPU", "tindakan": "Reball/ganti IC"},
            {"bagian": "Jalur Data Audio", "letak": "CPU ↔ Audio IC", "tindakan": "Ukur continuity"},
            {"bagian": "Mic Flex", "letak": "Dock Flex", "tindakan": "Tes mic flex"}
        ],
        "keterangan": "Gejala: panic + tidak ada suara saat rekam, voice memo tidak jalan."
    },

    "default": {
        "kategori": "Umum",
        "penyebab_umum": [
            "HP kena air",
            "Pernah jatuh / terbanting",
            "Baterai atau flex KW",
            "IC overheat"
        ],
        "checklist": [
            {"bagian": "Baterai", "letak": "Board bawah", "tindakan": "Coba ganti baterai original"},
            {"bagian": "Dock Flex", "letak": "Board bawah", "tindakan": "Tes ganti dock flex"},
            {"bagian": "Camera Flex", "letak": "Board atas", "tindakan": "Tes ganti kamera flex"},
            {"bagian": "PMIC", "letak": "Dekat CPU", "tindakan": "Ukur tegangan, cek short"}
        ],
        "keterangan": "Digunakan jika panic log tidak cocok dengan pola spesifik."
    }
}

# =====================
# Fungsi parsing log
# =====================
def parse_panic_log(log_text):
    results = {}

    # Cari tipe iPhone
    product_match = re.search(r"iPhone\d+,\d+", log_text)
    if product_match:
        product_code = product_match.group(0)
        results["Model"] = IPHONE_MAP.get(product_code, f"Tidak dikenal ({product_code})")
    else:
        results["Model"] = "Tidak ditemukan"

    # Cari error utama
    found_errors = []
    for key, explanation in PANIC_ERROR_DB.items():
        if key.lower() in log_text.lower():
            found_errors.append(f"{key.upper()} → {explanation}")
    results["Diagnosis"] = found_errors if found_errors else ["Tidak ada error spesifik ditemukan"]

    # Tambahkan kemungkinan penyebab umum
    results["Kemungkinan"] = [
        "Panic full bisa terjadi karena: kena air, terbanting, solderan retak, atau IC rusak."
    ]

    return results

# =====================
# Fungsi buat PDF report
# =====================
def build_report(model, diagnosis, kemungkinan, raw_text):
    filename = "panic_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)
    story = []

    story.append(Paragraph("📱 Laporan Analisa Panic Full", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Model iPhone: {model}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("🔎 Diagnosis:", styles["Heading2"]))
    for d in diagnosis:
        story.append(Paragraph(f"- {d}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("💡 Kemungkinan Penyebab:", styles["Heading2"]))
    for k in kemungkinan:
        story.append(Paragraph(f"- {k}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("📝 Log Asli:", styles["Heading2"]))
    story.append(Paragraph(f"<pre>{raw_text[:2000]}</pre>", styles["Code"]))  # biar ga terlalu panjang

    doc.build(story)
    return filename

# =====================
# Streamlit App
# =====================
st.title("📱 iPhone Panic Full Reader")
st.write("Upload log panic-full untuk analisa otomatis.")

uploaded_file = st.file_uploader("Upload file panic-full", type=["txt", "log"])

if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8", errors="ignore")

    results = parse_panic_log(log_text)

    st.subheader("📌 Hasil Analisa")
    st.write(f"**Model iPhone**: {results['Model']}")

    st.write("**Diagnosis:**")
    for d in results["Diagnosis"]:
        st.markdown(f"- {d}")

    st.write("**Kemungkinan Penyebab Umum:**")
    for k in results["Kemungkinan"]:
        st.markdown(f"- {k}")

    # Tombol export PDF
    if st.button("📤 Export ke PDF"):
        pdf_file = build_report(results["Model"], results["Diagnosis"], results["Kemungkinan"], log_text)
        with open(pdf_file, "rb") as f:
            st.download_button("Download Report PDF", f, file_name="panic_report.pdf")
