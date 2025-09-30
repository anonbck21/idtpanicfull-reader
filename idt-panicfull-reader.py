import streamlit as st
import re

# ===============================
# 1. Database iPhone (Board Code + Identifier)
# ===============================
BOARD_MAP = {
    "N61AP": "iPhone 6", "N56AP": "iPhone 6 Plus",
    "N71AP": "iPhone 6s", "N66AP": "iPhone 6s Plus",
    "N69AP": "iPhone SE (1st Gen)",

    "D10AP": "iPhone 7", "D11AP": "iPhone 7 Plus",
    "D20AP": "iPhone 8", "D21AP": "iPhone 8 Plus",
    "D22AP": "iPhone X",

    "D321AP": "iPhone XS", "D331pAP": "iPhone XS Max", "N841AP": "iPhone XR",

    "D421AP": "iPhone 11 Pro", "D431AP": "iPhone 11 Pro Max", "N104AP": "iPhone 11",
    "D79AP": "iPhone SE (2nd Gen)",

    "D52GAP": "iPhone 12", "D53GAP": "iPhone 12 mini",
    "D54PAP": "iPhone 12 Pro", "D55PAP": "iPhone 12 Pro Max",

    "D16AP": "iPhone 13 mini", "D17AP": "iPhone 13",
    "D18AP": "iPhone 13 Pro", "D19AP": "iPhone 13 Pro Max",

    "D49AP": "iPhone SE (3rd Gen)",

    "D27AP": "iPhone 14", "D28AP": "iPhone 14 Plus",
    "D29AP": "iPhone 14 Pro", "D30AP": "iPhone 14 Pro Max",

    "D83AP": "iPhone 15", "D84AP": "iPhone 15 Plus",
    "D85AP": "iPhone 15 Pro", "D86AP": "iPhone 15 Pro Max",

    "D47AP": "iPhone 16", "D48AP": "iPhone 16 Plus",
    "D49AP": "iPhone 16 Pro", "D50AP": "iPhone 16 Pro Max",
}

IPHONE_MAP = {
    "iPhone7,2": "iPhone 6", "iPhone7,1": "iPhone 6 Plus",
    "iPhone8,1": "iPhone 6s", "iPhone8,2": "iPhone 6s Plus",
    "iPhone8,4": "iPhone SE (1st Gen)",
    "iPhone9,1": "iPhone 7", "iPhone9,2": "iPhone 7 Plus",
    "iPhone10,1": "iPhone 8", "iPhone10,2": "iPhone 8 Plus",
    "iPhone10,3": "iPhone X",
    "iPhone11,2": "iPhone XS", "iPhone11,4": "iPhone XS Max",
    "iPhone11,6": "iPhone XS Max", "iPhone11,8": "iPhone XR",
    "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro",
    "iPhone12,5": "iPhone 11 Pro Max",
    "iPhone12,8": "iPhone SE (2nd Gen)",
    "iPhone13,1": "iPhone 12 mini", "iPhone13,2": "iPhone 12",
    "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,4": "iPhone 13 mini", "iPhone14,5": "iPhone 13",
    "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,6": "iPhone SE (3rd Gen)",
    "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus",
    "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
    "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus",
    "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
    "iPhone16,3": "iPhone 16", "iPhone16,4": "iPhone 16 Plus",
    "iPhone16,5": "iPhone 16 Pro", "iPhone16,6": "iPhone 16 Pro Max",
}

# ===============================
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

# ======================

# ===============================
# 3. Database Penyebab Umum Panic Full
# ===============================
CAUSE_DB = [
    "Terkena air atau lembab",
    "Ponsel terbanting / jatuh",
    "Overheat (panas berlebih)",
    "Korslet akibat pengisian daya",
    "Update iOS gagal atau corrupt",
    "Kerusakan hardware (IC, konektor, jalur)",
]

# ===============================
# 4. Fungsi Parsing Panic Full
# ===============================
def parse_panic_log(text):
    out = {}
    model = None

    # Cari identifier iPhoneX,Y
    match_id = re.search(r"(iPhone\d+,\d+)", text)
    if match_id:
        code = match_id.group(1)
        model = IPHONE_MAP.get(code, f"Unknown ({code})")

    # Cari board code
    match_board = re.search(r"(D\d+\w*AP|N\d+\w*AP)", text)
    if match_board and not model:
        code = match_board.group(1)
        model = BOARD_MAP.get(code, f"Unknown ({code})")

    out["model"] = model if model else "Unknown"
    out["symptoms"] = []
    out["possible_causes"] = []

    for key, issues in SYMPTOM_DB.items():
        if re.search(key, text, re.IGNORECASE):
            out["symptoms"].append(key)
            out["possible_causes"].extend(issues)

    return out

# ===============================
# 5. Streamlit App
# ===============================
st.title("📱 iPhone Panic Full Reader - IDT DokterHP")

uploaded = st.file_uploader("Upload Panic Full Log (.txt)", type=["txt"])
if uploaded:
    text = uploaded.read().decode("utf-8", errors="ignore")
    result = parse_panic_log(text)

    st.subheader("📌 Hasil Analisis")
    st.write(f"**Model iPhone**: {result['model']}")

    if result["symptoms"]:
        st.write("**Gejala yang terdeteksi:**")
        for s in result["symptoms"]:
            st.markdown(f"- {s}")

        st.write("**Kemungkinan kerusakan:**")
        for c in result["possible_causes"]:
            st.markdown(f"- {c}")
    else:
        st.info("Tidak ada gejala spesifik ditemukan dalam log.")

    st.write("**Penyebab umum Panic Full:**")
    for c in CAUSE_DB:
        st.markdown(f"- {c}")

# ===============================
# 6. Footer
# ===============================
st.markdown("---")
st.markdown("© 2025 | Interested in collaboration: [@maxxjen1](https://instagram.com/maxxjen1) on Instagram")
