#=============================================
#=============================================
#=====================INÍCIO==================
#=============================================
#=============================================
#
#
#=============================================
#--------Importando as bibliotecas
#=============================================
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine, Unit
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão restaurantes', layout = 'wide', page_icon = '🍲')

#=============================================
#--------Importando os dados
#=============================================
df = pd.read_csv('train.csv')
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )



#################################################################################################
#                                   DEFININDO AS FUNÇÕES
#################################################################################################

########## Função para limpeza dos dados ############
def clean_data(df):
    """Esta função tem a responsabilidade de limpar o dataframe.
    Tipos de limpeza realizadas:
        1) Remove as linhas que contém NaN
        2) Transforme os valores integrais e floats corretamente
        3) Remove os espaços extras nas entradas
        4) Remove outros termos desnecessários às entradas

    Args:
        Um dataframe contendo variáveis sobre as entregas nas colunas e entradas de entregas nas linhas

    Returns:
        Um dataframe contendo variáveis sobre as entregas nas colunas e entradas de entregas nas linhas limpo e pronto para ser analisado
    """
    data = df.loc[df['Delivery_person_Age'] !='NaN ', :] #Removendo linhas com NaN na coluna Delivery_person_Age
    data = data.loc[data['City'] !='NaN ', :] #Removendo linhas com NaN na coluna City
    data = data.loc[data['Festival'] !='NaN ', :] #Removendo linhas com NaN na coluna Festival
    data = data.loc[data['Road_traffic_density']!='NaN ', :] #Removendo linhas com NaN na coluna Road_traffic_density
    data = data.loc[data['Delivery_person_Ratings']!='NaN ', :] #Removendo linhas com NaN na coluna Delivery_person_Ratings
    data = data.loc[data['Weatherconditions']!='NaN ', :] #Removendo linhas com NaN na coluna Weaatherconditions
    data = data.loc[data['multiple_deliveries'] != 'NaN ', :] #Removendo linhas com NaN na coluna multiple_deliveries

    data[['Delivery_person_Age', 'multiple_deliveries']] = data[['Delivery_person_Age', 'multiple_deliveries']].astype(int) #Convertendo variáveis numéricas de str para int

    data['Delivery_person_Ratings'] = data['Delivery_person_Ratings'].astype( float ) #Convertendo str para float
    data = data.reset_index(drop=True) #Resetando os indexes das linhas

    data.loc[:, 'ID'] = data.loc[:, 'ID'].str.strip()
    data.loc[:, 'Type_of_order'] = data.loc[:, 'Type_of_order'].str.strip()
    data.loc[:, 'Type_of_vehicle'] = data.loc[:, 'Type_of_vehicle'].str.strip()
    data.loc[:, 'City'] = data.loc[:, 'City'].str.strip()
    data.loc[:, 'Road_traffic_density'] = data.loc[:, 'Road_traffic_density'].str.strip()
    data.loc[:, 'Festival'] = data.loc[:, 'Festival'].str.strip()

    data.loc[:, 'Weatherconditions'] = data.loc[:, 'Weatherconditions'].str.replace('conditions ', '')

    data['Time_taken(min)'] = data['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    data['Time_taken(min)'] = data['Time_taken(min)'].astype(int)

    data['distances'] = (data.loc[:, ['Restaurant_latitude',  'Restaurant_longitude',  'Delivery_location_latitude', 'Delivery_location_longitude']]
                         .apply(lambda x: haversine((x['Restaurant_latitude'], 
                                                     x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], 
                                                     x['Delivery_location_longitude'])), axis=1))

    df1 = data.copy() #Backup do dataframe
    
    return data

########## Função para plotar pizza com distancia media por cidade ############
def dist_media_city(data):
    """Plota a distancia media percorrida em cada cidade

    Args:
        data

    Returns:
        grafico de pizza
    """    
    avg_distances = data.loc[:, ['City', 'distances']].groupby('City').mean().reset_index()
    fig = go.Figure(data = [go.Pie(labels = avg_distances['City'], values = avg_distances['distances'], pull=[0, 0.1, 0])])
    return fig


########## Função para plotar barras tempo medio por cidade ############
def tmedio_cidade(data):
    """Plota um grafico de barras com o tempo médio por cidade

    Args:
        data

    Returns:
        grafico de barras
    """    
    df_aux = data[['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['time_taken_mean', 'time_taken_std']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar( name='Control', x = df_aux['City'], 
                            y = df_aux['time_taken_mean'], 
                            error_y =  dict(type = 'data', array = df_aux['time_taken_std'])))
    return fig


