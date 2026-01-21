import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import base64
import os

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
            background-image: linear-gradient(rgba(10, 14, 18, 0.8), rgba(10, 14, 18, 0.8)), 
            url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-attachment: fixed;
        """
    else:
        bg_style = "background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%);"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        .stApp {{ {bg_style} }}
        
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
        [data-testid="stTable"] {{
            background-color: transparent !important;
        }}

        [data-testid="stDataFrame"] [role="gridcell"] {{
            background-color: rgba(255, 255, 255, 0.01) !important;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
        }}

        [data-testid="stDataFrame"] [role="columnheader"] {{
            background-color: rgba(157, 198, 58, 0.2) !important;
            color: #9DC63A !important;
            font-weight: 700 !important;
            border-bottom: 2px solid rgba(157, 198, 58, 0.5) !important;
        }}

        /* --- INPUTS E CALENDÁRIO --- */
        div[data-testid="stDateInput"] input {{
            color: #ffffff !important;
            background-color: rgba(45, 55, 72, 0.9) !important;
            border: 1px solid #9DC63A !important;
            border-radius: 8px !important;
        }}
        
        .stSelectbox div[data-baseweb="select"], .stTextInput input {{
            background-color: rgba(45, 55, 72, 0.9) !important;
            color: white !important;
            border: 1px solid rgba(157, 198, 58, 0.4) !important;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, #9DC63A, #7fb52a) !important;
            color: #0f1419 !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            height: 3rem;
            width: 100%;
            border: none !important;
        }}
        /* ESCONDER HEADER E MENU */
        [data-testid="stHeader"] {{
            display: none !important;
        }}
        footer {{
            display: none !important;
        }}
        #MainMenu {{
            visibility: hidden;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_styles('Fundo.png')

# --- 3. CARREGAMENTO DE DADOS ---
@st.cache_data(show_spinner="Carregando base de dados...")
def load_data(file_source):
    if not file_source: return None
    try:
        df = pd.read_excel(file_source)
        df.columns = [c.strip() for c in df.columns]
        
        # Colunas obrigatórias para o dashboard funcionar
        cols_obrigatorias = ['Evento', 'Efetuado por', 'Pessoa', 'Matrícula']
        faltando = [c for c in cols_obrigatorias if c not in df.columns]
        
        if faltando:
            st.warning(f"⚠️ Atenção: As colunas {faltando} não foram encontradas no Excel. Verifique o arquivo.")
            return None

        if 'Data e hora' in df.columns:
            df['Data e hora'] = pd.to_datetime(df['Data e hora'], format='%d/%m/%Y - %H:%M', errors='coerce')
            df['Data'] = df['Data e hora'].dt.date
            df['Hora'] = df['Data e hora'].dt.strftime('%H:%M')
        else:
            st.warning("⚠️ Coluna 'Data e hora' não encontrada. Filtros de data podem não funcionar.")
            df['Data'] = pd.to_datetime('today').date()
            df['Hora'] = '--:--'
            
        return df
    except Exception as e:
        st.error(f"Erro técnico ao ler o Excel: {e}")
        return None

# Busca automática: pega QUALQUER arquivo .xls ou .xlsx, priorizando o mais recente
if 'data_base' not in st.session_state:
    arquivos_excel = [f for f in os.listdir('.') if f.lower().endswith(('.xls', '.xlsx'))]
    if arquivos_excel:
        # Ordena pelos arquivos mais recentes (data de modificação)
        arquivos_excel.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        st.session_state.data_base = load_data(arquivos_excel[0])
    else:
        st.session_state.data_base = None

# --- 4. TÍTULO ATUALIZADO ---
st.markdown('<h1><span class="cocal-green">Cocal</span> Treinamentos</h1>', unsafe_allow_html=True)

if st.session_state.data_base is not None:
    df = st.session_state.data_base
    hoje = datetime.now().date()

    # --- 5. FILTROS ---
    with st.container():
        col_btn, col_date, col_evento, col_inst, col_busca = st.columns([1, 2, 2, 2, 2])
        
        with col_btn:
            st.write("")
            st.write("")
            if st.button("Filtrar Hoje"):
                st.session_state.data_filtro = (hoje, hoje)
                st.rerun()

        with col_date:
            default_range = (df['Data'].min(), df['Data'].max())
            data_range = st.date_input("Período:", 
                                     value=st.session_state.get('data_filtro', default_range),
                                     format="DD/MM/YYYY") 
            
        with col_evento:
            sel_evento = st.selectbox("Evento:", ['Todos'] + sorted(df['Evento'].dropna().unique().tolist()))
            
        with col_inst:
            sel_inst = st.selectbox("Instrutor:", ['Todos'] + sorted(df['Efetuado por'].dropna().unique().tolist()))
            
        with col_busca:
            busca = st.text_input("🔎 Matrícula do Participante:")

    # Filtragem
    df_f = df.copy()
    if isinstance(data_range, tuple) and len(data_range) == 2:
        df_f = df_f[(df_f['Data'] >= data_range[0]) & (df_f['Data'] <= data_range[1])]
    if sel_evento != 'Todos': df_f = df_f[df_f['Evento'] == sel_evento]
    if sel_inst != 'Todos': df_f = df_f[df_f['Efetuado por'] == sel_inst]
    if busca:
        df_f = df_f[df_f['Pessoa'].str.contains(busca, case=False, na=False) | 
                    df_f['Matrícula'].astype(str).str.contains(busca, na=False)]

    # --- 6. MÉTRICAS ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Participações", len(df_f))
    c2.metric("Colaboradores Únicos", df_f['Pessoa'].nunique())
    c3.metric("Instrutores Ativos", df_f['Efetuado por'].nunique())

    st.markdown("---")

    # --- 7. GRÁFICOS ---
    g1, g2 = st.columns(2)
    with g1:
        st.markdown('<h4>Distribuição de Treinamentos</h4>', unsafe_allow_html=True)
        evt_count = df_f['Evento'].value_counts().reset_index().head(10)
        fig_evt = px.bar(evt_count, x='count', y='Evento', orientation='h',
                         color='count', color_continuous_scale='Greens', 
                         template='plotly_dark', text_auto=True)
        fig_evt.update_traces(textfont_size=12, textfont_color="white", textposition="outside")
        fig_evt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font=dict(color="white"), bargap=0.4, height=400)
        st.plotly_chart(fig_evt, use_container_width=True)

    with g2:
        st.markdown('<h4>Participantes por Instrutor</h4>', unsafe_allow_html=True)
        inst_count = df_f['Efetuado por'].value_counts().reset_index().head(10)
        fig_inst = px.bar(inst_count, x='count', y='Efetuado por', orientation='h',
                          color='count', color_continuous_scale='Greens', 
                          template='plotly_dark', text_auto=True)
        fig_inst.update_traces(textfont_size=12, textfont_color="white", textposition="outside")
        fig_inst.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                               font=dict(color="white"), bargap=0.4, height=400)
        st.plotly_chart(fig_inst, use_container_width=True)

    # --- 8. TABELA TRANSPARENTE ---
    st.markdown('<h4>Board de Participantes</h4>', unsafe_allow_html=True)
    
    st.dataframe(
        df_f[['Matrícula', 'Pessoa', 'Evento', 'Efetuado por', 'Data', 'Hora']].sort_values(['Data', 'Hora'], ascending=False),
        use_container_width=True, 
        height=800, 
        hide_index=True,
        column_config={
            "Matrícula": st.column_config.TextColumn("Matrícula do Participante", width="medium"),
            "Pessoa": st.column_config.TextColumn("Colaborador", width="large"),
            "Evento": st.column_config.TextColumn("Treinamento", width="large"),
            "Efetuado por": st.column_config.TextColumn("Instrutor", width="medium"),
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Hora": st.column_config.TextColumn("Horário", width="small")
        }
    )

# --- 9. GESTÃO DA BASE ---
st.divider()
st.markdown('### ⚙️ Atualizar Base')
new_file = st.file_uploader("Upload de nova base (Excel):", type=['xls', 'xlsx'])
if new_file:
    st.session_state.data_base = load_data(new_file)
    st.success("Board atualizado!")
    if st.button("Aplicar Agora"):
        st.rerun()