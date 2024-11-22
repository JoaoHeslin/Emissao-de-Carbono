import pandas as pd
import plotly.express as px
import streamlit as st

# Carregando os dados
@st.cache_data
def carregar_dados(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df

# Carregando os dados
df = carregar_dados('Carbon_(CO2)_Emissions_by_Country.csv')

# Sidebar para seleção de continente
st.sidebar.title("Continentes")
opcoes = ['Mundo'] + list(df['Region'].unique())
continente_selecionado = st.sidebar.selectbox('Selecione o Continente:', opcoes)

# Filtrando os dados
df_filtrado = df if continente_selecionado == 'Mundo' else df[df['Region'] == continente_selecionado]

#Titulo da Página:
st.markdown("""
<h1 style="text-align: center; color: black;">
    Análise Interativa das Emissões Globais de CO₂
</h1>
<h6 style="text-align: center; color: black;">
    Entenda como diferentes regiões e países contribuem para as emissões de carbono e visualize padrões de emissões totais e ao longo do tempo.
</h6>
""", unsafe_allow_html=True)

# Agrupando os dados necessarios
numericas = df.select_dtypes(include='number').columns.tolist()

agrup_reg = df_filtrado.groupby('Region')[numericas].agg({
    'Kilotons of Co2': 'sum',
    'Metric Tons Per Capita': 'mean',
}).reset_index()

agrup_temp = df_filtrado.groupby(df['Date'].dt.year)[numericas].agg({
    'Kilotons of Co2': 'sum',
    'Metric Tons Per Capita': 'mean',
}).reset_index().rename(columns={'Date': 'Year'})

agrup_temp_reg = df_filtrado.groupby(['Date', 'Region'])[numericas].agg({
    'Kilotons of Co2': 'sum',
    'Metric Tons Per Capita': 'mean',
}).reset_index().rename(columns={'Date': 'Year'})

agrup_pais = df_filtrado.groupby(df.Country)[numericas].agg({
    'Kilotons of Co2': 'sum',
    'Metric Tons Per Capita': 'mean',
}).reset_index().rename(columns={'Date': 'Year'})

# Criando colunas para os gráficos
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)
col7, col8 = st.columns(2)

