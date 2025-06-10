import pandas as pd
import streamlit as st
import plotly.express as px

#----------------------------------
#            Dados
#----------------------------------

dados = pd.read_csv('smart_manufacturing_data.csv')

#----------------------------------
#     Configuração da Página
#----------------------------------

st.set_page_config(layout= "wide")

#----------------------------------
#            Tabelas
#----------------------------------

##---Média Sensores

dados_sensores = dados.copy()
dados_sensores = dados_sensores.drop(['timestamp', 'machine_status', 'anomaly_flag', 'predicted_remaining_life', 'failure_type', 'downtime_risk', 'maintenance_required'], axis=1)
dados_sensores = dados_sensores.dropna()
dados_sensores.reset_index(drop= True, inplace= True)
media_sensores = dados_sensores.groupby('machine')[['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']].mean()
Temperatura = media_sensores['temperature']
Vibration = media_sensores['vibration']
Humidity = media_sensores['humidity']
Pressure = media_sensores['pressure']
Energy_consumption = media_sensores['energy_consumption']
media_sensores = pd.DataFrame({
    'Máquina' : media_sensores.index,
    'Temperatura' : Temperatura,
    'Vibration' : Vibration,
    'Humidity' : Humidity,
    'Pressure' : Pressure,
    'Energy_consumption' : Energy_consumption,
})
media_sensores.reset_index(drop=True, inplace=True)
media_sensores.head()

medias = media_sensores.drop(columns= ['Máquina']).mean()
df_medias = pd.DataFrame(medias).reset_index()
df_medias.columns = ['Feature', 'Media']

##----Manutenção
manutencao  = dados.copy()
manutencao = manutencao.drop(['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption'], axis=1)
manutencao['timestamp'] = pd.to_datetime(manutencao['timestamp'])
manutencao['mes'] = manutencao['timestamp'].dt.month
manutencao['dia'] = manutencao['timestamp'].dt.day
manutencao['hora'] = manutencao['timestamp'].dt.hour
manutencao['minuto'] = manutencao['timestamp'].dt.minute

manutencao.drop('timestamp', axis=1, inplace=True)

manutencao = manutencao[["machine", "mes", "dia", "hora", "minuto", "machine_status",
                        "anomaly_flag", "predicted_remaining_life", "failure_type",
                        "downtime_risk", "maintenance_required"]]

manutencao['maintenance_required'] = manutencao['maintenance_required'].fillna('Unknown')
manutencao_nan = manutencao[manutencao['maintenance_required'] == 'Unknown']
manutencao_nan.reset_index(drop=True, inplace=True)

manutencao_maquina = manutencao[manutencao['maintenance_required'] == 'Yes']
manutencao_Failure = manutencao_nan[manutencao_nan['machine_status'] == 'Failure']
manutencao_maquina = pd.concat([manutencao_maquina, manutencao_Failure], ignore_index=True)

manutencao_maquina.loc[manutencao_maquina['maintenance_required'] == 'Unknown', 'maintenance_required'] = 'Yes'

manutencao_maquina.reset_index(drop=True, inplace=True)

qtd_maquina_manutencao = manutencao_maquina.groupby('machine').size()

qtd_maquina_manutencao = pd.DataFrame({
    'Máquina' : qtd_maquina_manutencao.index,
    'QTD_manutencao' : qtd_maquina_manutencao
})
qtd_maquina_manutencao.reset_index(drop= True, inplace= True)

manutencao_maquina_mes = manutencao_maquina.groupby('mes').size()
manutencao_maquina_mes = pd.DataFrame({
    'Mes' : manutencao_maquina_mes.index,
    'qtd' : manutencao_maquina_mes
})

media_vida_util = manutencao_maquina.groupby('machine')[['predicted_remaining_life']].mean().reset_index()

#----------------------------------
#         Gráficos
#----------------------------------

## Média Sensores
fig_media_total = px.bar(df_medias,
                         y= 'Media',
                         x= 'Feature',
                         text_auto= True,
                         color= 'Feature',
                         title= 'Média dos valores lidos dos sensores das máquinas')

fig_media_temperatura = px.bar(media_sensores,
                               y= 'Temperatura',
                               x='Máquina',
                               text_auto= True,
                               title= 'Média de temperatura')

fig_media_vibracao = px.bar(media_sensores,
                               y= 'Vibration',
                               x='Máquina',
                               text_auto= True,
                               title= 'Média de Vibração')

fig_media_umidade = px.bar(media_sensores,
                               y= 'Humidity',
                               x='Máquina',
                               text_auto= True,
                               title= 'Média de umidade')

fig_media_pressao = px.bar(media_sensores,
                               y= 'Pressure',
                               x='Máquina',
                               text_auto= True,
                               title= 'Média de pressão')

fig_media_consumo_energia = px.bar(media_sensores,
                               y= 'Energy_consumption',
                               x='Máquina',
                               text_auto= True,
                               title= 'Média de consumo de energia')

## Manutenção

