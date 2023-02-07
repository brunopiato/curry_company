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
import folium
from haversine import haversine, Unit
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão_empresa', layout = 'wide', page_icon = '📃')

#=============================================
#--------Importando os dados
#=============================================
df = pd.read_csv('train.csv')
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )



#=============================================
#--------Definindo as funções
#=============================================

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

    df1 = data.copy() #Backup do dataframe
    
    return data


########## Função para gráfico de barras  ############
def order_metric(data):
    """Mostra o número de pedidos por dia em um gráfico de barras

    Args:
        data 

    Returns:
        px.bar
    """
    
    df_aux = data[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID') 
    
    return fig


########## Função para gráfico de pizza ############
def traffic_order_share(data):
    """Mostra o gráfico de pizza com a contagem de pedidos por tipo de tráfego

    Args:
        data 

    Returns:
        px.pie
    """
    
    df_aux = data[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index() 
    pizza = px.pie(df_aux, values='ID', names='Road_traffic_density')
    
    return pizza


########## Função para gráfico de bolhas ############
def traffic_order_city(data):
    """Mostra um gráfico de bolhas com o tamanho dos pontos de acordo com o número de pedidos por cidade (x) e tráfego (y)

    Args:
        data 

    Returns:
        px.scatter
    """
    
    df_aux = data[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    bolhas = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return bolhas


########## Função para linhas por semana ############
def order_by_week(data):
    """Plota um gráfico de linhas com a quantidade de pedidos por semana do ano

    Args:
        data 

    Returns:
        px.line
    """
    
    data['week_of_year'] = data['Order_Date'].dt.strftime('%U') 
    df_aux = data[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    linhas1 = px.line(df_aux, x='week_of_year', y='ID')
    
    return linhas1


########## Função para linhas por semana por entregador ############
def order_share_by_week(data):
    """Plota um gráfico de linhas com a quantidade de pedidos por entregador por semana do ano

    Args:
        data 

    Returns:
        px.line
    """
    
    df_aux01 = data.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index() #Agrupando os pedidos por semana do ano
    df_aux02 = data.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index() #Agrupando a qtd de entregadores únicos por semana do ano
    df_aux = pd.merge(df_aux01, df_aux02, how='inner') #Combinando as duas tabelas através da semana do ano
    df_aux['order_by_deliveryman'] = df_aux['ID']/df_aux['Delivery_person_ID'] #Calculando o número de pedido médio por entregador a cada semana do ano
    linhas2 = px.line(df_aux, x='week_of_year', y='order_by_deliveryman') #Plotando o gráfico propriamente dito
    
    return linhas2


########## Função para plotar o mapa ############
def country_maps(data):
    """Plota um mapa com os pontos medianos das cidades

    Args:
        data 

    Returns:
        folium_static(mapa)
    """
    
    df_aux = data[['Road_traffic_density', 'City', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    mapa = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']]).add_to(mapa)
    folium_static(mapa, width=800, height=600)

#################################################################################################
#                            INICIANDO AS ANÁLISES
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
st.sidebar.markdown('## Fastest curry in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual data?',
                  value=pd.datetime(2022, 3, 13),
                  min_value=pd.datetime(2022, 2, 11),
                  max_value=pd.datetime(2022, 4, 6),
                  format='DD-MM-YYYY'
                 )
traffic_options = st.sidebar.multiselect(label='Em quais condições de tráfego:', 
                       options=['High', 'Jam', 'Low', 'Medium'],
                       default=['High', 'Jam', 'Low', 'Medium'])

st.sidebar.markdown('##### Powered by ComunidadeDS')

#Vinculando os widgets
linhas_selecionadas = data['Order_Date'] < data_slider
data = data.loc[linhas_selecionadas, :]

linhas_selecionadas = data['Road_traffic_density'].isin(traffic_options)
data = data.loc[linhas_selecionadas, :]

#=============================================
#Layout do projeto
#=============================================

st.header('Curry Company - Visão da empresa')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#--------------- tab1
with tab1:
    with st.container():
        st.markdown('# Visão Gerencial')
        st.markdown('### Gráfico de barras da quantidade de pedidos por dia')
        fig = order_metric(data)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)    
    with st.container():
        with col1:
            st.markdown('### Coluna 1')
            pizza = traffic_order_share(data)
            st.plotly_chart(pizza, use_container_width=True)


        with col2:
            st.markdown('### Coluna 2')
            bolhas = traffic_order_city(data)
            st.plotly_chart(bolhas, use_container_width=True)
        
    
#--------------- tab2
with tab2:
    st.markdown('# Visão Tática')
    with st.container():
        st.markdown('### Quantidade de pedidos por semana do ano')
        linhas1 = order_by_week(data)
        st.plotly_chart(linhas1, use_container_width=True)
    
    with st.container():
        st.markdown('### Quantidade de entregas por entregador por semana do ano')
        linhas2 = order_share_by_week(data)
        st.plotly_chart(linhas2, use_container_width=True)


#--------------- tab3
with tab3:
    with st.container():
        st.markdown('# Visão Geográfica')
        st.markdown('### Mapa')    
        
        country_maps(data)
        
#=============================================
#=============================================
#===================FIM=======================
#=============================================
#=============================================



