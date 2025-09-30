# =======================================
# 📱 DokterHP Panic-Full Reader (iPhone)
# v1.1 by IDT
# =======================================

import streamlit as st
import re
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ======================
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
# Regex Extractor 🔍
# ======================
RE_PATTERNS = {
    "device": re.compile(r'product:\s*([^\s,;]+)', re.I),
    "ios_version": re.compile(r'iOS Version:\s*([^\n\r]+)|OS Version:\s*([^\n\r]+)', re.I),
    "panic_string": re.compile(r'panicString:\s*(.+)', re.I),
    "missing_sensors": re.compile(r'Missing sensor\(s\):\s*([^\n\r]+)', re.I),
    "userspace_watchdog": re.compile(r'userspace watchdog timeout:\s*(.+)', re.I),
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
    checks, notes = [], []

    if "mic2" in sensors:
        data = PANIC_DB["mic2"]
    elif any("batt" in s or "ntc" in s for s in sensors):
        data = PANIC_DB["battery_ntc"]
    elif ctx.get("contains_thermalmonitord"):
        data = PANIC_DB["thermalmonitord"]
    elif "userspace_watchdog" in ctx:
        data = PANIC_DB["userspace_watchdog"]
    else:
        data = PANIC_DB["default"]

    return data["kategori"], data["checklist"], data["penyebab_umum"], data["keterangan"]

# ======================
# Report Generator 📄
# ======================
def export_report(device, ios, kategori, notes, checklist, keterangan, format="txt"):
    if format == "txt":
        content = f"""📱 DokterHP Panic-Full Report
=============================
Device   : {device}
iOS      : {ios}
Kategori : {kategori}

📌 Catatan
{keterangan}

⚡ Penyebab Umum
- """ + "\n- ".join(notes) + """

🛠 Checklist
"""
        for row in checklist:
            content += f"- {row['bagian']} ({row['letak']}) → {row['tindakan']}\n"
        return BytesIO(content.encode("utf-8"))

    elif format == "pdf":
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("📱 DokterHP Panic-Full Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"<b>Device:</b> {device}", styles["Normal"]))
        elements.append(Paragraph(f"<b>iOS:</b> {ios}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Kategori:</b> {kategori}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>📌 Catatan</b>", styles["Heading3"]))
        elements.append(Paragraph(keterangan, styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>⚡ Penyebab Umum</b>", styles["Heading3"]))
        for n in notes:
            elements.append(Paragraph(f"- {n}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>🛠 Checklist</b>", styles["Heading3"]))
        table_data = [["Bagian", "Letak", "Tindakan"]]
        for row in checklist:
            table_data.append([row["bagian"], row["letak"], row["tindakan"]])
        table = Table(table_data, colWidths=[120, 120, 200])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer

# ======================
# Streamlit UI 🎨
# ======================
st.set_page_config(page_title="DokterHP Panic-Full Reader", page_icon="📱", layout="wide")

st.title("📱 DokterHP v1.1 by IDT")
st.subheader("Panic-Full Log Analyzer (iPhone) + Export Report")

uploaded_file = st.file_uploader("Unggah file Panic-Full (.txt / .log)", type=["txt", "log"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    ctx = extract_all(text)
    kategori, checklist, notes, keterangan = generate_checklist(ctx)

    device = ctx.get("device", "Tidak diketahui")
    ios = ctx.get("ios_version", "Tidak diketahui")

    st.markdown(f"### 📌 Hasil Analisa")
    st.write(f"**Device:** {device}")
    st.write(f"**iOS:** {ios}")
    st.write(f"**Kategori:** {kategori}")
    st.write(f"**Catatan:** {keterangan}")

    st.markdown("#### ⚡ Penyebab Umum")
    for n in notes:
        st.write(f"- {n}")

    st.markdown("#### 🛠 Checklist Perbaikan")
    df = pd.DataFrame(checklist)
    st.dataframe(df, use_container_width=True)

    # Export Buttons
    st.markdown("### 📤 Export Report")
    col1, col2 = st.columns(2)

    with col1:
        txt_file = export_report(device, ios, kategori, notes, checklist, keterangan, "txt")
        st.download_button("⬇️ Download TXT", txt_file, file_name="panic_report.txt")

    with col2:
        pdf_file = export_report(device, ios, kategori, notes, checklist, keterangan, "pdf")
        st.download_button("⬇️ Download PDF", pdf_file, file_name="panic_report.pdf")

st.markdown("---")
st.caption("© 2025 DokterHP v1.1 by IDT | Collaboration 👉 @maxxjen1 on Instagram")
