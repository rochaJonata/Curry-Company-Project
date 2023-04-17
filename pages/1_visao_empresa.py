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

st.set_page_config(page_title='Visão Empresa', page_icon=':chart_with_upwards_trend:', layout='wide')

# ====================
# Funções
# ====================
def country_maps(df):
        
    data_plot = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Gerando um mapa
    map = fl.Map()

    for index, location_info in data_plot.iterrows():
        fl.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']]).add_to( map )
    folium_static(map, width=1024, height=600)

def order_share_by_week(df):
            
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner', on='week_of_year')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # Gerando gráfico de linhas
    grafico_linha = px.line( df_aux, x='week_of_year', y='order_by_delivery')

    return grafico_linha

def order_by_week(df):
            
    # Obtendo a quantidade de pedidos por semana
    df['week_of_year'] = df['Order_Date'].dt.strftime("%U")
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    # Gerando gráfico de barras
    grafico_linha = px.line(df_aux, x='week_of_year', y='ID')

    return grafico_linha

def traffic_order_city(df):
                
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density']).count().reset_index()

    grafico_bolhas = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return grafico_bolhas

def traffic_order_share(df):
                
    # Obtendo a porcentagem de pedidos
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())

    # Gerando um gráfico de pizza
    grafico_pizza = px.pie( df_aux, values='perc_ID', names='Road_traffic_density')

    return grafico_pizza

def order_metric(df):
            
    # Obtendo a quantidade de pedidos por dia
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']

    # Gerando um gráfico de barras
    grafico_barras = px.bar(df_aux, x='order_date', y='qtde_entregas')

    return grafico_barras

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

# ==================== Visão da empresa ====================

# ====================
# Barra Lateral

st.header("Marketplace - Visão Empresa")

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        grafico_barras = order_metric(df)
        st.markdown('# Orders by Day')
        st.plotly_chart(grafico_barras, use_container_width=True)

    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:
            grafico_pizza = traffic_order_share(df)
            st.header("Traffic Order Share")
            st.plotly_chart(grafico_pizza, use_container_width=True)
            
        with col2:
            grafico_bolhas = traffic_order_city(df)
            st.header("Traffic Order City")
            st.plotly_chart(grafico_bolhas, use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown("# Order by Week")
        grafico_linha = order_by_week(df)
        st.plotly_chart(grafico_linha, use_container_width=True)

    with st.container():
        st.markdown("# Order Share by Week")
        grafico_linha = order_share_by_week(df)
        st.plotly_chart(grafico_linha, use_container_width=True)
        
with tab3:
    st.markdown("# Country Maps")
    country_maps(df)
    