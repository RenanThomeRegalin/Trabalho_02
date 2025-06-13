import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.preprocessing import OrdinalEncoder

#----------------------------------
#            Dados
#----------------------------------

dados = pd.read_csv('smart_manufacturing_data.csv')

#----------------------------------
#     Configuração da Página
#----------------------------------

st.set_page_config(layout= "wide")

#----------------------------------
#              Sidebar
#----------------------------------

dados['timestamp'] = pd.to_datetime(dados['timestamp'])

st.sidebar.title('Filtros')

data_min = dados['timestamp'].min().to_pydatetime()
data_max = dados['timestamp'].max().to_pydatetime()

with st.sidebar.expander("Data"):
    todas_datas = st.checkbox("Todas as datas", value=True)

    if todas_datas:
        f_data = (data_min, data_max)
    else:
        f_data = st.slider(
            "Selecione o intervalo de data",
            min_value=data_min,
            max_value=data_max,
            value=(data_min, data_max),
            format="YYYY-MM-DD"
        )

with st.sidebar.expander('Máquina'):
    maquinas = dados['machine'].unique()
    f_maquinas = st.multiselect('Selecione as máquinas', maquinas, default= maquinas)

with st.sidebar.expander('Falhas'):
    falhas = dados['failure_type'].unique()
    f_falhas = st.multiselect('Selecione o tipo de falha', falhas, default= falhas)

#Filtro de dados

query = '''
@f_data[0] <= timestamp <= @f_data[1] and \
machine in @f_maquinas and \
failure_type in @ f_falhas
'''

dados = dados.query(query)



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

##------Falhas

normal = manutencao_maquina[manutencao_maquina['failure_type'] == 'Normal'].groupby('machine').size()
Electrical_Fault = manutencao_maquina[manutencao_maquina['failure_type'] == 'Electrical Fault'].groupby('machine').size()
Overheating = manutencao_maquina[manutencao_maquina['failure_type'] == 'Overheating'].groupby('machine').size()
Pressure_Drop	= manutencao_maquina[manutencao_maquina['failure_type'] == 'Pressure Drop'].groupby('machine').size()
Vibration_Issue	= manutencao_maquina[manutencao_maquina['failure_type'] == 'Vibration Issue'].groupby('machine').size()


qtd_maquinas_falhas = pd.DataFrame({
    'Máquina' : media_sensores.index,
    'Normal' : normal,
    'Electrical Fault' : Electrical_Fault,
    'Overheating' : Overheating,
    'Pressure Drop' : Pressure_Drop,
    'Vibration Issue' : Vibration_Issue
})
qtd_maquinas_falhas.reset_index(drop=True, inplace=True)

##Percenttual

percentual_falhas = manutencao.copy()

percentual_falhas['machine_status'] = percentual_falhas['machine_status'].fillna('Unknown')

idle = percentual_falhas[percentual_falhas['machine_status'] == 'Idle'].groupby('machine').size()
running = percentual_falhas[percentual_falhas['machine_status'] == 'Running'].groupby('machine').size()
failure = percentual_falhas[percentual_falhas['machine_status'] == 'Failure'].groupby('machine').size()
unknown = percentual_falhas[percentual_falhas['machine_status'] == 'Unknown'].groupby('machine').size()

percentual_falhas_maquinas = pd.DataFrame({
    'Máquina' : maquinas,
    'Idle' : idle,
    'Running' : running,
    'Failure' : failure,
    'Unknown' : unknown
})

percentual_falhas_maquinas.reset_index(drop=True, inplace=True)

percentual_falhas_maquinas['Total'] = percentual_falhas_maquinas.drop(columns='Máquina').sum(axis=1)

somas = percentual_falhas_maquinas[['Idle', 'Running', 'Failure', 'Unknown']].sum()

df_duas_colunas = somas.reset_index()
df_duas_colunas.columns = ['Feature', 'Valor']



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
                             y= 'predicted_remaining_life',
                             text_auto= True,
                             color= 'machine',
                             title= 'Média de vida útil de cada máquina')

# Falhas

fig_falha_normal = px.bar(qtd_maquinas_falhas,
                          x= 'Máquina',
                          y= 'Normal',
                          text_auto= True,
                          color= 'Máquina',
                          title= 'Número de paradas por máquina para manutenção de rotina')

fig_falha_eletrico = px.bar(qtd_maquinas_falhas,
                          x= 'Máquina',
                          y= 'Electrical Fault',
                          text_auto= True,
                          color= 'Máquina',
                          title= 'Número de paradas por máquina por falha elétrica')

fig_falha_temperatura = px.bar(qtd_maquinas_falhas,
                          x= 'Máquina',
                          y= 'Overheating',
                          text_auto= True,
                          color= 'Máquina',
                          title= 'Número de paradas por máquina por temperatura elevada')