if continente_selecionado == 'Mundo':  #Graficos para o Mundo todo

    soma_global = df_filtrado['Kilotons of Co2'].sum()
    media_capita_global = df_filtrado['Metric Tons Per Capita'].sum()
  
    col1.metric("Soma Total Global de CO₂ (Kilotons)", f"{soma_global:.2f}")
    col2.metric("Média Total Global de CO₂ Per Capita", f"{media_capita_global:.2f}")

    col1.plotly_chart(
        px.pie(agrup_reg, 
               names='Region', 
               values='Kilotons of Co2', 
               title='Proporção total das emissões de CO₂ por Região', 
               hole=0.4), 
        use_container_width=True)

    col2.plotly_chart(
        px.pie(agrup_reg, 
               names='Region', 
               values='Metric Tons Per Capita', 
               title='Proporção total da emissão de CO₂ Per Capita por Região', 
               hole=0.4), 
        use_container_width=True)
    
    col5.plotly_chart(
        px.line(agrup_temp_reg, 
                x='Year', 
                y='Kilotons of Co2', 
                color='Region',
                title='Emissão Total de CO₂ ao longo dos anos por Região'), 
        use_container_width=True)
    
    col6.plotly_chart(
        px.line(agrup_temp_reg, 
                x='Year', 
                y='Metric Tons Per Capita', 
                color='Region',
                title='Emissão Total de CO₂ Per Capita ao longo dos anos por Região'), use_container_width=True)
    
    paises_mais_emissores = (df.groupby('Country')['Kilotons of Co2']
    .sum()
    .sort_values(ascending=False)
    .head()
    .reset_index()) 
       
    paises_capita_mais_emissores = (df.groupby('Country')['Metric Tons Per Capita']
    .mean()
    .sort_values(ascending=False)
    .head()
    .reset_index())
    
    col7.plotly_chart(
        px.bar(paises_mais_emissores, 
               x="Country", 
               y="Kilotons of Co2", 
               title='Países Mais Emissores de CO₂',
               text_auto=True), 
        use_container_width=True)
    
    col8.plotly_chart(
        px.bar(paises_capita_mais_emissores, 
               x="Country", 
               y="Metric Tons Per Capita", 
               title='Países mais Emissores de CO₂ Per Capita',
               text_auto=True),
        use_container_width=True)
    
    
    col9, col10 = st.columns(2)
    
    top_paises = df.groupby('Country')['Kilotons of Co2'].sum().nlargest().index
    filtrado = df[df['Country'].isin(top_paises)]
    agrup_pais_data = filtrado.groupby(['Country', 'Date'])[['Kilotons of Co2']].sum().reset_index()
    
    col9.plotly_chart(
        px.line(agrup_pais_data,
                x='Date',
                y='Kilotons of Co2',
                color='Country',
                title='Países mais emissores de CO₂ ao longo dos Anos'
                ), 
        use_container_width=True)
    
    top_paises_capita = df.groupby('Country')['Metric Tons Per Capita'].sum().nlargest().index
    filtrado_capita = df[df['Country'].isin(top_paises_capita)]
    agrup_pais_data_capita = filtrado_capita.groupby(['Country', 'Date'])[['Metric Tons Per Capita']].sum().reset_index()
    
    col10.plotly_chart(
        px.line(agrup_pais_data_capita,
                x='Date',
                y='Metric Tons Per Capita',
                color='Country',
                title='Países mais emissores de CO₂ Per Capita ao longo dos Anos'
                ), 
        use_container_width=True)
    
    
    col11 = st.columns(1)[0]
    col12 = st.columns(1)[0]
    
    col11.plotly_chart(
        px.choropleth(agrup_pais, 
                      locations='Country',
                      locationmode='country names', 
                      color='Kilotons of Co2',
                      color_continuous_scale='Blues',
                      title=f'Emissão Total de CO₂ Global')
        .update_layout(width=900, 
            height=500,
            margin={"r":0,"t":50,"l":0,"b":0}),
        use_container_width=False)
    
    col12.plotly_chart(
    px.choropleth(agrup_pais, 
                  locations='Country', 
                  locationmode='country names', 
                  color='Metric Tons Per Capita',
                  color_continuous_scale='Greens',
                  title=f'Emissão Total Per Capita de CO₂ global')
    .update_layout(width=900,
                   height=500, 
                   margin={"r":0,"t":50,"l":0,"b":0}), 
    use_container_width=False)
    
    col13 = st.columns(1)[0]
    
    continente_pais = df.groupby(['Region', 'Country'])['Kilotons of Co2'].sum().reset_index()
    col13.plotly_chart(
        px.treemap(continente_pais, 
                   path=['Region', 'Country'], 
                   values='Kilotons of Co2',
                   title='Acumuilativo da Emissão de CO₂').
        update_layout(width=700,
                   height=500, 
                   margin={"r":0,"t":50,"l":0,"b":0}), 
        use_container_width=False)
   
