from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import base64
# convert Logo ke base64
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

# ================= FUNGSI SKOR LAHAN =================
def hitung_skor_lahan(jenis, curah, ph, tinggi, weights):
   

    skor_tanah = {
        "Latosol": 90,
        "Podsolik": 75,
        "Gambut": 60
    }[jenis]

    # curah hujan
    if 2000 <= curah <= 3000:
        skor_hujan = 90
    elif 1500 <= curah < 2000 or 3000 < curah <= 3500:
        skor_hujan = 75
    else:
        skor_hujan = 60

    # pH
    if 5 <= ph <= 6.5:
        skor_ph = 90
    elif 4 <= ph < 5 or 6.5 < ph <= 7:
        skor_ph = 75
    else:
        skor_ph = 60

    # Ketinggian
    if tinggi <= 200:
        skor_tinggi = 90
    elif tinggi <= 500:
        skor_tinggi = 75
    else:
        skor_tinggi = 60

    skor_total = (
        skor_tanah * weights[0] +
        skor_hujan * weights[1] +
        skor_ph * weights[2] +
        skor_tinggi * weights[3]
    )

    return skor_total

# ✅ HEADER (logo + judul)

mode_theme = st.toggle("🌙 Dark Mode", value=True)
# ================= HEADER =================
st.markdown(f"""
<div class="header">
    <div class="logo-wrapper">
        <img src="data:image/png;base64,{logo}">
    </div>
    <div>
        <div class="title">PalmWise</div>
        <div class="subtitle">
            Smart Decision Support System for Oil Palm
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
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
    bg = "#f1f5f9"
    secondary_bg = "#ffffff"
    text = "#0f172a"
    subtext = "#334155"   # 🔥 lebih gelap biar kebaca
    accent = "#1d4ed8"
    glass = "rgba(0,0,0,0.05)"
    border = "rgba(0,0,0,0.1)"
    plotly_theme = "plotly_white"
# ========================= CSS ========================================================================================

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

.stRadio label {{
    font-size:16px;
    font-weight:500;
}}

.stRadio div[role="radiogroup"] {{
    background: rgba(255,255,255,0.05);
    padding:10px;
    border-radius:12px;
    justify-content:center;
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

h1,h2,h3 {{
    color:{accent};
}}

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
}}

/* 🔥 TAMBAHAN NAVIGASI */
.stRadio > div {{
    justify-content: center;
    gap: 20px;
}}
/* card bobot */
.bobot-card {{
    padding: 16px;
    border-radius: 16px;
    background: {glass};
    border: 1px solid {border};
    text-align: center;
    transition: 0.3s;
    margin-bottom: 8px;
}}

/* 🔥 TARUH DI SINI */
.bobot-card:hover {{
    transform: scale(1.05);
}}

.bobot-title {{
    font-size: 14px;
    color: {subtext};
}}

.bobot-value {{
    font-size: 24px;
    font-weight: bold;
}}
/* 🔥 FIX JARAK KOLOM */
div[data-testid="column"] {{
    margin-bottom: 4px !important;
}}
/* Biar CR Rapih*/    
.stAlert {{
    margin-top: 8px;
}}

</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
st.markdown("### ")

menu = st.radio(
    "",
    ["🏠 Home", "📊 Dashboard", "📈 Analisis", "ℹ️ About"],
    horizontal=True
)
if menu == "🏠 Home":
    st.markdown(f"""
    <div class="glass">
        <h3>👋 Selamat datang di PalmWise</h3>
        <p>
        Sistem pendukung keputusan untuk menentukan kelayakan lahan kelapa sawit 
        menggunakan metode <b>AHP + SAW</b> serta analisis berbasis AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown("""
    <div class="glass">
        <h4>📊 Dashboard</h4>
        <p>Monitoring data lahan & perhitungan</p>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown("""
    <div class="glass">
        <h4>⚖️ AHP-SAW</h4>
        <p>Perhitungan kelayakan lahan</p>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown("""
    <div class="glass">
        <h4>📈 Analisis</h4>
        <p>Prediksi & visualisasi produksi</p>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📊 Dashboard":

    st.markdown("## 📊 Dashboard Hasil Keputusan")

    # VALIDASI
    if "df" not in st.session_state:
        st.warning("⚠️ Silakan isi dan hitung data di halaman Analisis terlebih dahulu")
        st.stop()

    df = st.session_state["df"]
    best = st.session_state["best"]

    # ================= CARD UTAMA =================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏆 Alternatif Terbaik", best["Alt"])
    col2.metric("🌱 Lahan Terbaik", best["Tanah"])
    col3.metric("🌿 Bibit Terbaik", best["BibitJenis"])
    col4.metric("⭐ Skor Akhir", f"{best['Skor']:.3f}")

    # ================= DETAIL =================
    st.markdown("### 📊 Detail Nilai Terbaik")

    c1, c2, c3 = st.columns(3)

    c1.metric("Skor Lahan", f"{best['Lahan']:.2f}")
    c2.metric("Skor Bibit", f"{best['Bibit']:.2f}")
    c3.metric("Skor Ekonomi", f"{best['Ekonomi']:.0f}")

    # ================= TABEL RANKING =================
    st.markdown("### 🏆 Ranking Lengkap")
    st.dataframe(df, use_container_width=True)

    # ================= INSIGHT =================
    st.success(f"""
✅ Rekomendasi terbaik adalah **{best['Alt']}**
🌱 Tanah: {best['Tanah']}
🌿 Bibit: {best['BibitJenis']}
💰 Skor akhir: {best['Skor']:.3f}
""")
    # TARUH: INPUT + DATA + AHP + SAW di sini

elif menu == "📈 Analisis":
    st.warning("Analisis Produksi & Ekonomi")
    # TARUH: GRAFIK + EKONOMI di sini

elif menu == "ℹ️ About":
    st.write("PalmWise adalah sistem SPK untuk kelapa sawit berbasis AHP-SAW + AI")

# ================= DATABASE =================
bibit_db = {
    "DxP PPKS": {
        "produktivitas": 30,   # ton/ha/tahun
        "ketahanan": 90,
        "umur_panen": 30,      # bulan
        "skor": 90
    },
    "Tenera Socfindo": {
        "produktivitas": 28,
        "ketahanan": 85,
        "umur_panen": 32,
        "skor": 85
    },
    "Lonsum": {
        "produktivitas": 25,
        "ketahanan": 80,
        "umur_panen": 34,
        "skor": 80
    }
}

biaya_db = {
    "Latosol": {"investasi": 28000000, "operasional": 8000000},
    "Podsolik": {"investasi": 32000000, "operasional": 10000000},
    "Gambut": {"investasi": 38000000, "operasional": 12000000}
}

# ================== AHP LAHAN ==============
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("⚖️ AHP Lahan")

w1 = st.slider("Tanah vs Curah Hujan",1,9,3)
w2 = st.slider("Tanah vs pH",1,9,4)
w3 = st.slider("Tanah vs Ketinggian",1,9,5)
w4 = st.slider("Curah Hujan vs pH",1,9,3)
w5 = st.slider("Curah Hujan vs Ketinggian",1,9,4)
w6 = st.slider("pH vs Ketinggian",1,9,3)

matrix = np.array([
    [1,w1,w2,w3],
    [1/w1,1,w4,w5],
    [1/w2,1/w4,1,w6],
    [1/w3,1/w5,1/w6,1]
])

norm = matrix / matrix.sum(axis=0)
weights_lahan = norm.mean(axis=1)

# ================= HITUNG CR =================
n_kriteria = matrix.shape[0]

# λ max
eigval = np.max(np.linalg.eigvals(matrix).real)

# Consistency Index
CI = (eigval - n_kriteria) / (n_kriteria - 1)

# Random Index
RI_dict = {
    1: 0.0,
    2: 0.0,
    3: 0.58,
    4: 0.90,
    5: 1.12
}

RI = RI_dict[n_kriteria]

# Consistency Ratio
CR = CI / RI if RI != 0 else 0

# ================= OUTPUT =================
kriteria = ["Tanah", "Curah Hujan", "pH", "Ketinggian"]

df_bobot = pd.DataFrame({
    "Kriteria": kriteria,
    "Bobot": weights_lahan
})

df_bobot["Persen"] = df_bobot["Bobot"] * 100
df_bobot["Rank"] = df_bobot["Bobot"].rank(ascending=False).astype(int)

df_bobot = df_bobot.sort_values("Rank")

st.markdown("### 📊 Bobot Kriteria")

cols = st.columns(len(df_bobot))

for col, (_, row) in zip(cols, df_bobot.iterrows()):

    color = "#22c55e" if row['Rank']==1 else "#38bdf8"

    with col:
        st.markdown(f"""
        <div class="bobot-card" style="text-align:center;">
            <div class="bobot-title">{row['Kriteria']}</div>
            <div class="bobot-rank">Rank #{row['Rank']}</div>
            <div class="bobot-value" style="color:{color};">
                {row['Bobot']:.3f}
            </div>
            <div style="font-size:12px; color:#9ca3af;">
                {row['Persen']:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
if CR < 0.1:
    st.success(f"CR Lahan = {CR:.3f} (Konsisten ✅)")
else:
    st.error(f"CR Lahan = {CR:.3f} (Tidak Konsisten ❌)")
if CR >= 0.1:
    st.warning("Perbandingan belum konsisten, silakan ubah nilai AHP!")
    st.stop()    

# ================= FUNGSI LAHAN =================
def skor_lahan(jenis, curah, ph, tinggi):

    skor_tanah = {"Latosol":90,"Podsolik":75,"Gambut":60}[jenis]

    skor_hujan = 90 if 2000<=curah<=3000 else 75 if 1500<=curah<=3500 else 60
    skor_ph = 90 if 5<=ph<=6.5 else 75 if 4<=ph<=7 else 60
    skor_tinggi = 90 if tinggi<=200 else 75 if tinggi<=500 else 60

    return (
        skor_tanah * weights_lahan[0] +
        skor_hujan * weights_lahan[1] +
        skor_ph * weights_lahan[2] +
        skor_tinggi * weights_lahan[3]
    )

# ================= INPUT =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📥 Input Data")

n = st.number_input("Jumlah Alternatif",1,10,3, key="jumlah_alt")

data=[]

for i in range(n):
    st.markdown(f"### Alternatif {i+1}")
    c1,c2,c3,c4,c5 = st.columns(5)

    nama = c1.text_input("Nama", f"A{i+1}", key=f"nama_{i}")
    jenis = c2.selectbox("Tanah", ["Latosol","Podsolik","Gambut"], key=f"tanah_{i}")
    hujan = c3.number_input("Curah Hujan",1500,4000,2500,key=f"hujan_{i}")
    ph = c4.number_input("pH",3.0,8.0,5.5,key=f"ph_{i}")
    tinggi = c5.number_input("Ketinggian",0,1000,100,key=f"tinggi_{i}")
    bibit = st.selectbox("Bibit", list(bibit_db.keys()), key=f"bibit_{i}")

    # ================= EKONOMI REAL =================
    st.markdown("#### 💰 Input Ekonomi")

    c6, c7, c8 = st.columns(3)

    harga = c6.number_input("Harga TBS (Rp/kg)", 1500, 4000, 2500, key=f"harga_{i}")
    biaya_invest = c7.number_input("Biaya Investasi (Rp)", 0, 100000000, 30000000, key=f"invest_{i}")
    biaya_operasional = c8.number_input("Biaya Operasional (Rp/tahun)", 0, 50000000, 10000000, key=f"operasional_{i}")

   # ================= HITUNG SKOR =================
    lahan = hitung_skor_lahan(jenis, hujan, ph, tinggi, weights_lahan)

    # ================= PRODUKSI =================
    produksi_dasar = bibit_db[bibit]["produktivitas"]
    produksi = produksi_dasar * (lahan / 100)

    # ================= EKONOMI =================
    pendapatan = produksi * 1000 * harga
    total_biaya = biaya_invest + biaya_operasional
    keuntungan = pendapatan - total_biaya
    ekonomi = pendapatan - total_biaya

    bibit_score = bibit_db[bibit]["skor"]
# ====================== Simpan Data =========================
    data.append([nama, lahan, bibit_score, ekonomi, jenis, bibit])
# ===== DATAFRAME (LUAR LOOP) =====
df = pd.DataFrame(data,columns=["Alt","Lahan","Bibit","Ekonomi","Tanah","BibitJenis"])

st.dataframe(df)
st.markdown('</div>', unsafe_allow_html=True)

# ================= DATA =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("📊 Data")
st.dataframe(df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================= AHP UTAMA =================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("⚖️ AHP Utama")

a = st.slider("Lahan vs Bibit",1,9,3)
b = st.slider("Lahan vs Ekonomi",1,9,4)
c = st.slider("Bibit vs Ekonomi",1,9,2)

m = np.array([[1,a,b],[1/a,1,c],[1/b,1/c,1]])
w = (m/m.sum(axis=0)).mean(axis=1)

eigval2 = np.max(np.linalg.eigvals(m).real)
CI2 = (eigval2 - 3) / 2
CR2 = CI2 / 0.58

st.info(f"CR Utama: {CR2:.3f}")
if CR2 < 0.1:
    st.success("Konsisten ✅")
else:
    st.error("Tidak konsisten ❌, silakan ubah perbandingan")
st.write("Bobot:",w)
st.markdown('</div>', unsafe_allow_html=True)

# ================= SAW =================
# normalisasi
norm_df = df[["Lahan","Bibit","Ekonomi"]].copy()

# semua kriteria benefit
for col in norm_df.columns:
    max_val = norm_df[col].max()
    if max_val != 0:
        norm_df[col] = norm_df[col] / max_val

# hitung skor akhir
df["Skor"] = (
    norm_df["Lahan"] * w[0] +
    norm_df["Bibit"] * w[1] +
    norm_df["Ekonomi"] * w[2]
)

# ranking
df = df.sort_values("Skor", ascending=False)
best = df.iloc[0]

st.session_state["df"] = df
st.session_state["best"] = best

# tampilkan
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("🏆 Ranking Alternatif")

st.dataframe(df, use_container_width=True)

st.success(f"""
Alternatif terbaik adalah **{best['Alt']}**
dengan nilai preferensi **{best['Skor']:.3f}**
""")
st.markdown('</div>', unsafe_allow_html=True)

# ================= AI PRODUKSI =================
tahun = np.arange(1,26)
produksi = np.array([0,0,3,8,15,20,25,28,30,30,29,28,27,26,25,24,23,22,21,20,18,16,14,12,10])
model = LinearRegression().fit(tahun.reshape(-1,1),produksi)
pred = model.predict(tahun.reshape(-1,1))*best["Skor"]

fig = go.Figure()

fig.add_trace(go.Scatter(x=tahun,y=produksi,name="Literatur",line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=tahun,y=pred,name="Prediksi",mode='lines+markers'))

peak = np.argmax(pred)
fig.add_trace(go.Scatter(x=[tahun[peak]],y=[pred[peak]],mode='markers+text',text=["Peak"]))

fig.update_layout(title="Produksi Sawit",template=plotly_theme)
st.plotly_chart(fig,use_container_width=True)

# ================= EKONOMI =================
harga = st.slider("Harga TBS",1500,3500,2500)

tanah = best["Tanah"]

biaya = biaya_db[tanah]["investasi"] + biaya_db[tanah]["operasional"]

# produksi berdasarkan skor
if best["Skor"] >= 0.8:
    produksi_ton = 30
elif best["Skor"] >= 0.6:
    produksi_ton = 25
else:
    produksi_ton = 20

pendapatan = produksi_ton * 1000 * harga
keuntungan = pendapatan - biaya
roi = (keuntungan / biaya) * 100

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.subheader("💰 Analisis Ekonomi")

col1, col2, col3, col4 = st.columns(4)
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
- **Jenis Tanah:** {tanah}  
- **Pupuk:** {pupuk}  
- **Umur Panen:** 30–36 bulan  
- **Produksi:** {produksi_ton} ton/ha  
- **ROI:** {roi:.2f}%  
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

top3 = df.head(3)

st.write(f"""
Alternatif terbaik adalah **{best['Alt']}** dengan skor **{best['Skor']:.3f}**.

📊 Analisis:
- Lahan terbaik didominasi oleh **{top3['Tanah'].mode()[0]}**
- Bibit yang sering muncul di ranking atas adalah **{top3['BibitJenis'].mode()[0]}**
- Nilai ekonomi tertinggi: **Rp {int(df['Ekonomi'].max()):,}**

📈 Kesimpulan:
Alternatif dengan kombinasi **lahan optimal + bibit unggul + ekonomi tinggi**
cenderung menghasilkan skor SAW terbaik.
""")

st.markdown('</div>', unsafe_allow_html=True)

st.subheader("📊 KPI Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Jumlah Alternatif", len(df))
col2.metric("Alternatif Terbaik", best["Alt"])
col3.metric("Nilai SAW Tertinggi", round(best["Skor"], 3))
col4.metric("Rata-rata Skor", round(df["Skor"].mean(),3))
col5.metric("Skor Terendah", round(df["Skor"].min(),3))

col6 = st.columns(1)[0]
col6.metric("Rentang Skor", round(df["Skor"].max() - df["Skor"].min(),3))