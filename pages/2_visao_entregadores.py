# ==========================
# Importando as bibliotecas

import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

#Para desenhar gráficos
import plotly.express as px
import plotly.graph_objects as go

#Para desenhar um mapa
import folium as fl

from haversine import haversine

st.set_page_config(page_title='Visão Entregadores', page_icon=':bicyclist:', layout='wide')

# ====================
# Funções
# ====================
def top_delivers(df, top_asc):
                
    df_selecionado = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_aux1 = df_selecionado.loc[df_selecionado['City'] == 'Metropolitia', :].head(10)
    df_aux2 = df_selecionado.loc[df_selecionado['City'] == 'Urba', :].head(10)
    df_aux3 = df_selecionado.loc[df_selecionado['City'] == 'Semi-Urba', :].head(10)

    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)

    return df3

def clean_code(df):
    
    """ Esta função tem a responsabilidade de limpar o dataframe 
        
        Tipos de limpeza:
        1. Remover os espaços das string
        2. Excluir as linhas vazias
        3. Conversões de tipos dados
        4. Redefinir o índice do DataFrame
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # 1. Remover os espaços das string
    colunas = ['ID', 'Delivery_person_ID', 'Delivery_person_Age', 'Delivery_person_Ratings', 'Order_Date', 'Time_Orderd', 'Time_Order_picked', 'Weatherconditions', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'multiple_deliveries', 'Festival', 'City', 'Time_taken(min)']

    for coluna in colunas:
      df.loc[:, coluna] = df.loc[:, coluna].str.strip("(min) ")

    # 2. Excluir as linhas vazias
    for colum in colunas:
      df = df.loc[df[colum] != 'NaN', :]

    # 3. Conversões de tipos dados
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    df['Vehicle_condition'] = df['Vehicle_condition'].astype(int)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # 4. Redefinir o índice do DataFrame
    df = df.reset_index(drop=True)
    
    return df

# --------------------- Inicio da Estrutura logica do código --------

# ====================
# Carregando o dataset
# ====================

#Importando o arquivo
df_orig = pd.read_csv('dataset/train.csv')

# ==================
# Limpando os dados
# ====================

df = clean_code(df_orig)

# ==================== Visão de Entregadores ====================

# ====================
# Barra Lateral

st.header("Marketplace - Visão Entregadores")

# image_path = 'C:/Users/atano/ComunidadeDS/repos/ftc_programacao_python/Ciclo_06-Visualizacao_interativa/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data limite")

date_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022, 4, 13), min_value=pd.datetime(2022, 2, 11), max_value=pd.datetime(2022, 4, 6), format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Comunidade DS")

#Filtro de data
df = df.loc[df['Order_Date'] < date_slider, :]

#Filtro de transito
df = df.loc[df['Road_traffic_density'].isin(traffic_options), :]

# ==========================
# Layout no Streamlit

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadores
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            #A melhor condicao de vaiculos
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_condicao)
            
        with col4:
            #A pior condicao de vaiculos
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condicao', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacao medias por entregador')
            df_avg_ratings_per_deliver = df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
            
        with col2:
            st.markdown('##### Avaliacao media por transito')
            df_selecionado = df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']})

            #Mudança de nome das colunas
            df_selecionado.columns = ['Delivery_mean', 'Delivery_std']
            df_selecionado = df_selecionado.reset_index()
            st.dataframe(df_selecionado)
            
            st.markdown('##### Avaliacao media por clima')
            df_selecionado = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})

            #Mudança de nome das colunas
            df_selecionado.columns = ['Delivery_mean', 'Delivery_std']
            df_selecionado = df_selecionado.reset_index()
            st.dataframe(df_selecionado)
        
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            df3 = top_delivers(df, top_asc=True)           
            st.dataframe(df3)
        
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df, top_asc=False)
            st.dataframe(df3)