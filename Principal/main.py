import streamlit as st
import pandas as pd
import leituraDados as utils
import graficos as charts

# 1. Configuração da página
st.set_page_config(page_title="EcoMonitor - ODS 7", page_icon="⚡", layout="wide")

# Cabeçalho
st.title("⚡ Sistema de Monitoramento de Eficiência Energética")
st.markdown("""
**Projeto de Extensão - Engenharia de Computação**
Objetivo: Análise de padrões de consumo elétrico para promoção de Energia Limpa e Acessível (ODS 7).
""")
st.markdown("---")

# 2. Upload de arquivo
st.subheader("📂 Carregue seus dados")
uploaded_file = st.file_uploader("Arraste seu CSV aqui", type="csv")

if uploaded_file is None:
    st.info("👆 Por favor, faça o upload do arquivo CSV para iniciar a análise.")
    st.markdown("Exemplo de estrutura esperada:")
    st.markdown("- Coluna de Data/Hora (ex: `StartDate: 2026-01-01 00:00:00`)")
    st.markdown("- Coluna de Valor (ex: `Value (kWh)`)")
    st.markdown("- (Opcional) Notas sobre o dia (ex: `day_of_week: 1-7`, `notes: weekend/weekday/vacation`)")
else:
    try:
        # Carrega o DF bruto
        df_raw = utils.load_data(uploaded_file)

        # Seletor de colunas
        st.markdown("### ⚙️ Configuração das Colunas")
        cols = list(df_raw.columns)
        c1, c2, c3, c4 = st.columns(4)
        
        # Tenta selecionar as colunas automaticamente
        idx_data = next((i for i, c in enumerate(cols) if 'date' in c.lower()), 0)
        idx_cons = next((i for i, c in enumerate(cols) if 'value' in c.lower() or 'kwh' in c.lower()), 0)
        idx_day = next((i for i, c in enumerate(cols) if 'day' in c.lower()), None)
        idx_note = next((i for i, c in enumerate(cols) if 'notes' in c.lower() or 'cat' in c.lower()), None)

        col_data = c1.selectbox("DATA/HORA:", cols, index=idx_data)
        col_consumo = c2.selectbox("CONSUMO (kWh):", cols, index=idx_cons)
        col_dia_semana = c3.selectbox("Dia da Semana (0-6):", ["Nenhuma"] + cols, index=(idx_day + 1 if idx_day is not None else 0))
        col_notas = c4.selectbox("Categoria (ex: notes):", ["Nenhuma"] + cols, index=(idx_note + 1 if idx_note is not None else 0))

        st.markdown("---")

        if st.button("🚀 Gerar Análise Completa", type="primary"):
            
            with st.spinner('Processando inteligência de dados...'):
                # Processamento
                df = utils.process_data(df_raw, col_data, col_consumo)

                # Dashboard
                st.subheader("📊 3. Diagnóstico de Consumo")

                # KPIs
                total, media, maximo = utils.calculate_kpis(df)
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Consumo Total", f"{total:,.0f} kWh")
                k2.metric("Média Hora", f"{media:.2f} kWh")
                k3.metric("Pico Máximo", f"{maximo:.2f} kWh")

                # GRÁFICO 1: Tendência (Charts)
                st.markdown("### 📈 Tendência Mensal")
                fig_trend = charts.plot_trend_line(df)
                st.plotly_chart(fig_trend, use_container_width=True)

                # ANÁLISE 1: Dia da Semana
                if col_dia_semana != "Nenhuma":
                    st.markdown("### 🗓️ Detalhe por Dia da Semana")
                    # Gera gráfico e o DF agrupado para pegarmos o nome do dia
                    fig_dia, df_dia_grouped = charts.plot_bar_chart(
                        df.dropna(subset=[col_dia_semana]), 
                        x_col=col_dia_semana, 
                        y_col='Consumo_Processado', 
                        title="Consumo Médio por Dia", 
                        use_map=True
                    )
                    st.plotly_chart(fig_dia, use_container_width=True)
                    
                    # Pega o nome do dia com maior consumo médio
                    col_nome_final = 'Dia_Nome' if 'Dia_Nome' in df_dia_grouped.columns else col_dia_semana
                    pior_dia = utils.get_smart_insight(df_dia_grouped, col_nome_final, 'Consumo_Processado')
                    st.info(f"💡 **Análise:** Em média, o consumo é maior durante: **{pior_dia}**.")

                # ANÁLISE 2: Categorias
                if col_notas != "Nenhuma":
                    st.markdown("### 🏷️ Categorias")
                    fig_cat, df_cat_grouped = charts.plot_bar_chart(
                        df, 
                        x_col=col_notas, 
                        y_col='Consumo_Processado', 
                        title="Média por Categoria"
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
                    
                    pior_cat = utils.get_smart_insight(df_cat_grouped, col_notas, 'Consumo_Processado')
                    st.info(f"💡 **Análise Estatística:** O perfil de consumo é mais intenso na categoria: **{pior_cat}**.")

                # ANÁLISE 3: Picos
                st.markdown("### 🚨 Detecção de Picos Extremos")
                anomalias, limite, hora_comum = utils.detect_anomalies(df, threshold_factor=5)

                if not anomalias.empty:
                    st.warning(f"Detectamos {len(anomalias)} picos de alto consumo (acima de {limite:.2f} kWh).")
                    
                    st.markdown(f"""
                    **⚠️ Atenção! Picos de Consumo Identificados ⚠️**
                    A análise mostra que a maioria dos picos de desperdício ocorre por volta das **{hora_comum}h:00**.
                    
                    **Ação Recomendada:**
                    1. Verifique quais aparelhos são ligados rotineiramente às **{hora_comum}h**.
                    2. Evite ligar **Chuveiro e Ar Condicionado** simultaneamente neste horário.
                    """)
                    
                    with st.expander("Ver tabela de dados dos picos"):
                        st.dataframe(anomalias[[col_data, col_consumo]])
                else:
                    st.success("✅ O sistema elétrico apresenta comportamento estável.")

    except Exception as e:
        st.error(f"Erro técnico: {e}")