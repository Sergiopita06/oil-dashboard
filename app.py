import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Oil Market Intelligence", page_icon="🛢️", layout="wide")

# Navegación por pestañas
tab1, tab2 = st.tabs(["📈 Market Dashboard", "🌍 Geopolitical Intelligence"])

# ─── DATOS ───────────────────────────────────────────────
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

EVENTOS = [
    {"fecha": "2023-10-07", "label": "Ataque Hamas a Israel",        "color": "#E8593C"},
    {"fecha": "2023-11-22", "label": "Tregua Gaza",                  "color": "#3B8BD4"},
    {"fecha": "2024-01-12", "label": "EEUU ataca Houthis en Yemen",  "color": "#E8593C"},
    {"fecha": "2024-04-01", "label": "Ataque Iran a Israel",         "color": "#E8593C"},
    {"fecha": "2024-06-02", "label": "OPEC+ extiende recortes",      "color": "#F2A623"},
    {"fecha": "2024-09-05", "label": "OPEC+ retrasa aumento oferta", "color": "#F2A623"},
    {"fecha": "2024-11-05", "label": "Elecciones EEUU — Trump gana", "color": "#9B59B6"},
    {"fecha": "2025-01-20", "label": "Trump: drill baby drill",      "color": "#9B59B6"},
    {"fecha": "2025-03-04", "label": "OPEC+ anuncia aumento oferta", "color": "#F2A623"},
]

ESTRECHOS = [
    {
        "nombre": "Estrecho de Hormuz",
        "pais": "Iran / Oman",
        "flujo_mbd": 21,
        "pct_global": 21,
        "riesgo": 85,
        "riesgo_label": "Muy alto",
        "color_riesgo": "#E8593C",
        "lat": 26.5, "lon": 56.5,
        "descripcion": "Paso obligado del petróleo de Arabia Saudita, Iraq, Kuwait, EAU e Iran. Un cierre elevaría el precio entre $20–$50/barril según estimaciones históricas."
    },
    {
        "nombre": "Bab-el-Mandeb",
        "pais": "Yemen / Djibouti",
        "flujo_mbd": 8.8,
        "pct_global": 9,
        "riesgo": 75,
        "riesgo_label": "Alto",
        "color_riesgo": "#F2A623",
        "lat": 12.5, "lon": 43.5,
        "descripcion": "Conecta el Mar Rojo con el Golfo de Aden. Los ataques Houthi desde 2023 han desviado tráfico hacia el Cabo de Buena Esperanza (+14 días de ruta)."
    },
    {
        "nombre": "Canal de Suez",
        "pais": "Egipto",
        "flujo_mbd": 5.5,
        "pct_global": 5,
        "riesgo": 40,
        "riesgo_label": "Moderado",
        "color_riesgo": "#F2A623",
        "lat": 30.5, "lon": 32.3,
        "descripcion": "Ruta clave entre el Mediterráneo y el Mar Rojo. El bloqueo del Ever Given en 2021 costó $9.6B/día al comercio global."
    },
    {
        "nombre": "Estrecho de Malacca",
        "pais": "Malaysia / Indonesia / Singapur",
        "flujo_mbd": 16,
        "pct_global": 16,
        "riesgo": 30,
        "riesgo_label": "Moderado",
        "color_riesgo": "#3B8BD4",
        "lat": 2.5, "lon": 101.5,
        "descripcion": "Principal ruta de suministro hacia China, Japón y Corea del Sur. Riesgo actual bajo pero crítico para Asia-Pacífico."
    },
    {
        "nombre": "Cabo de Buena Esperanza",
        "pais": "Sudáfrica",
        "flujo_mbd": 4,
        "pct_global": 4,
        "riesgo": 10,
        "riesgo_label": "Bajo",
        "color_riesgo": "#2ECC71",
        "lat": -34.4, "lon": 18.5,
        "descripcion": "Ruta alternativa usada cuando Suez o Bab-el-Mandeb están comprometidos. Añade 10–14 días y coste significativo de flete."
    },
]

df = cargar_datos()

