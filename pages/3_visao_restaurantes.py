# ==========================
# Importando as bibliotecas

import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

#Para desenhar gráficos
import plotly.express as px
import plotly.graph_objects as go

#Para desenhar um mapa
import folium as fl

from haversine import haversine

st.set_page_config(page_title='Visão Restaurantes', page_icon=':fork_and_knife:', layout='wide')

# ====================
# Funções
# ====================
def avg_std_time_on_traffic(df):
            
    df_selecionado = df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    df_selecionado.columns = ['avg_time', 'std_time']
    df_selecionado = df_selecionado.reset_index()

    fig = px.sunburst(df_selecionado, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_selecionado['std_time']))

    return fig

def avg_std_time_graph(df):

    df_selecionado = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_selecionado.columns = ['avg_time', 'std_time']
    df_selecionado = df_selecionado.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_selecionado['City'], y=df_selecionado['avg_time'], error_y=dict(type='data', array=df_selecionado['std_time'])))
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery(df, festival, op):
            
    df_selecionado = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
    df_selecionado.columns = ['avg_time', 'std_time']
    df_selecionado = df_selecionado.reset_index()
    df_selecionado = np.round(df_selecionado.loc[df_selecionado['Festival'] == festival, op], 2)

    return df_selecionado

def distance(df, figura):
    df['Distance'] = df.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
    
    if figura == False:
        
        avg_distance = np.round(df['Distance'].mean(), 2)
        return avg_distance
    else:
        avg_distance = df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0])])
        return fig

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

# ==================== Visão dos Restaurantes ====================

# ====================
# Barra Lateral

st.header("Marketplace - Visão Restaurantes")

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
    # 1 container
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
            
        with col2:
            avg_distance = distance(df, False)
            col2.metric('A distancia media das entregas', avg_distance)
            
        with col3:
            df_selecionado = avg_std_time_delivery(df, 'Yes', 'avg_time')
            col3.metric('Tempo Médio de Entrega c/ Festival', df_selecionado)
            
        with col4:
            df_selecionado = avg_std_time_delivery(df, 'Yes', 'std_time')
            col4.metric('Desvio Padrão de Entrega c/ Festival', df_selecionado)
            
        with col5:
            df_selecionado = avg_std_time_delivery(df, 'No', 'avg_time')
            col5.metric('Tempo Médio de Entrega c/ Festival', df_selecionado)
            
        with col6:
            df_selecionado = avg_std_time_delivery(df, 'No', 'std_time')
            col6.metric('Desvio Padrão de Entrega c/ Festival', df_selecionado)
    
    # 2 container
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig)
        
        with col2:

            df_selecionado = df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
            df_selecionado.columns = ['avg_time', 'std_time']
            df_selecionado = df_selecionado.reset_index()

            st.dataframe(df_selecionado)
    
    # 3 container
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df, True)
            st.plotly_chart(fig)

        with col2:
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)
    