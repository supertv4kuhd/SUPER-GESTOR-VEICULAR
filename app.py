import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supergestor Veicular", page_icon="🚘", layout="wide")

st.title("🚘 Supergestor Veicular")
st.caption("Gestão financeira e operacional para motorista de aplicativo")

# Cadastro inicial editável
with st.sidebar:
    st.header("Veículo e operação")
    veiculo = st.text_input("Veículo", "BYD Dolphin GS")
    valor_compra = st.number_input("Valor de compra (R$)", min_value=0.0, value=139990.0, step=1000.0)
    km_atual = st.number_input("Quilometragem atual (km)", min_value=0, value=0, step=100)
    parcelas = st.number_input("Quantidade de parcelas", min_value=0, value=60, step=1)
    valor_parcela = st.number_input("Valor da parcela (R$)", min_value=0.0, value=3250.0, step=50.0)
    total_parcelas = parcelas * valor_parcela
    diferenca_financiamento = total_parcelas - valor_compra
    st.caption(f"Total das parcelas: R$ {total_parcelas:,.2f}")
    st.caption(f"Diferença sobre o preço à vista: R$ {diferenca_financiamento:,.2f}")
    km_dia = st.number_input("KM total por dia", min_value=0.0, value=250.0, step=10.0)
    dias_mes = st.number_input("Dias trabalhados por mês", min_value=0, max_value=31, value=26, step=1)
    horas_dia = st.number_input("Horas trabalhadas por dia", min_value=0.0, value=10.0, step=0.5)

st.info("Preencha os campos por seção. Os valores ficam disponíveis durante esta sessão; para persistência permanente, será necessário conectar um banco de dados.")

tabs = st.tabs([
    "1. Motorista", "2. Combustível", "3. Depreciação", "4. Preventiva",
    "5. Corretiva", "6. Documentação", "7. Seguros", "8. Operacionais",
    "9. Alimentação", "10. KM e tempo", "11. Financeiro", "12. Reservas",
    "13. Preço das corridas", "📊 Resumo"
])

def money_input(label, key, value=0.0, help_text=None):
    return st.number_input(label, min_value=0.0, value=float(value), step=10.0, key=key, help=help_text)

def checklist_costs(items, prefix):
    st.caption("Informe o custo mensal estimado de cada item (R$). Use zero quando não se aplicar.")
    vals = {}
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            vals[item] = st.number_input(f"{item} (R$/mês)", min_value=0.0, value=0.0, step=10.0, key=f"{prefix}_{i}")
    return vals

# 1
with tabs[0]:
    st.subheader("Remuneração do motorista")
    pro_labore = money_input("Pró-labore mensal desejado (R$)", "prolabore", 3000)
    c1, c2, c3 = st.columns(3)
    with c1: meta_dia = money_input("Meta de ganho diário (R$)", "meta_dia")
    with c2: meta_semana = money_input("Meta de ganho semanal (R$)", "meta_semana")
    with c3: meta_mes = money_input("Meta de ganho mensal (R$)", "meta_mes")
    dias_semana = st.number_input("Dias trabalhados por semana", 0, 7, 6, key="dias_sem")
    descanso = st.number_input("Dias de descanso por semana", 0, 7, 1, key="descanso")
    ferias = money_input("Reserva mensal para férias (R$)", "ferias")
    decimo = money_input("Reserva mensal para 13º (R$)", "decimo")
    parada = money_input("Reserva para períodos sem trabalhar (R$/mês)", "parada")
    doenca = money_input("Reserva doença/imprevistos pessoais (R$/mês)", "doenca")

# 2
with tabs[1]:
    st.subheader("Combustível")
    tipo_comb = st.selectbox("Combustível", ["Energia elétrica", "Gasolina", "Etanol", "Diesel", "Híbrido / outro"], key="comb_tipo")
    preco_litro = money_input("Preço do litro ou kWh (R$)", "comb_preco")
    consumo = st.number_input("Consumo médio (km/l ou km/kWh)", min_value=0.0, value=0.0, step=0.5, key="consumo")
    km_mes_comb = st.number_input("Quilometragem mensal total (km)", min_value=0.0, value=float(km_dia*dias_mes), step=100.0, key="km_mes_comb")
    perc_extra = st.slider("Percentual adicional estimado (trânsito, ar-condicionado, deslocamentos vazios)", 0, 100, 15, key="perc_extra")
    combustivel_mes = (km_mes_comb / consumo * preco_litro * (1 + perc_extra/100)) if consumo > 0 else 0.0
    st.metric("Estimativa mensal de energia/combustível", f"R$ {combustivel_mes:,.2f}")

