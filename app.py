import streamlit as st

st.set_page_config(
    page_title="Cocal Treinamentos",
    page_icon="🏑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Cocal Treinamentos")
st.subheader("Dashboard de Métricas de Desempenho")

st.info("📄 **Aplicação em desenvolvimento**\n\nEsta aplicação apresenta métricas de treinamentos da empresa Cocal.")

# Placeholder para gráficos
st.markdown("---")
st.write("### Próximas funcionalidades:")
st.write("- Gráficos de participação")
st.write("- Análise de treinamentos")
st.write("- Relatórios de desempenho")
