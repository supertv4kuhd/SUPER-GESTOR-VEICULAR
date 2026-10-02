import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path

# ==========================================
# SUPER GESTÃO VEICULAR
# ==========================================

st.set_page_config(
    page_title="Super Gestão Veicular",
    page_icon="🚗",
    layout="wide"
)

DB_PATH = Path(__file__).parent / "gestao_veicular.db"


# ==========================================
# BANCO DE DADOS
# ==========================================

def conectar():
    return sqlite3.connect(DB_PATH)


def iniciar_banco():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS veiculo (
                id INTEGER PRIMARY KEY,
                modelo TEXT,
                ano TEXT,
                valor_compra REAL,
                km_atual INTEGER
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS abastecimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                km INTEGER,
                litros REAL,
                valor REAL,
                combustivel TEXT,
                posto TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                km INTEGER,
                descricao TEXT,
                valor REAL,
                proxima_km INTEGER
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                tipo TEXT,
                categoria TEXT,
                descricao TEXT,
                valor REAL
            )
        """)

        quantidade = conn.execute(
            "SELECT COUNT(*) FROM veiculo"
        ).fetchone()[0]

        if quantidade == 0:
            conn.execute("""
                INSERT INTO veiculo
                (id, modelo, ano, valor_compra, km_atual)
                VALUES (1, ?, ?, ?, ?)
            """, ("Renault Kwid Zen", "2025/2026", 55000, 20000))


def consultar(sql, parametros=()):
    with conectar() as conn:
        return pd.read_sql_query(sql, conn, params=parametros)


def executar(sql, parametros=()):
    with conectar() as conn:
        conn.execute(sql, parametros)


iniciar_banco()


# ==========================================
# CABEÇALHO
# ==========================================

st.title("🚗 SUPER GESTÃO VEICULAR")
st.caption("Controle de veículo, manutenção, combustível e finanças")

st.divider()


# ==========================================
# MENU
# ==========================================

pagina = st.sidebar.radio(
    "MENU PRINCIPAL",
    [
        "📊 Painel",
        "🚘 Meu Veículo",
        "⛽ Abastecimentos",
        "🔧 Manutenções",
        "💰 Receitas e Despesas"
    ]
)


# ==========================================
# PAINEL
# ==========================================

if pagina == "📊 Painel":

    st.header("📊 Painel de Controle")

    veiculo = consultar("SELECT * FROM veiculo LIMIT 1").iloc[0]

    abastecimentos = consultar(
        "SELECT * FROM abastecimentos ORDER BY km"
    )

    manutencoes = consultar(
        "SELECT * FROM manutencoes"
    )

    movimentacoes = consultar(
        "SELECT * FROM movimentacoes"
    )

    total_receitas = 0
    total_despesas = 0

    if not movimentacoes.empty:
        total_receitas = movimentacoes[
            movimentacoes["tipo"] == "Receita"
        ]["valor"].sum()

        total_despesas = movimentacoes[
            movimentacoes["tipo"] == "Despesa"
        ]["valor"].sum()

    total_combustivel = 0
    if not abastecimentos.empty:
        total_combustivel = abastecimentos["valor"].sum()

    total_manutencao = 0
    if not manutencoes.empty:
        total_manutencao = manutencoes["valor"].sum()

    saldo = total_receitas - total_despesas - total_combustivel - total_manutencao

    c1, c2, c3 = st.columns(3)

    c1.metric("Veículo", veiculo["modelo"])
    c2.metric("Quilometragem", f'{int(veiculo["km_atual"]):,} km')
    c3.metric("Valor de compra", f'R$ {veiculo["valor_compra"]:,.2f}')

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("Receitas", f"R$ {total_receitas:,.2f}")
    c2.metric("Despesas registradas", f"R$ {total_despesas:,.2f}")
    c3.metric("Saldo operacional", f"R$ {saldo:,.2f}")

    st.divider()

    c1, c2 = st.columns(2)

    c1.metric("Gastos com combustível", f"R$ {total_combustivel:,.2f}")
    c2.metric("Gastos com manutenção", f"R$ {total_manutencao:,.2f}")

    st.subheader("📈 Últimos abastecimentos")

    if not abastecimentos.empty:
        ultimos = abastecimentos.sort_values(
            "data", ascending=False
        ).head(5)

        st.dataframe(
            ultimos[
                ["data", "km", "litros", "valor", "combustivel"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum abastecimento registrado.")

    st.subheader("🔧 Últimas manutenções")

    if not manutencoes.empty:
        ultimas = manutencoes.sort_values(
            "data", ascending=False
        ).head(5)

        st.dataframe(
            ultimas[
                ["data", "km", "descricao", "valor", "proxima_km"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma manutenção registrada.")


# ==========================================
# MEU VEÍCULO
# ==========================================

elif pagina == "🚘 Meu Veículo":

    st.header("🚘 Cadastro do Veículo")

    veiculo = consultar("SELECT * FROM veiculo LIMIT 1").iloc[0]

    with st.form("form_veiculo"):

        modelo = st.text_input(
            "Modelo",
            value=veiculo["modelo"]
        )

        ano = st.text_input(
            "Ano / Modelo",
            value=veiculo["ano"]
        )

        valor_compra = st.number_input(
            "Valor de compra (R$)",
            min_value=0.0,
            value=float(veiculo["valor_compra"]),
            step=500.0
        )

        km_atual = st.number_input(
            "Quilometragem atual",
            min_value=0,
            value=int(veiculo["km_atual"]),
            step=100
        )

        salvar = st.form_submit_button("💾 Salvar veículo")

        if salvar:
            executar("""
                UPDATE veiculo
                SET modelo = ?, ano = ?, valor_compra = ?, km_atual = ?
                WHERE id = 1
            """, (modelo, ano, valor_compra, km_atual))

            st.success("Dados do veículo salvos!")
            st.rerun()


# ==========================================
# ABASTECIMENTOS
# ==========================================

elif pagina == "⛽ Abastecimentos":

    st.header("⛽ Controle de Abastecimentos")

    with st.form("form_abastecimento"):

        data_abast = st.date_input(
            "Data",
            value=date.today()
        )

        km = st.number_input(
            "Quilometragem",
            min_value=0,
            step=100
        )

        combustivel = st.selectbox(
            "Combustível",
            ["Etanol", "Gasolina", "Diesel", "GNV", "Elétrico"]
        )

        litros = st.number_input(
            "Quantidade (litros ou kWh)",
            min_value=0.0,
            step=1.0
        )

        valor = st.number_input(
            "Valor pago (R$)",
            min_value=0.0,
            step=10.0
        )

        posto = st.text_input("Posto")

        salvar = st.form_submit_button("💾 Registrar abastecimento")

        if salvar:
            if litros <= 0 or valor <= 0:
                st.error("Informe a quantidade e o valor.")
            else:
                executar("""
                    INSERT INTO abastecimentos
                    (data, km, litros, valor, combustivel, posto)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(data_abast),
                    km,
                    litros,
                    valor,
                    combustivel,
                    posto
                ))

                executar("""
                    UPDATE veiculo
                    SET km_atual = MAX(km_atual, ?)
                    WHERE id = 1
                """, (km,))

                st.success("Abastecimento registrado!")
                st.rerun()

    st.divider()

    st.subheader("📋 Histórico")

    dados = consultar("""
        SELECT data, km, combustivel, litros, valor, posto
        FROM abastecimentos
        ORDER BY data DESC, id DESC
    """)

    if not dados.empty:
        dados["Preço por litro/unidade"] = (
            dados["valor"] / dados["litros"]
        ).round(2)

        st.dataframe(
            dados,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📉 Consumo estimado")

        consumo = dados.sort_values("km").copy()
        consumo["km_anterior"] = consumo["km"].shift(1)
        consumo["distancia"] = consumo["km"] - consumo["km_anterior"]
        consumo["consumo_estimado"] = (
            consumo["distancia"] / consumo["litros"]
        )

        consumo_valido = consumo[
            (consumo["distancia"] > 0) &
            (consumo["litros"] > 0)
        ]

        if not consumo_valido.empty:
            ultimo = consumo_valido.iloc[-1]

            st.metric(
                "Consumo estimado do último intervalo",
                f'{ultimo["consumo_estimado"]:.2f} km/L'
            )

            st.caption(
                "Estimativa baseada na quilometragem entre registros "
                "e na quantidade do abastecimento atual. "
                "É mais confiável quando os abastecimentos são feitos "
                "com o tanque sempre completado."
            )
    else:
        st.info("Nenhum abastecimento cadastrado.")


# ==========================================
# MANUTENÇÕES
# ==========================================

elif pagina == "🔧 Manutenções":

    st.header("🔧 Controle de Manutenções")

    with st.form("form_manutencao"):

        data_manut = st.date_input(
            "Data da manutenção",
            value=date.today()
        )

        km = st.number_input(
            "Quilometragem",
            min_value=0,
            step=100
        )

        descricao = st.text_input(
            "Descrição",
            placeholder="Ex.: Revisão de 30.000 km"
        )

        valor = st.number_input(
            "Valor pago (R$)",
            min_value=0.0,
            step=50.0
        )

        proxima_km = st.number_input(
            "Próxima manutenção (km)",
            min_value=0,
            step=1000
        )

        salvar = st.form_submit_button("💾 Registrar manutenção")

        if salvar:
            if not descricao.strip():
                st.error("Informe a descrição da manutenção.")
            else:
                executar("""
                    INSERT INTO manutencoes
                    (data, km, descricao, valor, proxima_km)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(data_manut),
                    km,
                    descricao,
                    valor,
                    proxima_km
                ))

                executar("""
                    UPDATE veiculo
                    SET km_atual = MAX(km_atual, ?)
                    WHERE id = 1
                """, (km,))

                st.success("Manutenção registrada!")
                st.rerun()

    st.divider()

    st.subheader("📋 Histórico de Manutenções")

    dados = consultar("""
        SELECT data, km, descricao, valor, proxima_km
        FROM manutencoes
        ORDER BY data DESC, id DESC
    """)

    if not dados.empty:
        st.dataframe(
            dados,
            use_container_width=True,
            hide_index=True
        )

        veiculo = consultar(
            "SELECT km_atual FROM veiculo LIMIT 1"
        ).iloc[0]

        km_atual = int(veiculo["km_atual"])

        pendentes = dados[
            (dados["proxima_km"] > 0) &
            (dados["proxima_km"] <= km_atual + 2000)
        ]

        if not pendentes.empty:
            st.warning("⚠️ Atenção às próximas manutenções:")

            for _, item in pendentes.iterrows():
                diferenca = int(item["proxima_km"]) - km_atual

                if diferenca <= 0:
                    st.error(
                        f'{item["descricao"]}: revisão prevista para '
                        f'{int(item["proxima_km"]):,} km. '
                        "Quilometragem prevista atingida ou ultrapassada."
                    )
                else:
                    st.info(
                        f'{item["descricao"]}: faltam {diferenca:,} km '
                        "para a manutenção prevista."
                    )
    else:
        st.info("Nenhuma manutenção cadastrada.")


# ==========================================
# RECEITAS E DESPESAS
# ==========================================

elif pagina == "💰 Receitas e Despesas":

    st.header("💰 Controle Financeiro")

    with st.form("form_movimentacao"):

        data_mov = st.date_input(
            "Data",
            value=date.today()
        )

        tipo = st.selectbox(
            "Tipo",
            ["Receita", "Despesa"]
        )

        categoria = st.selectbox(
            "Categoria",
            [
                "Uber",
                "99",
                "InDrive",
                "Combustível",
                "Manutenção",
                "Seguro",
                "IPVA",
                "Licenciamento",
                "Lavagem",
                "Alimentação",
                "Pedágio",
                "Financiamento",
                "Outros"
            ]
        )

        descricao = st.text_input("Descrição")

        valor = st.number_input(
            "Valor (R$)",
            min_value=0.0,
            step=10.0
        )

        salvar = st.form_submit_button("💾 Registrar movimentação")

        if salvar:
            if valor <= 0:
                st.error("Informe um valor maior que zero.")
            else:
                executar("""
                    INSERT INTO movimentacoes
                    (data, tipo, categoria, descricao, valor)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(data_mov),
                    tipo,
                    categoria,
                    descricao,
                    valor
                ))

                st.success(f"{tipo} registrada!")
                st.rerun()

    st.divider()

    st.subheader("📋 Histórico Financeiro")

    dados = consultar("""
        SELECT data, tipo, categoria, descricao, valor
        FROM movimentacoes
        ORDER BY data DESC, id DESC
    """)

    if not dados.empty:
        receitas = dados[
            dados["tipo"] == "Receita"
        ]["valor"].sum()

        despesas = dados[
            dados["tipo"] == "Despesa"
        ]["valor"].sum()

        c1, c2, c3 = st.columns(3)

        c1.metric("Receitas", f"R$ {receitas:,.2f}")
        c2.metric("Despesas", f"R$ {despesas:,.2f}")
        c3.metric("Saldo", f"R$ {receitas - despesas:,.2f}")

        st.dataframe(
            dados,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma movimentação registrada.")


# ==========================================
# RODAPÉ
# ==========================================

st.divider()

st.caption(
    "SUPER GESTÃO VEICULAR | Controle inteligente do seu veículo"
)