# 3
with tabs[2]:
    st.subheader("Depreciação")
    valor_mercado = money_input("Valor atual de mercado (R$)", "valor_mercado", valor_compra)
    anos_uso = st.number_input("Anos previstos até a venda", min_value=1, value=5, key="anos_uso")
    valor_venda = money_input("Valor estimado na venda (R$)", "valor_venda")
    custo_oportunidade = money_input("Custo de oportunidade mensal do capital (R$)", "oportunidade")
    km_venda = st.number_input("Quilometragem prevista para venda (km)", min_value=0, value=150000, step=5000, key="km_venda")
    depreciacao_mensal = max(valor_mercado - valor_venda, 0) / (anos_uso*12)
    st.metric("Depreciação mensal estimada", f"R$ {depreciacao_mensal:,.2f}")

# 4 & 5
preventiva_items = ["Óleo do motor", "Filtro de óleo", "Filtro de ar", "Filtro de combustível", "Filtro de cabine", "Velas", "Correias", "Fluido de freio", "Arrefecimento", "Revisões", "Alinhamento", "Balanceamento", "Rodízio de pneus", "Limpeza do sistema"]
corretiva_items = ["Pneus", "Pastilhas de freio", "Discos de freio", "Bateria", "Suspensão", "Amortecedores", "Buchas", "Pivôs", "Terminais de direção", "Embreagem (se aplicável)", "Transmissão", "Alternador", "Motor de partida", "Sistema elétrico", "Ar-condicionado", "Reparos inesperados", "Emergência mecânica"]
with tabs[3]:
    st.subheader("Manutenção preventiva")
    preventiva = checklist_costs(preventiva_items, "prev")
with tabs[4]:
    st.subheader("Manutenção corretiva e desgaste")
    corretiva = checklist_costs(corretiva_items, "corr")

# 6
with tabs[5]:
    st.subheader("Documentação e impostos")
    documentacao = checklist_costs(["IPVA", "Licenciamento/CRLV", "Taxas obrigatórias", "Vistorias", "Impostos da atividade", "Contabilidade", "MEI/enquadramento", "Taxas municipais"], "doc")
# 7
with tabs[6]:
    st.subheader("Seguros e proteção")
    seguros = checklist_costs(["Seguro do veículo", "Cobertura para aplicativo", "Roubo/furto", "Colisão", "Terceiros", "Reserva para franquia", "Acidentes pessoais", "Veículo parado", "Reserva para sinistro"], "seg")
# 8
with tabs[7]:
    st.subheader("Despesas operacionais")
    taxa_app = money_input("Taxa diária do aplicativo (R$)", "taxa_app", 58)
    comissao = money_input("Comissão/taxas da plataforma (R$/mês)", "comissao")
    operacionais = checklist_costs(["Pedágios não reembolsados", "Estacionamento", "Lavagem", "Higienização", "Produtos de limpeza", "Internet móvel", "Plano de celular", "Suporte para celular", "Carregador veicular", "Acessórios", "Despachante"], "op")
# 9
with tabs[8]:
    st.subheader("Alimentação e despesas durante o trabalho")
    alimentacao = checklist_costs(["Café da manhã", "Almoço", "Jantar", "Lanches", "Água", "Café", "Banheiro/apoio", "Outras despesas"], "alim")
# 10
with tabs[9]:
    st.subheader("Quilometragem e tempo")
    km_passageiro = st.number_input("KM com passageiros por mês", min_value=0.0, value=0.0, key="km_pass")
    km_vazio = st.number_input("KM sem passageiros / deslocamento / busca por chamadas", min_value=0.0, value=0.0, key="km_vazio")
    tempo_espera = st.number_input("Horas mensais aguardando chamadas/passageiros", min_value=0.0, value=0.0, key="espera")
    tempo_transporte = st.number_input("Horas mensais efetivamente transportando passageiros", min_value=0.0, value=0.0, key="transporte")
    tempo_conectado = st.number_input("Horas mensais conectado ao app", min_value=0.0, value=float(horas_dia*dias_mes), key="conectado")
    km_total_real = km_passageiro + km_vazio
    st.metric("KM mensal total informado", f"{km_total_real:,.0f} km")
# 11
with tabs[10]:
    st.subheader("Custos financeiros")
    juros = money_input("Juros mensais do financiamento (R$)", "juros")
    parcela_fin = money_input("Parcela mensal do veículo (R$)", "parcela_fin", valor_parcela)
    st.caption(f"Financiamento informado: {parcelas} parcelas de R$ {valor_parcela:,.2f} = R$ {total_parcelas:,.2f} no total.")
    st.caption(f"Preço à vista: R$ {valor_compra:,.2f}. Diferença bruta: R$ {diferenca_financiamento:,.2f}. Essa diferença pode incluir juros, entrada, tarifas, seguros ou outros encargos; confirme o contrato.")
    emprestimos = money_input("Juros de empréstimos (R$/mês)", "emprestimos")
    tarifas = money_input("Tarifas bancárias (R$/mês)", "tarifas")
    antecipacao = money_input("Antecipação de recebíveis (R$/mês)", "antecipacao")
    capital = money_input("Custo do capital investido (R$/mês)", "capital")
