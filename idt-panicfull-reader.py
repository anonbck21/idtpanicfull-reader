# =======================================
# 📱 IDT Panic-Full Reader (iPhone)
# v1.0 by JENSKYYY
# =======================================

import streamlit as st
import re
from datetime import datetime
import pandas as pd

# =====================
# Database iPhone Mapping

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
# Mapping board-code ke iPhone model
BOARD_MAP = {
    # iPhone 6 series
    "N61AP": "iPhone 6",
    "N56AP": "iPhone 6 Plus",

    # iPhone 6s series
    "N71AP": "iPhone 6s",
    "N66AP": "iPhone 6s Plus",

    # iPhone SE (1st Gen)
    "N69AP": "iPhone SE (1st Gen)",

    # iPhone 7 series
    "D10AP": "iPhone 7",
    "D11AP": "iPhone 7 Plus",

    # iPhone 8 series
    "D20AP": "iPhone 8",
    "D21AP": "iPhone 8 Plus",

    # iPhone X
    "D22AP": "iPhone X",

    # iPhone XS / XS Max / XR
    "D321AP": "iPhone XS",
    "D331pAP": "iPhone XS Max",
    "N841AP": "iPhone XR",

    # iPhone 11 series
    "D421AP": "iPhone 11 Pro",
    "D431AP": "iPhone 11 Pro Max",
    "N104AP": "iPhone 11",

    # iPhone SE (2nd Gen)
    "D79AP": "iPhone SE (2nd Gen)",

    # iPhone 12 series
    "D52GAP": "iPhone 12",
    "D53GAP": "iPhone 12 mini",
    "D54PAP": "iPhone 12 Pro",
    "D55PAP": "iPhone 12 Pro Max",

    # iPhone 13 series
    "D16AP": "iPhone 13 mini",
    "D17AP": "iPhone 13",
    "D18AP": "iPhone 13 Pro",
    "D19AP": "iPhone 13 Pro Max",

    # iPhone SE (3rd Gen)
    "D49AP": "iPhone SE (3rd Gen)",

    # iPhone 14 series
    "D27AP": "iPhone 14",
    "D28AP": "iPhone 14 Plus",
    "D29AP": "iPhone 14 Pro",
    "D30AP": "iPhone 14 Pro Max",

    # iPhone 15 series
    "D83AP": "iPhone 15",
    "D84AP": "iPhone 15 Plus",
    "D85AP": "iPhone 15 Pro",
    "D86AP": "iPhone 15 Pro Max",

    # iPhone 16 series (2024)
    "D47AP": "iPhone 16",
    "D48AP": "iPhone 16 Plus",
    "D49AP": "iPhone 16 Pro",
    "D50AP": "iPhone 16 Pro Max",
}

def extract_all(text):
    out = {}
    for k, pat in RE_PATTERNS.items():
        m = pat.search(text)
        if m:
            groups = [g for g in m.groups() if g]
            out[k] = groups[0].strip() if groups else m.group(0).strip()
prod_code = out.get("device", "")
if prod_code in BOARD_MAP:
    out["iphone_model"] = BOARD_MAP[prod_code]
elif re.search(r"iPhone\d+,\d+", text):
    code = re.search(r"(iPhone\d+,\d+)", text).group(1)
    out["iphone_model"] = IPHONE_MAP.get(code, f"Unknown ({code})")
else:
    out["iphone_model"] = f"Unknown ({prod_code})" if prod_code else "Unknown"

    # --- Cari product: iPhoneXX,YY ---
    
    # --- Missing sensors ---
    ms = re.findall(r'Missing sensor\(s\):\s*([^\n\r]+)', text, re.I)
    if ms:
        sensors = []
        for s in ms:
            sensors += re.split(r'[,\s]+', s.strip())
        out['missing_sensors_all'] = list(dict.fromkeys([x for x in sensors if x]))

    out['contains_thermalmonitord'] = bool(re.search(r'thermalmonitord', text, re.I))
    
    prod_code = out.get("device", "")
if prod_code in BOARD_MAP:
    out["iphone_model"] = BOARD_MAP[prod_code]
elif re.search(r"iPhone\d+,\d+", text):
    code = re.search(r"(iPhone\d+,\d+)", text).group(1)
    out["iphone_model"] = IPHONE_MAP.get(code, f"Unknown ({code})")
else:
    out["iphone_model"] = f"Unknown ({prod_code})" if prod_code else "Unknown"

    return out

# Regex Extractor 🔍
# ======================
RE_PATTERNS = {
    "device": re.compile(r'product:\s*([^\s,;]+)', re.I),
    "ios_version": re.compile(r'iOS Version:\s*([^\n\r]+)|OS Version:\s*([^\n\r]+)', re.I),
    "panic_string": re.compile(r'panicString:\s*(.+)', re.I),
    "missing_sensors": re.compile(r'Missing sensor\(s\):\s*([^\n\r]+)', re.I),
    "userspace_watchdog": re.compile(r'userspace watchdog timeout:\s*(.+)', re.I),
}



def generate_checklist(ctx):
    sensors = [s.lower() for s in ctx.get('missing_sensors_all', [])]
    checks, notes = [], []

    if "mic2" in sensors:
        data = PANIC_DB["mic2"]
        checks, notes = data["checklist"], data["penyebab_umum"]

    elif any("batt" in s or "ntc" in s for s in sensors):
        data = PANIC_DB["battery_ntc"]
        checks, notes = data["checklist"], data["penyebab_umum"]

    elif ctx.get("contains_thermalmonitord"):
        data = PANIC_DB["thermalmonitord"]
        checks, notes = data["checklist"], data["penyebab_umum"]

    elif "userspace_watchdog" in ctx:
        data = PANIC_DB["userspace_watchdog"]
        checks, notes = data["checklist"], data["penyebab_umum"]

    else:
        data = PANIC_DB["default"]
        checks, notes = data["checklist"], data["penyebab_umum"]

    return data["kategori"], checks, notes, data["keterangan"]

# ======================
# Streamlit UI 🎨
# ======================
st.set_page_config(page_title="IDT Panic-Full Reader", page_icon="📱", layout="wide")

st.title("📱 IDT Panic Full Reader v1 by IDT")
st.subheader("Panic-Full Log Analyzer (iPhone)")

uploaded_file = st.file_uploader("Unggah file Panic-Full (.txt / .ips / .log)", type=["txt", "ips", "log"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    ctx = extract_all(text)
    kategori, checklist, notes, keterangan = generate_checklist(ctx)

    st.markdown(f"### 📌 Hasil Analisa")
    st.write(f"**Device:** {ctx.get('device', 'Tidak diketahui')}")
    st.write(f"**iOS:** {ctx.get('ios_version', 'Tidak diketahui')}")
    st.write(f"**Kategori:** {kategori}")
    st.write(f"**Catatan:** {keterangan}")

    st.markdown("#### ⚡ Penyebab Umum")
    for n in notes:
        st.write(f"- {n}")

    st.markdown("#### 🛠 Checklist Perbaikan")
    df = pd.DataFrame(checklist)
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("© 2025 Semua di develop sendiri tidak dengan team. Tools bebas untuk digunakkan dan Gratis | Interested in collaboration 👉 @maxxjen1 on Instagram")




