import plotly.express as px
import pandas as pd

def plot_trend_line(df):
    """Gera o gráfico de linha mensal."""
    # Agrupa por Mês (ME = Month End)
    df_mensal = df.set_index('Data_Processada').resample('ME')['Consumo_Processado'].sum().reset_index()
    
    fig = px.line(
        df_mensal, 
        x='Data_Processada', 
        y='Consumo_Processado', 
        markers=True,
        labels={'Data_Processada': 'Mês', 'Consumo_Processado': 'Consumo (kWh)'}
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def plot_bar_chart(df, x_col, y_col, title, color_scale='Blues', use_map=False):
    """Gera gráficos de barras genéricos com gradiente de cor."""
    
    # Agrupa os dados
    df_grouped = df.groupby(x_col)[y_col].mean().reset_index()

    # Mapeamento para dias da semana, se necessário
    if use_map:
        # Tenta converter para número para ordenar corretamente
        df_grouped['sort_key'] = pd.to_numeric(df_grouped[x_col], errors='coerce')
        
        # Se for numérico e estiver entre 0-7, mapeia para nomes
        if df_grouped['sort_key'].notnull().all() and df_grouped['sort_key'].max() <= 7:
            mapa_dias = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo', 7: 'Domingo'}
            df_grouped['Dia_Nome'] = df_grouped['sort_key'].map(mapa_dias)
            x_col = 'Dia_Nome' # Atualiza o eixo X para usar o nome
            df_grouped = df_grouped.sort_values('sort_key') # Ordena por número (Seg->Dom)

    fig = px.bar(
        df_grouped, 
        x=x_col, 
        y=y_col,
        color=y_col,
        color_continuous_scale=color_scale,
        title=title,
        labels={y_col: 'Média (kWh)'}
    )

    # Ajuste de Sensibilidade (Zoom no eixo Y)
    min_val = df_grouped[y_col].min()
    max_val = df_grouped[y_col].max()
    margin = (max_val - min_val) * 0.2
    if margin == 0: margin = 0.1
    
    fig.update_yaxes(range=[max(0, min_val - margin), max_val + margin])
    
    return fig, df_grouped # Retorna o DF também para pegar o nome do maior dia