fig_qtd_maquinas_manutencao = px.bar(qtd_maquina_manutencao,
                                     y= 'QTD_manutencao',
                                     x= 'Máquina',
                                     text_auto= True,
                                     color= 'Máquina',
                                     title= 'Quantidade de paradads para manutenção')

fig_manutencao_maquina_mes = px.pie(manutencao_maquina_mes,
                                    names= 'Mes',
                                    values= 'qtd',
                                    title= 'Percentual de paradas para manutenção por mês')

fig_media_vida_util = px.bar(media_vida_util,
                             x= 'machine',
                             y= 'predicted_remaining_life')

#----------------------------------
#         Dashboard
#----------------------------------

st.title("Dashboard")

tab_home, tab_manutencao, tab_falhas = st.tabs(['Home', 'Manutenção', 'Falhas'])

with tab_home:
    col1, col2 = st.columns(2, border= True)
    with col1:
        idx_maior_temperatura = dados_sensores.index[dados_sensores['temperature'] == dados_sensores['temperature'].max()]
        maquina_maior_temperatura = dados_sensores.iloc[idx_maior_temperatura[0]]['machine']
        maior_temperatura = dados_sensores.iloc[idx_maior_temperatura[0]]['temperature']
        st.metric(f'Máquina com maior temperatura: {maquina_maior_temperatura}', maior_temperatura , ' Graus')

    with col2: 
        idx_maior_vibracao = dados_sensores.index[dados_sensores['vibration'] == dados_sensores['vibration'].max()]
        maquina_maior_vibracao = dados_sensores.iloc[idx_maior_vibracao[0]]['machine']
        maior_vibracao = dados_sensores.iloc[idx_maior_vibracao[0]]['vibration']
        st.metric(f'Máquina com maior vibração: {maquina_maior_vibracao}', maior_vibracao , ' mm/s')

    col1, col2, col3 = st.columns(3, border= True)
    with col1:
        idx_maior_umidade = dados_sensores.index[dados_sensores['humidity'] == dados_sensores['humidity'].max()]
        maquina_maior_umidade = dados_sensores.iloc[idx_maior_umidade[0]]['machine']
        maior_umidade = dados_sensores.iloc[idx_maior_umidade[0]]['humidity']
        st.metric(f'Máquina com maior umidade: {maquina_maior_umidade}', maior_umidade , ' %')

    with col2: 
        idx_maior_pressao = dados_sensores.index[dados_sensores['pressure'] == dados_sensores['pressure'].max()]
        maquina_maior_pressao = dados_sensores.iloc[idx_maior_pressao[0]]['machine']
        maior_pressao = dados_sensores.iloc[idx_maior_pressao[0]]['pressure']
        st.metric(f'Máquina com maior pressão: {maquina_maior_pressao}', maior_pressao , ' kPa')

    with col3: 
        idx_maior_consumo = dados_sensores.index[dados_sensores['energy_consumption'] == dados_sensores['energy_consumption'].max()]
        maquina_maior_consumo = dados_sensores.iloc[idx_maior_consumo[0]]['machine']
        maior_consumo = dados_sensores.iloc[idx_maior_consumo[0]]['energy_consumption']
        st.metric(f'Máquina com maior consumo de energia: {maquina_maior_consumo}', maior_consumo , ' kWh')


    st.plotly_chart(fig_media_total)
    
    
    with st.container(height= 500):
        st.subheader('Média dos valores dos sensores por máquina')
        st.plotly_chart(fig_media_temperatura)
        st.plotly_chart(fig_media_vibracao)
        st.plotly_chart(fig_media_umidade)
        st.plotly_chart(fig_media_pressao)
        st.plotly_chart(fig_media_consumo_energia)

with tab_manutencao:

    col1, col2 = st.columns(2, border= True)
    with col1:
        idx_maior_manutencao = qtd_maquina_manutencao.index[qtd_maquina_manutencao['QTD_manutencao'] == qtd_maquina_manutencao['QTD_manutencao'].max()]
        maquina_maior_manutencao = qtd_maquina_manutencao.iloc[idx_maior_manutencao[0]]['Máquina']
        maior_manutencao = qtd_maquina_manutencao.iloc[idx_maior_manutencao[0]]['QTD_manutencao']
        st.metric(f'Máquina com maior número de paradas para manutenção: {maquina_maior_manutencao}', maior_manutencao)

        idx_menor_manutencao = qtd_maquina_manutencao.index[qtd_maquina_manutencao['QTD_manutencao'] == qtd_maquina_manutencao['QTD_manutencao'].min()]
        maquina_menor_manutencao = qtd_maquina_manutencao.iloc[idx_menor_manutencao[0]]['Máquina']
        menor_manutencao = qtd_maquina_manutencao.iloc[idx_menor_manutencao[0]]['QTD_manutencao']
        st.metric(f'Máquina com menor número de paradas para manutenção: {maquina_menor_manutencao}', menor_manutencao)

    with col2:
        st.plotly_chart(fig_manutencao_maquina_mes)

    st.plotly_chart(fig_qtd_maquinas_manutencao)
    st.plotly_chart(fig_media_vida_util)

    
    st.dataframe(media_vida_util)