# 12
with tabs[11]:
    st.subheader("Lucro e reservas")
    reservas = checklist_costs(["Manutenção", "Pneus", "Documentação", "Seguro", "Depreciação", "Imprevistos", "Troca do veículo"], "res")
    lucro_desejado = money_input("Lucro líquido desejado (R$/mês)", "lucro_desejado")
    margem = st.slider("Margem de segurança (%)", 0, 50, 10, key="margem")

# 13
with tabs[12]:
    st.subheader("Formação do preço das corridas")
    faturamento = money_input("Faturamento bruto mensal esperado (R$)", "faturamento")
    corridas_mes = st.number_input("Quantidade estimada de corridas por mês", min_value=0, value=0, step=10, key="corridas")
    km_corridas = st.number_input("KM total mensal do veículo (incluindo KM vazio)", min_value=0.0, value=float(km_dia*dias_mes), step=100.0, key="km_preco")
    horas_mes_preco = st.number_input("Horas mensais de trabalho", min_value=0.0, value=float(horas_dia*dias_mes), key="horas_preco")

# Totais e resumo
prev_total = sum(preventiva.values()) if "preventiva" in locals() else 0
corr_total = sum(corretiva.values()) if "corretiva" in locals() else 0
doc_total = sum(documentacao.values()) if "documentacao" in locals() else 0
seg_total = sum(seguros.values()) if "seguros" in locals() else 0
op_total = sum(operacionais.values()) if "operacionais" in locals() else 0
alim_total = sum(alimentacao.values()) if "alimentacao" in locals() else 0
res_total = sum(reservas.values()) if "reservas" in locals() else 0

# Recalcular custos de categorias usando session_state para funcionar mesmo quando as abas não estão abertas
def sum_keys(prefix, count):
    return sum(float(st.session_state.get(f"{prefix}_{i}", 0.0)) for i in range(count))

custos_manut = sum_keys("prev", len(preventiva_items)) + sum_keys("corr", len(corretiva_items))
custos_doc = sum_keys("doc", 8)
custos_seg = sum_keys("seg", 9)
custos_op = sum_keys("op", 11)
custos_alim = sum_keys("alim", 8)
custos_res = sum_keys("res", 7)
custos_motorista = pro_labore + ferias + decimo + parada + doenca
custos_financeiros = float(st.session_state.get("juros",0)) + float(st.session_state.get("parcela_fin",valor_parcela)) + float(st.session_state.get("emprestimos",0)) + float(st.session_state.get("tarifas",0)) + float(st.session_state.get("antecipacao",0)) + float(st.session_state.get("capital",0))
custos_operacao = combustivel_mes + custos_motorista + depreciacao_mensal + custos_manut + custos_doc + custos_seg + custos_op + custos_alim + custos_financeiros + taxa_app*dias_mes + comissao + custos_res
custo_km = custos_operacao/km_corridas if 'km_corridas' in locals() and km_corridas > 0 else 0
custo_hora = custos_operacao/horas_mes_preco if 'horas_mes_preco' in locals() and horas_mes_preco > 0 else 0
preco_minimo_km = custo_km*(1+margem/100)
lucro_estimado = faturamento-custos_operacao if 'faturamento' in locals() else 0
with tabs[13]:
    st.subheader("Resumo financeiro")
    a,b,c,d = st.columns(4)
    a.metric("Custo mensal estimado", f"R$ {custos_operacao:,.2f}")
    b.metric("Custo por KM total", f"R$ {custo_km:,.2f}/km")
    c.metric("Custo por hora", f"R$ {custo_hora:,.2f}/h")
    d.metric("Lucro estimado", f"R$ {lucro_estimado:,.2f}")
    st.metric("Preço mínimo por KM com margem de segurança", f"R$ {preco_minimo_km:,.2f}/km")
    st.caption("Atenção: este é um modelo inicial. Para análise correta, separar principal e juros do financiamento, evitar contar a mesma reserva duas vezes e adaptar combustível/energia ao veículo elétrico.")
    resumo = pd.DataFrame([
        ["Remuneração e reservas pessoais", custos_motorista],
        ["Energia/combustível", combustivel_mes],
        ["Depreciação estimada", depreciacao_mensal],
        ["Manutenção", custos_manut],
        ["Documentação", custos_doc],
        ["Seguros", custos_seg],
        ["Despesas operacionais", custos_op + taxa_app*dias_mes + comissao],
        ["Alimentação", custos_alim],
        ["Financeiro (inclui parcela informada)", custos_financeiros],
        ["Reservas adicionais", custos_res],
    ], columns=["Categoria", "Valor mensal (R$)"])
    st.dataframe(resumo, use_container_width=True, hide_index=True)
    st.download_button("Baixar resumo CSV", resumo.to_csv(index=False).encode("utf-8-sig"), "supergestor_resumo.csv", "text/csv")

st.divider()
st.caption("Supergestor Veicular • versão inicial editável")