########## Função para plotar tempo médio por tipo de pedido ############
def tmedio_tipo_pedido(data):
    """_summary_

    Args:
        data

    Returns:sunburst
        
    """    
    df_aux = data[['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['time_taken_mean', 'time_taken_std']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path = ['City', 'Type_of_order'], values = 'time_taken_mean',
            color = 'time_taken_std', color_continuous_scale = 'RdBu',
            color_continuous_midpoint = np.average(df_aux['time_taken_std']))
    return fig


########## Função para plotar sunburst tempo medio por cidade e trafego############
def tmedio_cidade_trafego(data):
    """Plota um sunburst com o tempo médio das entregas por cidade e por trafego

    Args:
        data

    Returns:
        sunburst
    """    
    df_aux = data[['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['time_taken_mean', 'time_taken_std']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'time_taken_mean',
        color = 'time_taken_std', color_continuous_scale = 'RdBu',
        color_continuous_midpoint = np.average(df_aux['time_taken_std']))
    return fig


#################################################################################################
#                                   INÍCIO DAS ANÁLISES
#################################################################################################

#=============================================
#--------Limpando os dados
#=============================================
data = clean_data(df)


#=============================================
#Layout da barra lateral
#=============================================
#image_path = Image.open('/home/piatobruno/repos/FTC_Python/imgs/curry_delivery.png')
st.sidebar.image('curry_delivery.png', width=60)

st.sidebar.markdown('# Curry company')
st.sidebar.markdown('##### *Fastest curry in town*')
st.sidebar.markdown("""---""")

#Definição dos botões
st.sidebar.markdown('## Selecione os parâmetros')
data_slider = st.sidebar.slider('Até qual data?',
                  value=pd.datetime(2022, 4, 6),
                  min_value=pd.datetime(2022, 2, 11),
                  max_value=pd.datetime(2022, 4, 6),
                  format='DD-MM-YYYY')

traffic_options = st.sidebar.multiselect(label='Em quais condições de tráfego:', 
                       options=['High', 'Jam', 'Low', 'Medium'],
                        default=['High', 'Jam', 'Low', 'Medium'])

weather_options = st.sidebar.multiselect(label='Em quais condições climáticas:', 
                       options=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'],
                                        default=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'])

st.sidebar.markdown('##### Powered by ComunidadeDS')

#Vinculando os widgets
linhas_selecionadas = data['Order_Date'] < data_slider
data = data.loc[linhas_selecionadas, :]

linhas_selecionadas = data['Road_traffic_density'].isin(traffic_options)
data = data.loc[linhas_selecionadas, :]

linhas_selecionadas = data['Weatherconditions'].isin(weather_options)
data = data.loc[linhas_selecionadas, :]

#=============================================
#Layout do projeto
#=============================================

st.header('Curry Company - Visão dos restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'x', 'x'])

with tab1:
    
    with st.container():
        st.title('Métricas dos restaurantes')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            entregadores_unicos = len(data['Delivery_person_ID'].unique())
            col1.metric('Número de Entregadores', entregadores_unicos)
            
        with col2:
            df1 = data.copy()
            dist_media = round(data['distances'].mean(), 2)
            col2.metric('Distância média', dist_media)
            
        with col3:
            col3.metric('Tempo de entrega - Festival', round(data[data['Festival']=='Yes']['Time_taken(min)'].mean(), 2))
            
        with col4:
            col4.metric('Std - Festival', round(data[data['Festival']=='Yes']['Time_taken(min)'].std(), 2))
            
        with col5:
            col5.metric('Tempo de entrega - s/ Festival', round(data[data['Festival']=='No']['Time_taken(min)'].mean(), 2))
            
        with col6:
            col6.metric('Std - s/ Festival', round(data[data['Festival']=='No']['Time_taken(min)'].std(), 2))
        
    with st.container():
        col9, col10 = st.columns(2)
        
        with col9:
            st.markdown('### Distância média por cidade')
            fig = dist_media_city(data)
            st.plotly_chart(fig, use_container_width=True)
            
        with col10:
            st.markdown('### Tempo médio por tipo de pedido')
            fig = tmedio_tipo_pedido(data)
            st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col7, col8 = st.columns(2)
        with col7:
            st.markdown('### Tempo médio por cidade')
            fig = tmedio_cidade(data)
            st.plotly_chart(fig, use_container_width=True)
            
        with col8:
            st.title('Tempo médio por cidade')
            fig = tmedio_cidade_trafego(data)
            st.plotly_chart(fig, use_container_width=True)