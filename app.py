import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import base64
import os
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Cocal Treinamentos",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LÓGICA DE IMAGEM DE FUNDO ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def apply_styles(file_path):
    bg_style = ""
    if os.path.exists(file_path):
        img_base64 = get_base64(file_path)
        bg_style = f"""
        background-image: linear-gradient(rgba(10, 14, 18, 0.8), rgba(10, 14, 18, 0.8)), url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-attachment: fixed;
        """
    else:
        bg_style = "background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%);"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp {{
    {bg_style}
    }}
    
    h1, h2, h3, h4, h5, p, label {{
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    }}
    
    /* DESTAQUE VERDE COCAL */
    .cocal-green {{
    color: #9DC63A !important;
    font-weight: 800;
    }}
    /* --- CARDS DE MÉTRICAS --- */
    [data-testid="stMetric"] {{
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(157, 198, 58, 0.4) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }}
    [data-testid="stMetricValue"] {{ 
    color: #9DC63A !important; 
    font-weight: 700 !important; 
    }}
    /* --- TABELA TOTALMENTE TRANSPARENTE (GLASSMORPHISM) --- */
    [data-testid="stDataFrame"], 
    [data-testid="stDataFrame"] > div,
    [data-testid="stTable"],
    [data-testid="stTable"] > div {{
    background: transparent !important;
    }}
    /* --- CONTAINER PARA TABELA --- */
    .transparent-container {{
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(157, 198, 58, 0.2) !important;
    border-radius: 8px !important;
    padding: 15px !important;
    }}
    /* --- FILTROS DO STREAMLIT --- */
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stTextInput"],
    [data-testid="stNumberInput"],
    [data-testid="stDateInput"] {{
    background: rgba(255, 255, 255, 0.05) !important;
    }}
    input, select, textarea {{
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(157, 198, 58, 0.3) !important;
    color: #ffffff !important;
    }}
    /* --- BOTÕES --- */
    button {{
    background-color: #9DC63A !important;
    color: #0f1419 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    }}
    button:hover {{
    background-color: #b5d855 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Aplicar estilos
apply_styles('fundo.png')

# --- 3. TÍTULO DA PÁGINA ---
st.markdown('<h1><span class="cocal-green">Cocal</span> Treinamentos</h1>', unsafe_allow_html=True)
st.markdown('---')

# --- 4. SEÇÃO DE UPLOAD ---
st.markdown('<h2>⚙️ Atualizar Base</h2>', unsafe_allow_html=True)
st.markdown('Upload de nova base (Excel):')

uploaded_file = st.file_uploader(
    "Drag and drop file here",
    type=['xls', 'xlsx'],
    label_visibility="collapsed"
)

data = None

if uploaded_file is not None:
    try:
        # Ler o arquivo enviado
        data = pd.read_excel(uploaded_file, sheet_name=0)
        st.success("Board atualizado!")
        st.info(f"Registros carregados: {len(data)}")
        
        if st.button("Aplicar Agora", key="apply_button"):
            st.session_state['data_loaded'] = True
            st.session_state['dataframe'] = data
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        data = None

# Usar dados da sessão se disponível
if 'dataframe' in st.session_state and st.session_state.get('data_loaded'):
    data = st.session_state['dataframe']

if data is not None and len(data) > 0:
    st.markdown('---')
    st.markdown('<h2>📊 Dashboard de Treinamentos</h2>', unsafe_allow_html=True)
    
    # Preparar dados
    try:
        # Garantir que as colunas existem
        required_cols = ['Data', 'Instrutor', 'Evento', 'Participantes', 'Éfaz']
        data_clean = data.copy()
        
        # Renomear colunas se necessário
        col_mapping = {}
        for col in data_clean.columns:
            col_lower = col.lower().strip()
            if 'data' in col_lower:
                col_mapping[col] = 'Data'
            elif 'instrutor' in col_lower:
                col_mapping[col] = 'Instrutor'
            elif 'evento' in col_lower or 'treinamento' in col_lower:
                col_mapping[col] = 'Evento'
            elif 'participante' in col_lower:
                col_mapping[col] = 'Participantes'
            elif 'éfaz' in col_lower or 'efaz' in col_lower:
                col_mapping[col] = 'Éfaz'
        
        data_clean = data_clean.rename(columns=col_mapping)
        
        # MÉTRICAS
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Treinamentos", len(data_clean))
        with col2:
            st.metric("Total de Participantes", int(data_clean['Participantes'].sum()) if 'Participantes' in data_clean.columns else 0)
        with col3:
            st.metric("Total de Instrutores", data_clean['Instrutor'].nunique() if 'Instrutor' in data_clean.columns else 0)
        with col4:
            st.metric("Éfaz Finalizado", int(data_clean['Éfaz'].sum()) if 'Éfaz' in data_clean.columns else 0)
        
        st.markdown('---')
        
        # GRÁFICOS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Treinamentos por Instrutor')
            if 'Instrutor' in data_clean.columns:
                fig_instrutor = px.bar(
                    data_clean.groupby('Instrutor').size().reset_index(name='Count'),
                    x='Instrutor',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Greens'
                )
                fig_instrutor.update_layout(showlegend=False, template="plotly_dark")
                st.plotly_chart(fig_instrutor, use_container_width=True)
        
        with col2:
            st.markdown('#### Participantes por Evento')
            if 'Evento' in data_clean.columns and 'Participantes' in data_clean.columns:
                fig_evento = px.pie(
                    data_clean.groupby('Evento')['Participantes'].sum().reset_index(),
                    values='Participantes',
                    names='Evento',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_evento.update_layout(template="plotly_dark")
                st.plotly_chart(fig_evento, use_container_width=True)
        
        st.markdown('---')
        
        # TABELA TRANSPARENTE
        st.markdown('#### Detalhes de Treinamentos')
        st.dataframe(data_clean, use_container_width=True, height=400)
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")
        st.dataframe(data, use_container_width=True)
else:
    st.info("\ud83d\udcc4 Carregue um arquivo Excel para visualizar o dashboard")
