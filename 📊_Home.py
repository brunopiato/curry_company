import streamlit as st
from PIL import Image
st.set_page_config(
    page_title = "Home",
    page_icon = ":📊bar_chart:")

#image_path = '/home/piatobruno/repos/FTC_Python/imgs/'
image = Image.open('curry_delivery.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Curry company')
st.sidebar.markdown('## Fastest curry in town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown("""
            Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores, restaurantes e da empresa.
            ### Como utilizar o Growth Dashboard?
            - Visão Empresa:
                - Visão gerencial: Métricas gerais de comportamento.
                - Visão tática: Indicadores semanais de crescimento.
                - Visão geográfica: Insights de geolocalização.
            - Visão Entregadores: 
                - Acompanhamento dos indicadores semanais de crescimento.
            - Visão Restaurantes:
                - Indicadores semanais de crescimento
            ### Ask for help
                - Time de Data Science no Discord
                    - @piatobruno#0143
            """)