fig_falha_pressao = px.bar(qtd_maquinas_falhas,
                          x= 'Máquina',
                          y= 'Pressure Drop',
                          text_auto= True,
                          color= 'Máquina',
                          title= 'Número de paradas por máquina por queda de pressão')

fig_falha_vibracao = px.bar(qtd_maquinas_falhas,
                          x= 'Máquina',
                          y= 'Vibration Issue',
                          text_auto= True,
                          color= 'Máquina',
                          title= 'Número de paradas por máquina por vibração elevada')

fig_status_percentual = px.pie(df_duas_colunas,
                                    names= 'Feature',
                                    values= 'Valor',
                                    title= 'Status das máquinas')

fig_total_falha = px.bar(percentual_falhas_maquinas,
                         x= 'Máquina',
                         y= 'Failure',
                         text_auto= True,
                         color= 'Máquina',
                         title= 'Quantidade de falha por máquina')

#----------------------------------
#         Dashboard
#----------------------------------

st.title("Dashboard Análise Máquinas")

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

with tab_falhas:

    col1, col2 = st.columns(2, border= True)
    with col1:
        if 'Normal' in f_falhas:
            idx_maior_normal = qtd_maquinas_falhas.index[qtd_maquinas_falhas['Normal'] == qtd_maquinas_falhas['Normal'].max()]
            maquina_maior_normal = qtd_maquinas_falhas.iloc[idx_maior_normal[0]]['Máquina']
            maior_normal = qtd_maquinas_falhas.iloc[idx_maior_normal[0]]['Normal']
            st.metric(f'Maior número de paradas para manutenção de rotina: {maquina_maior_normal}', maior_normal, 'Paradas')
            
        else:
            st.write("A seleção Normal foi desativada.")

        
        if 'Electrical Fault' in f_falhas:
            idx_maior_eletrico = qtd_maquinas_falhas.index[qtd_maquinas_falhas['Electrical Fault'] == qtd_maquinas_falhas['Electrical Fault'].max()]
            maquina_maior_eletrico = qtd_maquinas_falhas.iloc[idx_maior_eletrico[0]]['Máquina']
            maior_eletrico = qtd_maquinas_falhas.iloc[idx_maior_eletrico[0]]['Electrical Fault']
            st.metric(f'Maior número de paradas por falha elétrica: {maquina_maior_eletrico}', maior_eletrico, 'Paradas')
        else:
            st.write("A seleção Electrical Fault foi desativada.")

        if 'Overheating' in f_falhas:
            idx_maior_aquecimento = qtd_maquinas_falhas.index[qtd_maquinas_falhas['Overheating'] == qtd_maquinas_falhas['Overheating'].max()]
            maquina_maior_aquecimento = qtd_maquinas_falhas.iloc[idx_maior_aquecimento[0]]['Máquina']
            maior_aquecimento = qtd_maquinas_falhas.iloc[idx_maior_aquecimento[0]]['Overheating']
            st.metric(f'Maior número de paradas por superaquecimento: {maquina_maior_aquecimento}', maior_aquecimento, 'Paradas')
        else:
            st.write("A seleção Overheating foi desativada.")

        if 'Pressure Drop' in f_falhas:
            idx_maior_pressao = qtd_maquinas_falhas.index[qtd_maquinas_falhas['Pressure Drop'] == qtd_maquinas_falhas['Pressure Drop'].max()]
            maquina_maior_pressao = qtd_maquinas_falhas.iloc[idx_maior_pressao[0]]['Máquina']
            maior_pressao = qtd_maquinas_falhas.iloc[idx_maior_pressao[0]]['Pressure Drop']
            st.metric(f'Maior número de paradas por queda de pressão: {maquina_maior_pressao}', maior_pressao, 'Paradas')
        else:
            st.write("A seleção Pressure Drop foi desativada.")

        if 'Vribration Issue' in f_falhas:
            idx_maior_vibracao = qtd_maquinas_falhas.index[qtd_maquinas_falhas['Vibration Issue'] == qtd_maquinas_falhas['Vibration Issue'].max()]
            maquina_maior_vibracao = qtd_maquinas_falhas.iloc[idx_maior_vibracao[0]]['Máquina']
            maior_vibracao = qtd_maquinas_falhas.iloc[idx_maior_vibracao[0]]['Vibration Issue']
            st.metric(f'Maior número de paradas por exesso de vibração: {maquina_maior_vibracao}', maior_vibracao, 'Paradas')
        else:
            st.write("A seleção Vribration Issue foi desativada.")

    with col2:
        st.plotly_chart(fig_status_percentual)

    with st.container(height= 500):
        st.subheader('Quantidade de paradas por máquina para cada tipo de falha')
        st.plotly_chart(fig_falha_normal)
        st.plotly_chart(fig_falha_eletrico)
        st.plotly_chart(fig_falha_temperatura)
        st.plotly_chart(fig_falha_pressao)
        st.plotly_chart(fig_falha_vibracao)

    st.plotly_chart(fig_total_falha)

#st.dataframe(percentual_falhas_maquinas)