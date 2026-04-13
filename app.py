
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
    wti   = yf.download("CL=F", period="2y", interval="1wk")[["Close"]].reset_index()
    brent = yf.download("BZ=F", period="2y", interval="1wk")[["Close"]].reset_index()
    wti.columns   = ["period", "WTI"]
    brent.columns = ["period", "Brent"]
    df = wti.merge(brent, on="period")
    df["Spread"]     = df["WTI"] - df["Brent"]
    df["volatilidad"] = df["WTI"].pct_change().rolling(4).std() * 100
    return df

df = cargar_datos()

# KPIs en la parte superior
col1, col2, col3, col4 = st.columns(4)
col1.metric("WTI actual",    f"${df['WTI'].iloc[-1]:.2f}",    f"{df['WTI'].iloc[-1] - df['WTI'].iloc[-2]:.2f}")
col2.metric("Brent actual",  f"${df['Brent'].iloc[-1]:.2f}",  f"{df['Brent'].iloc[-1] - df['Brent'].iloc[-2]:.2f}")
col3.metric("Spread WTI-Brent", f"${df['Spread'].iloc[-1]:.2f}", f"{df['Spread'].iloc[-1] - df['Spread'].iloc[-2]:.2f}")
col4.metric("Volatilidad 4s",   f"{df['volatilidad'].iloc[-1]:.2f}%")

st.markdown("---")

# Gráficos
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=("WTI vs Brent (USD/barril)", "Spread WTI - Brent (USD)", "Volatilidad 4 semanas (WTI)"),
    vertical_spacing=0.12
)

fig.add_trace(go.Scatter(x=df["period"], y=df["WTI"],   name="WTI",   line=dict(color="#E8593C", width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=df["period"], y=df["Brent"], name="Brent", line=dict(color="#3B8BD4", width=2)), row=1, col=1)

colores_spread = ["#E8593C" if x >= 0 else "#3B8BD4" for x in df["Spread"]]
fig.add_trace(go.Bar(x=df["period"], y=df["Spread"], name="Spread", marker_color=colores_spread), row=2, col=1)
fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

fig.add_trace(go.Scatter(x=df["period"], y=df["volatilidad"], name="Volatilidad %", fill="tozeroy", line=dict(color="#F2A623", width=2)), row=3, col=1)

fig.update_layout(height=750, template="plotly_dark", showlegend=True)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Datos: Yahoo Finance · Actualización: cada hora · Desarrollado por [tu nombre]")
