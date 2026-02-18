# ============================================================
# 📊 DATYX DASHBOARD PROFESIONAL
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from openai import OpenAI

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Datyx Dashboard",
    layout="wide"
)

st.title("📊 Datyx Dashboard")
st.subheader("Análisis Inteligente de Museos de México")

# ============================================================
# CLIENTE OPENAI
# ============================================================

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ============================================================
# CARGAR DATA
# ============================================================

df = pd.read_csv("museos_clusterizados.csv")

df = df.rename(columns={
    "recinto": "Museo",
    "promedio_anual": "Visitantes anuales",
    "desviacion_anual": "Variabilidad anual",
    "volatilidad_promedio": "Volatilidad",
    "share_estatal_promedio": "Participación estatal",
    "porcentaje_extranjeros": "Visitantes extranjeros (%)",
    "cluster": "Cluster"
})

# ============================================================
# MENÚ
# ============================================================

st.sidebar.title("Menú")
opcion = st.sidebar.selectbox(
    "Selecciona sección",
    [
        "Base de datos",
        "Visualización de Clusters",
        "Análisis individual"
    ]
)

# ============================================================
# BASE DE DATOS
# ============================================================

if opcion == "Base de datos":
    st.subheader("📂 Base de datos")
    st.dataframe(
        df[["Museo", "Visitantes anuales", "Visitantes extranjeros (%)"]],
        use_container_width=True
    )

# ============================================================
# VISUALIZACIÓN CLUSTERS
# ============================================================

elif opcion == "Visualización de Clusters":
    st.subheader("📊 Análisis estratégico de clusters")

    total_museos = len(df)
    visitantes_totales = df["Visitantes anuales"].sum()
    visitantes_promedio = df["Visitantes anuales"].mean()
    cluster_dominante = df["Cluster"].value_counts().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total museos", total_museos)
    col2.metric("Visitantes totales", f"{visitantes_totales:,.0f}")
    col3.metric("Promedio por museo", f"{visitantes_promedio:,.0f}")
    col4.metric("Cluster dominante", cluster_dominante)

    st.markdown("---")

    # MAPA
    st.subheader("🧭 Mapa estratégico")
    fig, ax = plt.subplots()
    scatter = ax.scatter(df["PC1"], df["PC2"], c=df["Cluster"], s=80)
    legend = ax.legend(*scatter.legend_elements(), title="Cluster")
    ax.add_artist(legend)
    st.pyplot(fig)

    # PERFIL
    st.subheader("🧠 Perfil promedio")
    columnas_cluster = [
        "Visitantes anuales",
        "Variabilidad anual",
        "Volatilidad",
        "Participación estatal",
        "Visitantes extranjeros (%)"
    ]
    resumen = df.groupby("Cluster")[columnas_cluster].mean()
    st.dataframe(resumen)

    # INTERPRETACIÓN IA
    contenedor = st.container()
    if "interpretacion_clusters" not in st.session_state:
        st.session_state["interpretacion_clusters"] = ""

    if st.button("Generar interpretación de clusters"):
        prompt = f"""
        Analiza estos clusters:
        {resumen}
        Explica cada cluster y da recomendaciones.
        Máximo 120 palabras.
        """
        with st.spinner("Analizando..."):
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state["interpretacion_clusters"] = response.choices[0].message.content

    with contenedor:
        if st.session_state["interpretacion_clusters"] != "":
            st.success("Interpretación generada")
            st.info(st.session_state["interpretacion_clusters"])

# ============================================================
# ANÁLISIS INDIVIDUAL
# ============================================================

elif opcion == "Análisis individual":
    st.subheader("🔎 Análisis de museo")

    museo = st.selectbox("Selecciona un museo", df["Museo"])
    museo_data = df[df["Museo"] == museo].iloc[0]

    visitantes = museo_data["Visitantes anuales"]
    visitantes_dia = visitantes / 365
    extranjeros = museo_data["Visitantes extranjeros (%)"] * 100
    cluster = museo_data["Cluster"]

    if cluster == 0:
        nivel = "Alta afluencia"
    elif cluster == 1:
        nivel = "Baja afluencia"
    else:
        nivel = "Afluencia media"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Visitantes anuales", f"{visitantes:,.0f}")
    col2.metric("Visitantes diarios", f"{visitantes_dia:.1f}")
    col3.metric("% extranjeros", f"{extranjeros:.2f}%")
    col4.metric("Nivel", nivel)

    # MAPA
    st.subheader("📊 Posición")
    fig, ax = plt.subplots()
    ax.scatter(df["PC1"], df["PC2"], alpha=0.3)
    ax.scatter(museo_data["PC1"], museo_data["PC2"], s=200, color="red")
    st.pyplot(fig)

    # INTERPRETACIÓN IA
    st.subheader("🧠 Interpretación con IA")
    contenedor = st.container()

    if "interpretacion_museo" not in st.session_state:
        st.session_state["interpretacion_museo"] = ""
    if "museo_actual" not in st.session_state:
        st.session_state["museo_actual"] = museo

    # Detectar cambio de museo
    if museo != st.session_state["museo_actual"]:
        st.session_state["interpretacion_museo"] = ""
        st.session_state["museo_actual"] = museo

    texto_boton = (
        "Generar interpretación"
        if st.session_state["interpretacion_museo"] == ""
        else "Actualizar interpretación"
    )

    if st.button(texto_boton):
        prompt = f"""
        Analiza este museo:
        {museo}
        Visitantes: {visitantes}
        Extranjeros: {extranjeros:.2f}%
        Cluster: {cluster}
        Da recomendaciones.
        Máximo 150 palabras.
        """
        with st.spinner("Analizando..."):
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state["interpretacion_museo"] = response.choices[0].message.content

    with contenedor:
        if st.session_state["interpretacion_museo"] == "":
            st.info("Presiona el botón para generar la interpretación")
        else:
            st.success("Interpretación generada")
            st.markdown(f"### 📍 {museo}\n{st.session_state['interpretacion_museo']}")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("© 2026 Datyx")
