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

st.set_page_config(page_title = 'Visão entregadores', layout = 'wide', page_icon = '🚲')

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

    df1 = data.copy() #Backup do dataframe
    
    return data

########## Função para avaliação média por tráfego ############
def media_por_transito(data):
    """Apresenta um dataframe com as avaliações médias e desvio padrão por trafego

    Args:
        data

    Returns:
        _type_: _description_
    """
    df_aux = (data[['Delivery_person_Ratings', 'Road_traffic_density']]
              .groupby('Road_traffic_density')
              .agg({'Delivery_person_Ratings': ['mean', 'std']}))
    df_aux.columns = ['delivery_mean', 'delivery_std']
    df_aux = df_aux.reset_index()
    return df_aux



########## Função para tabela de média por clima ############
def media_por_clima(data):
    """Apresenta um dataframe com as avaliações médias e desvio padrão por condição climática

    Args:
        data

    Returns:
        _type_: _description_
    """
    df_aux = data[['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
    df_aux.columns = ['delivery_mean', 'delivery_std']
    df_aux = df_aux.reset_index()
    return df_aux




########## Função para o top 10 mais rápidos ############
def top10_rapidos(data):
    """Apresenta um dataframe mostrando os 10 entregadores mais rápidos

    Args:
        data

    Returns:
        _df
    """
    
    df_aux = (data[['Delivery_person_ID', 'Time_taken(min)', 'City']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean()
            .sort_values('Time_taken(min)', ascending=True)
            .round(2)
            .reset_index())
    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df


########## Função para o top 10 mais lentos ############
def top10_lentos(data):
    """Apresenta um dataframe mostrando os 10 entregadores mais lentos
    Args:
        data

    Returns:
        df
    """
    df_aux = (data[['Delivery_person_ID', 'Time_taken(min)', 'City']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean()
            .sort_values('Time_taken(min)', ascending=False)
            .round(2)
            .reset_index())
    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True).sort_values('Time_taken(min)', ascending=False)
    return df



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
st.sidebar.markdown('##### *Fastest curry in town*')
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
                       default = ['High', 'Jam', 'Low', 'Medium'])

weather_options = st.sidebar.multiselect(label='Em quais condições climáticas:', 
                       options=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'],
                       default = ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'])

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

st.header('Curry Company - Visão dos entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'x', 'x'])

with tab1:
    with st.container():
        st.title('Métricas gerais')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            #A maior idade dos entregadores
            st.markdown('##### Maior idade')
            maior_idade = data.loc[:, "Delivery_person_Age"].max()
            col1.metric('Maior idade:', maior_idade)
        with col2:
            #A maior idade dos entregadores
            st.markdown('##### Menor idade')
            menor_idade = data.loc[:, "Delivery_person_Age"].min()
            col2.metric('Menor idade:', menor_idade)
        with col3:
            st.markdown('##### Melhor condição de veículo')
            melhor_veic = data["Vehicle_condition"].max()
            col3.metric('A melhor condição é:', melhor_veic)
        with col4:
            st.markdown('##### Pior condição de veículo')
            pior_veic = data["Vehicle_condition"].min()
            col4.metric('A pior condição é:', pior_veic)
    
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col5, col6 = st.columns(2, gap='large')
        with col5:
            st.markdown('##### Avaliação média por entregador')
            df_aux = (data[['Delivery_person_ID', 'Delivery_person_Ratings']]
                      .groupby('Delivery_person_ID')
                      .mean()
                      .sort_values('Delivery_person_Ratings', ascending=False)
                      .reset_index())
            st.dataframe(df_aux)
            
        with col6:
            st.markdown('##### Avaliação média por trânsito')
            df_aux = media_por_transito(data)
            st.dataframe(df_aux)
            
            st.markdown('##### Avaliação média por condições climáticas')
            df_aux = media_por_clima(data)
            st.dataframe(df_aux)
        
    
    with st.container():
        st.markdown("""---""")
        st.title('Top entregadores')

        col7, col8 = st.columns(2, gap='large')
        with col7:
            st.markdown('##### Top 10 entregadores mais rápidos')
            df = top10_rapidos(data)
            st.dataframe(df)
            
        with col8:
            st.markdown('##### Top 10 entregadores mais lentos')
            df = top10_lentos(data)
            st.dataframe(df)