import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Oil Market Intelligence", page_icon="🛢️", layout="wide")
st.title("🛢️ Oil Market Intelligence Dashboard")
st.markdown("**Análisis de mercados de crudo — WTI & Brent**")
st.markdown("---")

@st.cache_data(ttl=3600)
def cargar_datos():
    wti = yf.download("CL=F", period="2y", interval="1wk", progress=False, auto_adjust=True)
    brent = yf.download("BZ=F", period="2y", interval="1wk", progress=False, auto_adjust=True)
    wti = wti[["Close"]].copy()
    brent = brent[["Close"]].copy()
    wti.columns = ["WTI"]
    brent.columns = ["Brent"]
    df = pd.concat([wti, brent], axis=1).dropna().reset_index()
    df.columns = ["period", "WTI", "Brent"]
    df["Spread"] = df["WTI"] - df["Brent"]
    df["volatilidad"] = df["WTI"].pct_change().rolling(4).std() * 100
    return df

# Eventos geopolíticos clave
EVENTOS = [
    {"fecha": "2023-10-07", "label": "Ataque Hamas a Israel",         "color": "#E8593C"},
    {"fecha": "2023-11-22", "label": "Tregua Gaza",                   "color": "#3B8BD4"},
    {"fecha": "2024-01-12", "label": "EEUU ataca Houthis en Yemen",   "color": "#E8593C"},
    {"fecha": "2024-04-01", "label": "Ataque Iran a Israel",          "color": "#E8593C"},
    {"fecha": "2024-06-02", "label": "OPEC+ extiende recortes",       "color": "#F2A623"},
    {"fecha": "2024-09-05", "label": "OPEC+ retrasa aumento oferta",  "color": "#F2A623"},
    {"fecha": "2024-11-05", "label": "Elecciones EEUU — Trump gana",  "color": "#9B59B6"},
    {"fecha": "2025-01-20", "label": "Trump: drill baby drill",       "color": "#9B59B6"},
    {"fecha": "2025-03-04", "label": "OPEC+ anuncia aumento oferta",  "color": "#F2A623"},
]

with st.spinner("Cargando datos de mercado..."):
    df = cargar_datos()

if df.empty:
    st.error("No se pudieron cargar los datos. Recarga la página.")
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("WTI actual",       f"${df['WTI'].iloc[-1]:.2f}",    f"{df['WTI'].iloc[-1] - df['WTI'].iloc[-2]:.2f}")
col2.metric("Brent actual",     f"${df['Brent'].iloc[-1]:.2f}",  f"{df['Brent'].iloc[-1] - df['Brent'].iloc[-2]:.2f}")
col3.metric("Spread WTI-Brent", f"${df['Spread'].iloc[-1]:.2f}", f"{df['Spread'].iloc[-1] - df['Spread'].iloc[-2]:.2f}")
col4.metric("Volatilidad 4s",   f"{df['volatilidad'].iloc[-1]:.2f}%")

st.markdown("---")

# Gráfico 1 — WTI vs Brent con eventos geopolíticos
st.subheader("📈 WTI vs Brent — Contexto geopolítico")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df["period"], y=df["WTI"],   name="WTI",   line=dict(color="#E8593C", width=2)))
fig1.add_trace(go.Scatter(x=df["period"], y=df["Brent"], name="Brent", line=dict(color="#3B8BD4", width=2)))

for ev in EVENTOS:
    fig1.add_vline(
        x=ev["fecha"],
        line_dash="dash",
        line_color=ev["color"],
        line_width=1.5,
        annotation_text=ev["label"],
        annotation_position="top left",
        annotation_font_size=9,
        annotation_font_color=ev["color"]
    )

fig1.update_layout(height=500, template="plotly_dark", showlegend=True)
st.plotly_chart(fig1, use_container_width=True)

# Leyenda de colores
st.markdown("""
🔴 **Rojo** — Escalada bélica / tensión geopolítica &nbsp;&nbsp;
🔵 **Azul** — Distensión / acuerdos &nbsp;&nbsp;
🟡 **Amarillo** — Decisiones OPEC+ &nbsp;&nbsp;
🟣 **Morado** — Política EEUU
""")

st.markdown("---")

# Gráfico 2 — Spread
st.subheader("📊 Spread WTI - Brent")
fig2 = go.Figure()
colores_spread = ["#E8593C" if x >= 0 else "#3B8BD4" for x in df["Spread"]]
fig2.add_trace(go.Bar(x=df["period"], y=df["Spread"], name="Spread", marker_color=colores_spread))
fig2.add_hline(y=0, line_dash="dash", line_color="gray")
fig2.update_layout(height=350, template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Gráfico 3 — Volatilidad
st.subheader("📉 Volatilidad 4 semanas (WTI)")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["period"], y=df["volatilidad"], name="Volatilidad %", fill="tozeroy", line=dict(color="#F2A623", width=2)))
fig3.update_layout(height=350, template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("Datos: Yahoo Finance · Eventos: elaboración propia · Actualización: cada hora")