# ─── TAB 1: MARKET DASHBOARD ─────────────────────────────
with tab1:
    st.title("🛢️ Oil Market Intelligence Dashboard")
    st.markdown("**Análisis de mercados de crudo — WTI & Brent**")
    st.markdown("---")

    if df.empty:
        st.error("No se pudieron cargar los datos.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("WTI actual",       f"${df['WTI'].iloc[-1]:.2f}",    f"{df['WTI'].iloc[-1] - df['WTI'].iloc[-2]:.2f}")
    col2.metric("Brent actual",     f"${df['Brent'].iloc[-1]:.2f}",  f"{df['Brent'].iloc[-1] - df['Brent'].iloc[-2]:.2f}")
    col3.metric("Spread WTI-Brent", f"${df['Spread'].iloc[-1]:.2f}", f"{df['Spread'].iloc[-1] - df['Spread'].iloc[-2]:.2f}")
    col4.metric("Volatilidad 4s",   f"{df['volatilidad'].iloc[-1]:.2f}%")

    st.markdown("---")
    st.subheader("📈 WTI vs Brent — Contexto geopolítico")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["period"], y=df["WTI"],   name="WTI",   line=dict(color="#E8593C", width=2)))
    fig1.add_trace(go.Scatter(x=df["period"], y=df["Brent"], name="Brent", line=dict(color="#3B8BD4", width=2)))

    for i, ev in enumerate(EVENTOS):
        fig1.add_shape(
            type="line",
            x0=ev["fecha"], x1=ev["fecha"],
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color=ev["color"], width=1.5, dash="dash")
        )
        fig1.add_annotation(
            x=ev["fecha"],
            y=0.98 - (i % 3) * 0.12,
            yref="paper",
            text=ev["label"],
            showarrow=False,
            font=dict(size=9, color=ev["color"]),
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=3,
            xanchor="left"
        )

    fig1.update_layout(height=550, template="plotly_dark", showlegend=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("🔴 **Rojo** — Escalada bélica &nbsp;&nbsp; 🔵 **Azul** — Distensión &nbsp;&nbsp; 🟡 **Amarillo** — OPEC+ &nbsp;&nbsp; 🟣 **Morado** — Política EEUU")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 Spread WTI - Brent")
        fig2 = go.Figure()
        colores_spread = ["#E8593C" if x >= 0 else "#3B8BD4" for x in df["Spread"]]
        fig2.add_trace(go.Bar(x=df["period"], y=df["Spread"], marker_color=colores_spread))
        fig2.add_hline(y=0, line_dash="dash", line_color="gray")
        fig2.update_layout(height=350, template="plotly_dark", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.subheader("📉 Volatilidad 4 semanas")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df["period"], y=df["volatilidad"], fill="tozeroy", line=dict(color="#F2A623", width=2)))
        fig3.update_layout(height=350, template="plotly_dark", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.caption("Datos: Yahoo Finance · Actualización: cada hora")

# ─── TAB 2: GEOPOLITICAL INTELLIGENCE ────────────────────
with tab2:
    st.title("🌍 Geopolitical Intelligence — Rutas del Petróleo")
    st.markdown("**Análisis de los principales cuellos de botella del suministro global de crudo**")
    st.markdown("---")

    # Mapa
    st.subheader("🗺️ Mapa de rutas críticas")
    fig_map = go.Figure()

    for e in ESTRECHOS:
        fig_map.add_trace(go.Scattergeo(
            lat=[e["lat"]], lon=[e["lon"]],
            mode="markers+text",
            marker=dict(size=e["flujo_mbd"] / 1.2, color=e["color_riesgo"], opacity=0.85),
            text=e["nombre"],
            textposition="top center",
            textfont=dict(size=11, color="white"),
            name=e["nombre"],
            hovertemplate=f"<b>{e['nombre']}</b><br>Flujo: {e['flujo_mbd']} Mb/d<br>% global: {e['pct_global']}%<br>Riesgo: {e['riesgo_label']}<extra></extra>"
        ))

    fig_map.update_layout(
        geo=dict(
            showland=True, landcolor="#1a1a2e",
            showocean=True, oceancolor="#16213e",
            showcoastlines=True, coastlinecolor="#404060",
            showcountries=True, countrycolor="#404060",
            projection_type="natural earth",
            center=dict(lat=15, lon=60),
            projection_scale=2.2
        ),
        height=500,
        paper_bgcolor="#0f0f23",
        plot_bgcolor="#0f0f23",
        font_color="white",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # Tabla de riesgo
    st.subheader("⚠️ Índice de riesgo por estrecho")
    cols = st.columns(len(ESTRECHOS))
    for i, e in enumerate(ESTRECHOS):
        with cols[i]:
            st.markdown(f"**{e['nombre']}**")
            st.markdown(f"*{e['pais']}*")
            st.metric("Flujo diario", f"{e['flujo_mbd']} Mb/d", f"{e['pct_global']}% global")
            st.markdown(f"Riesgo: :{('red' if e['riesgo'] > 70 else 'orange' if e['riesgo'] > 40 else 'green')}[**{e['riesgo_label']}** ({e['riesgo']}/100)]")

    st.markdown("---")

    # Detalle por estrecho
    st.subheader("📋 Análisis por estrecho")
    for e in ESTRECHOS:
        with st.expander(f"{e['nombre']} — {e['flujo_mbd']} Mb/d — Riesgo: {e['riesgo_label']}"):
            c1, c2 = st.columns([1, 3])
            with c1:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=e["riesgo"],
                    gauge=dict(
                        axis=dict(range=[0, 100]),
                        bar=dict(color=e["color_riesgo"]),
                        steps=[
                            dict(range=[0, 40],  color="#1a2a1a"),
                            dict(range=[40, 70], color="#2a2a1a"),
                            dict(range=[70, 100],color="#2a1a1a"),
                        ]
                    ),
                    title=dict(text="Índice de riesgo")
                ))
                fig_gauge.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=20,r=20,t=40,b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
            with c2:
                st.markdown(f"**País:** {e['pais']}")
                st.markdown(f"**Flujo diario:** {e['flujo_mbd']} millones de barriles/día")
                st.markdown(f"**% del suministro global:** {e['pct_global']}%")
                st.markdown(f"**Análisis:** {e['descripcion']}")

    st.markdown("---")
    st.caption("Fuentes: EIA, IEA, elaboración propia · Datos de riesgo: estimación cualitativa basada en eventos recientes")
