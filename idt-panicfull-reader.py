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
# 2. Database Kerusakan
# ===============================
SYMPTOM_DB = {
    "charger": ["IC Charging", "Konektor Charger", "Flex Charger"],
    "nand": ["NAND Flash rusak", "CPU komunikasi gagal"],
    "baseband": ["IC Baseband rusak", "Jalur Baseband bermasalah"],
    "sensor": ["IC Tristar/Hydra", "Sensor Flex rusak"],
    "camera": ["Konektor kamera rusak", "IC Kamera"],
    "wifi": ["IC Wifi", "Antena rusak"],
    "touch": ["IC Touch", "Layar rusak"],
}

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

uploaded = st.file_uploader("Upload Panic Full Log  (.txt / .ips / .log)", type=["txt", "ips", "log"])
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