else:  #Graficos para os Continentes
    soma_regional = df_filtrado.groupby('Region')['Kilotons of Co2'].sum()
    media_capita_regional = df_filtrado.groupby('Region')['Metric Tons Per Capita'].mean()

    emissao_regiao = soma_regional.get(continente_selecionado, 0)
    emissao_regiao_capita = media_capita_regional.get(continente_selecionado, 0)

    col1.metric(label=f'Emissão Total de Carbono na {continente_selecionado} (Kilotons)', 
                value=f'{emissao_regiao:.2f}')
    
    col2.metric(label=f'Emissão Total Per Capita de Carbono na {continente_selecionado} (Kilotons)', 
                value=f'{emissao_regiao_capita:.2f}')
    
    top_paises_regiao = (df.groupby(["Region", "Country"])[["Kilotons of Co2"]]
    .sum()
    .reset_index()
    .sort_values(by=["Region", "Kilotons of Co2"], ascending=[True, False])
    .groupby("Region")
    .head()  
)
    top_paises_capita_regiao = (df.groupby(["Region", "Country"])[["Metric Tons Per Capita"]]
    .mean()
    .reset_index()
    .sort_values(by=["Region", "Metric Tons Per Capita"], ascending=[True, False])
    .groupby("Region")
    .head()  
)
    emissores_por_regiao = top_paises_regiao[top_paises_regiao['Region'] == continente_selecionado]
    emissores_capita_regiao = top_paises_capita_regiao[top_paises_capita_regiao['Region'] == continente_selecionado]
    
    col5.plotly_chart(
        px.bar(emissores_por_regiao, 
               x="Country", 
               y="Kilotons of Co2", 
               title=f'Países Mais Emissores de CO₂ na {continente_selecionado}',
               text_auto=True), 
        use_container_width=True)
    
    col6.plotly_chart(
        px.bar(emissores_capita_regiao, 
               x="Country", 
               y="Metric Tons Per Capita", 
               title=f'Países mais Emissores de CO₂ Per Capita na {continente_selecionado}',
               text_auto=True),
        use_container_width=True)
    
    
    filtrado_total = df_filtrado[df_filtrado['Country'].isin(top_paises_regiao['Country'])]
    agrup_pais_data_total = filtrado_total.groupby(['Country', "Date"])['Kilotons of Co2'].sum().reset_index()
    
    col7.plotly_chart(
        px.line(agrup_pais_data_total, 
                x= 'Date', 
                y='Kilotons of Co2', 
                color='Country',
                title=f'Países mais emissores de CO₂  na {continente_selecionado} ao longo dos anos'),
        use_container_width=True
        )
    
    filtrado_capita = df_filtrado[df_filtrado['Country'].isin(top_paises_capita_regiao['Country'])]
    agrup_pais_data_capita = filtrado_capita.groupby(['Date', 'Country'])['Metric Tons Per Capita'].mean().reset_index()
    
    col8.plotly_chart(
        px.line(agrup_pais_data_capita,
                x='Date',
                y='Metric Tons Per Capita',
                color='Country',
                title=f'Países mais emissores de CO₂ Per Capita na {continente_selecionado} ao longo dos anos'),
        use_container_width=True
    )
    
    
    col9 = st.columns(1)[0] 
    col10 = st.columns(1)[0]
    
    col9.plotly_chart(
        px.choropleth(agrup_pais, 
                      locations='Country',
                      locationmode='country names', 
                      color='Kilotons of Co2',
                      color_continuous_scale='Blues',
                      title=f'Emissão Total de CO₂ na {continente_selecionado}')
        .update_layout( width=900, 
                       height=500, 
                       margin={"r":0,"t":50,"l":0,"b":0}), 
        use_container_width=False)
    
    col10.plotly_chart(
    px.choropleth(agrup_pais, 
                  locations='Country', 
                  locationmode='country names', 
                  color='Metric Tons Per Capita',
                  color_continuous_scale='Greens',
                  title=f'Emissão Total Per Capita de CO₂ na {continente_selecionado}')
    .update_layout(width=900,
                   height=500, 
                   margin={"r":0,"t":50,"l":0,"b":0}), 
    use_container_width=False)
    

#Gráficos em comum
col3.plotly_chart(
    px.line(agrup_temp, 
            x='Year', 
            y='Kilotons of Co2', 
            title='Emissões de CO₂ ao longo dos anos'),
    use_container_width=True)

col4.plotly_chart(
    px.line(agrup_temp, 
            x='Year', 
            y='Metric Tons Per Capita', 
            title='Emissão de CO₂ Per Capita ao longo dos anos'), 
    use_container_width=True)