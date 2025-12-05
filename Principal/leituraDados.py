import pandas as pd
import streamlit as st

def load_data(uploaded_file):
    # Tenta ler o CSV com diferentes separadores
    try:
        return pd.read_csv(uploaded_file)
    except:
        return pd.read_csv(uploaded_file, sep=';')

def process_data(df, col_data, col_consumo):
    # Processa as colunas de data e consumo
    df['Data_Processada'] = pd.to_datetime(df[col_data], errors='coerce')
    df['Consumo_Processado'] = pd.to_numeric(df[col_consumo], errors='coerce')
    df = df.dropna(subset=['Data_Processada', 'Consumo_Processado'])
    df = df.sort_values('Data_Processada')
    return df

def calculate_kpis(df):
    # Calcula KPIs básicos
    total = df['Consumo_Processado'].sum()
    media = df['Consumo_Processado'].mean()
    maximo = df['Consumo_Processado'].max()
    return total, media, maximo

def get_smart_insight(df, group_col, value_col):
    # Retorna o grupo com maior valor médio
    df_grouped = df.groupby(group_col)[value_col].mean().reset_index()
    # Encontra a linha com o valor máximo
    pior_row = df_grouped.loc[df_grouped[value_col].idxmax()]
    return pior_row[group_col]

def detect_anomalies(df, threshold_factor=5):
    # Detecta anomalias
    media = df['Consumo_Processado'].mean()
    limite = media * threshold_factor
    anomalias = df[df['Consumo_Processado'] > limite]
    
    hora_comum = None
    if not anomalias.empty:
        # Calcula a hora mais comum dos picos
        hora_comum = anomalias['Data_Processada'].dt.hour.mode()[0]
        
    return anomalias, limite, hora_comum