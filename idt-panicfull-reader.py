import streamlit as st
import re
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="📱 Panic Full Reader v1 by IDT", layout="wide")

st.title("📱 Panic Full Reader v1 by IDT")
st.write("Upload file **panic-full log** iPhone (.txt atau .ips).")

# Regex pola
RE_PATTERNS = {
    'device': re.compile(r'product:\s*([^\s,;]+)', re.I),
    'ios_version': re.compile(r'iOS Version:\s*([^\n\r]+)|OS Version:\s*([^\n\r]+)', re.I),
    'panic_string': re.compile(r'panicString:\s*(.+)', re.I),
    'missing_sensors': re.compile(r'Missing sensor\(s\):\s*([^\n\r]+)', re.I),
    'userspace_watchdog': re.compile(r'userspace watchdog timeout:\s*(.+)', re.I),
}

# Checklist database
CHECKLISTS = {
    "mic2": [
        {"Bagian": "Dock Flex / Mic Bawah", "Letak": "Dock Flex (bawah)", "Tindakan": "Ganti flex / cek dengan flex normal"},
        {"Bagian": "Konektor J6300", "Letak": "Board bawah", "Tindakan": "Bersihkan / re-tin pin konektor"},
        {"Bagian": "Jalur SDA / SCL", "Letak": "Board bawah → PMIC", "Tindakan": "Continuity test jalur I²C ke PMIC"},
        {"Bagian": "Resistor Pull-up 1.8V", "Letak": "Dekat J6300", "Tindakan": "Ukur nilai resistor (hubung ke 1.8V)"}
    ],
    "battery_ntc": [
        {"Bagian": "Baterai", "Letak": "Baterai iPhone", "Tindakan": "Ganti baterai original/baru"},
        {"Bagian": "Flexible Baterai", "Letak": "Konektor baterai", "Tindakan": "Cek kondisi flex dan konektor"},
        {"Bagian": "Jalur NTC", "Letak": "Baterai → PMIC", "Tindakan": "Ukur continuity jalur NTC ke PMIC"}
    ],
    "thermalmonitord": [
        {"Bagian": "Sensor Suhu Baterai", "Letak": "Baterai", "Tindakan": "Cek apakah NTC masih terbaca"},
        {"Bagian": "PMIC", "Letak": "Board", "Tindakan": "Periksa apakah ada short / overheat"},
        {"Bagian": "Camera Flex", "Letak": "Flex kamera depan/belakang", "Tindakan": "Cek sensor suhu di kamera flex"}
    ],
    "default": [
        {"Bagian": "Baterai", "Letak": "Baterai iPhone", "Tindakan": "Ganti baterai original/baru"},
        {"Bagian": "Dock Flex", "Letak": "Board bawah", "Tindakan": "Coba ganti dock flex"},
        {"Bagian": "Camera Flex", "Letak": "Board atas", "Tindakan": "Coba ganti kamera flex"},
        {"Bagian": "Jalur I²C ke PMIC", "Letak": "Board", "Tindakan": "Continuity test jalur SDA/SCL ke PMIC"}
    ]
}

def extract_all(text):
    out = {}
    for k, pat in RE_PATTERNS.items():
        m = pat.search(text)
        if m:
            groups = [g for g in m.groups() if g]
            out[k] = groups[0].strip() if groups else m.group(0).strip()
    ms = re.findall(r'Missing sensor\(s\):\s*([^\n\r]+)', text, re.I)
    if ms:
        sensors = []
        for s in ms:
            sensors += re.split(r'[,\s]+', s.strip())
        out['missing_sensors_all'] = list(dict.fromkeys([x for x in sensors if x]))
    out['contains_thermalmonitord'] = bool(re.search(r'thermalmonitord', text, re.I))
    return out

def generate_checklist(ctx):
    sensors = [s.lower() for s in ctx.get('missing_sensors_all', [])]
    checks = []
    if "mic2" in sensors:
        checks += CHECKLISTS["mic2"]
    if any("batt" in s or "ntc" in s for s in sensors):
        checks += CHECKLISTS["battery_ntc"]
    if ctx.get("contains_thermalmonitord"):
        checks += CHECKLISTS["thermalmonitord"]
    if not checks:
        checks += CHECKLISTS["default"]
    return checks

uploaded = st.file_uploader("Upload file panic-full", type=["txt","ips"])

if uploaded:
    text = uploaded.read().decode("utf-8", errors="ignore")
    extracted = extract_all(text)
    checklist = generate_checklist(extracted)

    st.subheader("📋 Hasil Parsing")
    st.json(extracted)

    st.subheader("🛠 Checklist Perbaikan")
    df = pd.DataFrame(checklist)
    st.table(df)

    st.caption("© 2025 Panic Full Reader v1 by IDT — interested in collaboration @maxxjen1 on Instagram")
