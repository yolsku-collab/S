from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import base64
# convert gambar ke base64
def get_base64(img_file):
    with open(img_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo = get_base64("logo_palmwise.png")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

# ✅ HEADER (logo + judul)

mode_theme = st.toggle("🌙 Dark Mode", value=True)

if mode_theme:
    bg = "#020617"
    secondary_bg = "#0f172a"
    text = "#ffffff"
    subtext = "#9ca3af"
    accent = "#38bdf8"
    glass = "rgba(255,255,255,0.06)"
    border = "rgba(255,255,255,0.1)"
    plotly_theme = "plotly_dark"
else:
    bg = "#f8fafc"
    secondary_bg = "#ffffff"
    text = "#0f172a"
    subtext = "#475569"
    accent = "#2563eb"
    glass = "rgba(0,0,0,0.05)"
    border = "rgba(0,0,0,0.1)"
    plotly_theme = "plotly_white"

st.markdown(f"""
<style>

/* Background utama */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, {bg}, {secondary_bg});
    color: {text};
}}

header {{visibility:hidden;}}

/* Navbar */
.navbar {{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:12px 30px;
    border-radius:16px;
    background:{glass};
    backdrop-filter:blur(12px);
    border:1px solid {border};
    margin-bottom:20px;
}}

.nav-title {{
    font-size:20px;
    font-weight:600;
    color:{text};
}}

.nav-menu span {{
    margin-left:20px;
    cursor:pointer;
    color:{subtext};
    transition:0.3s;
}}

.nav-menu span:hover {{
    color:{accent};
}}

/* Header */
.header {{
    display:flex;
    align-items:center;
    gap:30px;
    padding:30px;
    border-radius:20px;
    background:{glass};
    backdrop-filter:blur(16px);
    border:1px solid {border};
}}

/* Logo */
.logo-wrapper {{
    width:150px;
    height:150px;
    min-width:150px;
    min-height:150px;
    border-radius:50%;
    overflow:hidden;
    flex-shrink:0;
    border:3px solid {accent};
}}

.logo-wrapper img {{
    width:100%;
    height:100%;
    object-fit:cover;
}}

/* Title */
.title {{
    font-size:56px;
    font-weight:800;
    color:{text};
}}

.subtitle {{
    font-size:20px;
    color:{subtext};
    max-width:700px;
}}

/* Glass */
.glass {{
    background:{glass};
    border-radius:18px;
    padding:20px;
    backdrop-filter:blur(18px);
    border:1px solid {border};
    margin-bottom:20px;
}}

/* Heading */
h1,h2,h3 {{
    color:{accent};
}}

/* Responsive HP */
@media (max-width:768px){{
    .header {{
        flex-direction:column;
        text-align:center;
    }}

    .logo-wrapper {{
        width:110px;
        height:110px;
        min-width:110px;
        min-height:110px;
    }}

    .title {{
        font-size:32px;
    }}

    .subtitle {{
        font-size:16px;
    }}
}}

</style>
""", unsafe_allow_html=True)


# ================= DATABASE =================
bibit_db = {
    "DxP PPKS": {"skor": 90, "produksi": "28–32 ton/ha"},
    "Tenera Socfindo": {"skor": 85, "produksi": "25–30 ton/ha"},
    "Lonsum": {"skor": 80, "produksi": "22–28 ton/ha"}
}

tanah_db = {
    "Latosol": {"skor": 90, "ph": "5.0–6.5"},
    "Podsolik": {"skor": 75, "ph": "4.5–5.5"},
    "Gambut": {"skor": 60, "ph": "3.0–4.0"}
}

biaya_db = {
    "Latosol": 28000000,
    "Podsolik": 32000000,
    "Gambut": 38000000
}

# ================= INPUT =================
mode = st.radio("Input Data:", ["Manual", "Upload Excel"], horizontal=True)

if mode == "Manual":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("✍️ Input Agronomi")

    jumlah = st.number_input("Jumlah Alternatif", 1, 10, 3)

    data_list = []

    for i in range(jumlah):
        c1, c2, c3, c4 = st.columns(4)

        alt = c1.text_input(f"Alt {i+1}", f"A{i+1}", key=f"a{i}")
        tanah = c2.selectbox(f"Tanah {i+1}", list(tanah_db.keys()), key=f"t{i}")
        bibit = c3.selectbox(f"Bibit {i+1}", list(bibit_db.keys()), key=f"b{i}")
        ekonomi = c4.number_input(f"Ekonomi {i+1}", 0, 100, 70, key=f"e{i}")

        lahan_score = tanah_db[tanah]["skor"]
        bibit_score = bibit_db[bibit]["skor"]

        data_list.append([alt, lahan_score, bibit_score, ekonomi, tanah, bibit])

    df = pd.DataFrame(data_list, columns=[
        "Alternatif","Lahan","Bibit","Ekonomi","Tanah","Jenis Bibit"
    ])
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    file = st.file_uploader("Upload Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
    else:
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= DATA =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📊 Data")
st.dataframe(df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================= AHP =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("⚖️ AHP")

c1,c2,c3 = st.columns(3)
w1 = c1.slider("Lahan vs Bibit",1,9,3)
w2 = c2.slider("Lahan vs Ekonomi",1,9,4)
w3 = c3.slider("Bibit vs Ekonomi",1,9,2)

matrix = np.array([
    [1,w1,w2],
    [1/w1,1,w3],
    [1/w2,1/w3,1]
])

norm = matrix / matrix.sum(axis=0)
weights = norm.mean(axis=1)

eigval = np.max(np.linalg.eigvals(matrix).real)
CR = ((eigval-3)/2)/0.58

st.dataframe(pd.DataFrame({
    "Kriteria":["Lahan","Bibit","Ekonomi"],
    "Bobot":weights
}))
st.info(f"CR = {CR:.3f}")
st.markdown('</div>', unsafe_allow_html=True)

# ================= SAW =================
norm_df = df[["Lahan","Bibit","Ekonomi"]].copy()
for col in norm_df.columns:
    norm_df[col] /= norm_df[col].max()

df["Skor"] = (
    norm_df["Lahan"]*weights[0] +
    norm_df["Bibit"]*weights[1] +
    norm_df["Ekonomi"]*weights[2]
)

df = df.sort_values("Skor", ascending=False)
best = df.iloc[0]

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🏆 Ranking")
st.dataframe(df)
st.success(f"Terbaik: {best['Alternatif']}")
st.markdown('</div>', unsafe_allow_html=True)

# ================= AI PRODUKSI =================
tahun = np.arange(1,26).reshape(-1,1)

produksi_jurnal = np.array([
    0,0,3,8,15,20,25,28,30,30,
    29,28,27,26,25,24,23,22,21,20,
    18,16,14,12,10
])

model = LinearRegression()
model.fit(tahun, produksi_jurnal)

prediksi = model.predict(tahun) * best["Skor"]

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📈 Grafik Produksi")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=tahun.flatten(),
    y=prediksi,
    mode='lines+markers',
    line=dict(width=4)
))

peak = np.argmax(prediksi)

fig.add_trace(go.Scatter(
    x=[tahun.flatten()[peak]],
    y=[prediksi[peak]],
    mode='markers+text',
    text=["Peak"],
    textposition="top center"
))

fig.update_layout(template=plotly_theme)
st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ================= EKONOMI =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("💰 Analisis Ekonomi")

harga = st.slider("Harga TBS (Rp/kg)",1500,3500,2500)

tanah = best["Tanah"]
biaya = biaya_db[tanah]

if best["Skor"] >= 0.8:
    produksi_ton = 30
elif best["Skor"] >= 0.6:
    produksi_ton = 25
else:
    produksi_ton = 20

pendapatan = produksi_ton*1000*harga
keuntungan = pendapatan - biaya
roi = (keuntungan/biaya)*100

col1,col2,col3,col4 = st.columns(4)
col1.metric("Biaya", f"Rp {biaya:,}")
col2.metric("Produksi", f"{produksi_ton} ton")
col3.metric("Pendapatan", f"Rp {pendapatan:,.0f}")
col4.metric("ROI", f"{roi:.2f}%")

st.markdown('</div>', unsafe_allow_html=True)

# ================= REKOMENDASI =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🌱 Rekomendasi")

if tanah == "Gambut":
    pupuk = "Dolomit + NPK + Organik"
elif tanah == "Podsolik":
    pupuk = "NPK + Urea + KCl"
else:
    pupuk = "NPK + Kompos"

st.write(f"""
- Pupuk: {pupuk}  
- Panen: 30–36 bulan  
- Produksi: {produksi_ton} ton/ha  
- ROI: {roi:.2f}%  
""")

# ================= EXPORT EXCEL =================
def create_excel():
    df = pd.DataFrame({
        "Parameter": ["Tanah", "Pupuk", "Produksi", "ROI"],
        "Nilai": [tanah, pupuk, produksi_ton, f"{roi:.2f}%"]
    })

    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

excel = create_excel()

st.download_button(
    label="📥 Download Excel",
    data=excel,
    file_name="laporan_spk_sawit.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown('</div>', unsafe_allow_html=True)

# ================= INSIGHT =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🧠 Insight")

st.write(f"""
Alternatif {best['Alternatif']} terbaik berdasarkan kombinasi agronomi dan ekonomi.
Sistem menunjukkan bahwa kualitas lahan dan bibit sangat mempengaruhi hasil produksi dan keuntungan.
""")

st.markdown('</div>', unsafe_allow_html=True)

st.subheader("📊 KPI Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Jumlah Alternatif", len(df))
col2.metric("Alternatif Terbaik", best["Alternatif"])
col3.metric("Nilai SAW Tertinggi", round(best["Skor"], 3))
