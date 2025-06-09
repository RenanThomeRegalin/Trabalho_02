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

#----------------------------------
#         Gráficos
#----------------------------------

fig_media_total = px.bar(df_medias,
                         y= 'Media',
                         x= 'Feature')

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
#----------------------------------
#         Dashboard
#----------------------------------

st.title("Dashboard")

tab_home, tab_manutencao = st.tabs(['Home', 'Manutenção'])

with tab_home:

    st.plotly_chart(fig_media_total)
    
    with st.container(height= 500):
        st.subheader('Média dos valores dos sensores por máquina')
        st.plotly_chart(fig_media_temperatura)
        st.plotly_chart(fig_media_vibracao)
        st.plotly_chart(fig_media_umidade)
        st.plotly_chart(fig_media_pressao)
        st.plotly_chart(fig_media_consumo_energia)

    st.dataframe(df_medias)