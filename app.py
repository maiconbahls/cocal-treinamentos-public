# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import base64
import os
import io

# --- 1. CONFIG PAGE ---
st.set_page_config(
    page_title="Cocal Treinamentos",
    page_icon="O",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. BACKGROUND IMAGE LOGIC ---
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
    
    .cocal-green {{
    color: #9DC63A !important;
    font-weight: 800;
    }}
    
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
    
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
    background: transparent !important;
    }}
    
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stTextInput"] {{
    background: rgba(255, 255, 255, 0.05) !important;
    }}
    
    input, select, textarea {{
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(157, 198, 58, 0.3) !important;
    color: #ffffff !important;
    }}
    
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

# Apply styles
apply_styles('fundo.png')

# --- 3. TITLE ---
st.markdown('<h1><span class="cocal-green">Cocal</span> Treinamentos</h1>', unsafe_allow_html=True)
st.markdown('---')

# --- 4. LOAD DATA FROM UPLOADED FILES ---
@st.cache_data
def load_data_from_folder():
    """Carrega o primeiro arquivo Excel encontrado na pasta"""
    try:
        # Procurar por arquivos Excel na pasta atual
        import glob
        xls_files = glob.glob('*.xls') + glob.glob('*.xlsx')
        
        if xls_files:
            # Usar o primeiro arquivo encontrado
            arquivo = xls_files[0]
            data = pd.read_excel(arquivo, sheet_name=0)
            return data, arquivo
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
    
    return None, None

# Tentar carregar dados
data, arquivo_carregado = load_data_from_folder()

if data is not None and len(data) > 0:
    st.markdown('<h2>Dashboard de Treinamentos</h2>', unsafe_allow_html=True)
    
    try:
        data_clean = data.copy()
        
        # Remove colunas duplicadas
        data_clean = data_clean.loc[:, ~data_clean.columns.duplicated()]
        
        # Rename columns if needed
        col_mapping = {}
        for col in data_clean.columns:
            col_lower = col.lower().strip()
            if 'data' in col_lower:
                col_mapping[col] = 'Data'
            elif 'instrutor' in col_lower or 'efetuado' in col_lower:
                col_mapping[col] = 'Instrutor'
            elif 'evento' in col_lower or 'treinamento' in col_lower:
                col_mapping[col] = 'Evento'
            elif 'participante' in col_lower:
                col_mapping[col] = 'Participantes'
            elif 'efaz' in col_lower or 'efetuado' in col_lower:
                col_mapping[col] = 'Efaz'
        
        data_clean = data_clean.rename(columns=col_mapping)
        
        # METRICS
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Treinamentos", len(data_clean))
        with col2:
            total_part = 0
            for col in ['Participantes', 'participante']:
                if col in data_clean.columns:
                    try:
                        total_part = int(data_clean[col].sum())
                        break
                    except:
                        pass
            st.metric("Total de Participantes", total_part)
        with col3:
            total_inst = 0
            if 'Instrutor' in data_clean.columns:
                total_inst = data_clean['Instrutor'].nunique()
            st.metric("Total de Instrutores", total_inst)
        with col4:
            total_efaz = 0
            if 'Efaz' in data_clean.columns:
                try:
                    total_efaz = int(data_clean['Efaz'].sum())
                except:
                    total_efaz = 0
            st.metric("Efaz Finalizado", total_efaz)
        
        st.markdown('---')
        
        # CHARTS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Treinamentos por Instrutor')
            if 'Instrutor' in data_clean.columns:
                instrutores = data_clean['Instrutor'].value_counts().reset_index()
                instrutores.columns = ['Instrutor', 'Count']
                fig_instrutor = px.bar(
                    instrutores,
                    x='Instrutor',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Greens'
                )
                fig_instrutor.update_layout(showlegend=False, template="plotly_dark")
                st.plotly_chart(fig_instrutor, use_container_width=True)
        
        with col2:
            st.markdown('#### Participantes por Evento')
            if 'Evento' in data_clean.columns:
                eventos = data_clean.groupby('Evento')['Participantes'].sum().reset_index() if 'Participantes' in data_clean.columns else data_clean.groupby('Evento').size().reset_index(name='Participantes')
                fig_evento = px.pie(
                    eventos,
                    values='Participantes',
                    names='Evento',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_evento.update_layout(template="plotly_dark")
                st.plotly_chart(fig_evento, use_container_width=True)
        
        st.markdown('---')
        
        # DATA TABLE
        st.markdown('#### Detalhes de Treinamentos')
        st.dataframe(data_clean, use_container_width=True, height=400)
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")
        st.dataframe(data, use_container_width=True)
else:
    st.info("Nenhum arquivo Excel encontrado. Faça upload de um arquivo para visualizar o dashboard.")
    
    # Upload fallback
    st.markdown('<h2>Atualizar Base</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Selecione um arquivo Excel",
        type=['xls', 'xlsx'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.rerun()
