from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache

import pandas as pd
import numpy as np
from datetime import date, datetime
from decimal import Decimal

from meusgastos.apps.transacoes.models import Transacao, Planejamento
from meusgastos.apps.transacoes.utils import (
    get_transactions_with_items,
    get_balance_at_given_date,
    get_future_transactions
)
from meusgastos.apps.core.utils import mes_em_portugues


def dashboard_view(request):
    context = {}

    return render(request, 'core/dashboard.html', context)


def dashboard_data_view(request):
    """
    Get the data for the dashboard
    :param request:
    :return:
    """

    # #########################################
    #           INICIALIZA VARIAVEIS          #
    # #########################################

    # get parameters from request
    try:
        mes_analisado = int(request.GET.get('month'))
        ano_analisado = int(request.GET.get('year'))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid parameters'})

    hoje_datetime = datetime.today()
    inicio_do_mes_atual = date(hoje_datetime.year, hoje_datetime.month, 1)
    mes_datetime = datetime(ano_analisado, mes_analisado, 1)
    receitas = 0.0
    despesas = 0.0
    saldo_do_mes = 0.0
    reservas = 0.0
    credito = 0.0
    debito = 0.0
    despesas_por_categorias = {}
    despesas_por_subcategorias = {}
    grafico_crescimento_receitas_despesas = {}
    grafico_despesas_futuras = {}
    media_3_meses_despesas_por_categoria = {}
    lista_transacoes_do_mes = []
    _is_caching = False

    data = {
        'receitas': f"{receitas:.2f}",
        'despesas': f"{despesas:.2f}",
        'saldoMes': f"{saldo_do_mes:.2f}",
        'reservas': f"{reservas:.2f}",
        'despesasPorCategorias': despesas_por_categorias,
        'despesasPorSubcategorias': despesas_por_subcategorias,
        'crescimentoReceitasDespesas': grafico_crescimento_receitas_despesas,
        'despesasFuturas': grafico_despesas_futuras,
        'mediaGastosCategorias': media_3_meses_despesas_por_categoria,
        'transacoes': lista_transacoes_do_mes,
    }

    # #########################################
    #             CACHE TRANSAÇÕES            #
    # #########################################

    # Check if the data is already in cache
    cache_key = f'dashboard_transactions_data_{ano_analisado}'
    cached_data = cache.get(cache_key)

    if cached_data is not None and _is_caching is True:
        transactions = cached_data
    else:
        transactions = get_transactions_with_items(ano_analisado)
        # Store the data in cache for a certain period of time
        cache.set(cache_key, transactions, timeout=60 * 5)  # 5 minutes in seconds

    # #########################################
    #          CALCULA O SALDO INICIAL        #
    # #########################################

    # Current year start balance
    saldo_inicial_ano = get_balance_at_given_date(date(ano_analisado, 1, 1))

    # last month balance
    ultimo_mes_dt = date(ano_analisado, mes_analisado, 1)
    saldo_do_mes_anterior = float(get_balance_at_given_date(ultimo_mes_dt))
    if saldo_do_mes_anterior:
        if saldo_do_mes_anterior > 0:
            credito = saldo_do_mes_anterior
        elif saldo_do_mes_anterior < 0:
            debito = saldo_do_mes_anterior * -1

    # ######################################### #
    #  DATAFRAME COM OS DADOS DO ANO ANALISADO  #
    # ######################################### #

    # Transform the queryset into a Pandas DataFrame
    ano_df = pd.DataFrame(transactions)

    if len(ano_df) == 0:
        return JsonResponse(data)

    ano_df = prepare_transactions_dataframe(ano_df)

    # ######################################### #
    #  DATAFRAME COM OS DADOS DO MÊS ANALISADO  #
    # ######################################### #

    # Separa os dados do mês que está sendo analisado
    mes_df = ano_df[ano_df['mes'] == mes_analisado]

    # Separa os dados de renda e despesas do mês
    mes_receitas_df = mes_df[mes_df['tipo'] == Transacao.TYPE_INCOME]
    mes_despesas_df = mes_df[mes_df['tipo'] == Transacao.TYPE_EXPENSE]

    # Calculando informações para o mês
    if len(mes_receitas_df) > 0:
        receitas = mes_receitas_df['valor'].sum()

    if len(mes_despesas_df) > 0:
        despesas = mes_despesas_df['valor'].sum()

        # Calcular gastos por categoria
        despesas_por_categorias = mes_despesas_df.groupby('categoria')['valor'].sum().apply(
            lambda x: round(x, 2)).to_dict()

        # Calcular gastos por subcategoria
        despesas_por_subcategorias = {}
        for (categoria, subcategoria), valor in mes_despesas_df.groupby(
                ['categoria', 'subcategoria'])['valor'].sum().items():
            if subcategoria != '':
                if categoria not in despesas_por_subcategorias:
                    despesas_por_subcategorias[categoria] = {}
                despesas_por_subcategorias[categoria][subcategoria] = round(valor, 2)

    # prepara o dataframe para ser enviado para o frontend
    mes_df = mes_df.drop(['dia', 'mes', 'ano'], axis=1)
    ordem_colunas = ['data', 'tipo', 'descricao', 'categoria', 'subcategoria', 'valor']
    mes_df = mes_df[ordem_colunas]

    lista_transacoes_do_mes = mes_df.to_dict(orient='records')
    lista_adicao_transacoes = []

    if saldo_do_mes_anterior > 0:
        lista_adicao_transacoes = [
            {'data': mes_datetime,
             'tipo': 'E',
             'descricao': 'Ajuste de crédito mês anterior',
             'categoria': 'Ajuste',
             'subcategoria': '',
             'valor': saldo_do_mes_anterior}
        ]
        receitas += saldo_do_mes_anterior
    elif saldo_do_mes_anterior < 0:
        lista_adicao_transacoes = [
            {'data': mes_datetime,
             'tipo': 'S',
             'descricao': 'Ajuste de débito mês anterior',
             'categoria': 'Ajuste',
             'subcategoria': '',
             'valor': saldo_do_mes_anterior}
        ]
        despesas += abs(saldo_do_mes_anterior)

    # SALDO FINAL DO MÊS ANALISADO
    saldo_do_mes = receitas - despesas

    # ######################################### #
    #          TRANSAÇÕES FUTURAS               #
    # ######################################### #

    transacoes_futuras = get_future_transactions()
    transacoes_futuras_df = pd.DataFrame(transacoes_futuras)

    if len(transacoes_futuras_df) == 0:
        lista_transacoes_futuras_do_mes = []
    else:
        transacoes_futuras_df = prepare_transactions_dataframe(transacoes_futuras_df)
        transacoes_futuras_do_mes_df = transacoes_futuras_df[transacoes_futuras_df['mes'] == mes_analisado]
        transacoes_futuras_agrupado_mes = transacoes_futuras_df.groupby(['mes'])['valor'].sum().to_dict()

        lista_transacoes_futuras_do_mes = transacoes_futuras_do_mes_df.to_dict(orient='records')

    if lista_adicao_transacoes:
        lista_transacoes_do_mes = lista_adicao_transacoes + lista_transacoes_do_mes

    if lista_transacoes_futuras_do_mes:
        lista_transacoes_do_mes = lista_transacoes_do_mes + lista_transacoes_futuras_do_mes

        planejamento = Planejamento.gerar_lista_planejamento_anual(datetime.today().date())

        for _mes in range(hoje_datetime.month + 1, 13):
            despesas_planejadas_mes = planejamento[mes_em_portugues(_mes)]['total'] or Decimal('0.00')
            grafico_despesas_futuras[mes_em_portugues(_mes)] = {
                'comprasParceladas': f"{Decimal(transacoes_futuras_agrupado_mes.get(_mes, Decimal('0.00')))}",
                'despesasPlanejadas': f"{despesas_planejadas_mes}"
            }

    # ######################################### #
    #              GRÁFICOS ANUAIS              #
    # ######################################### #

    # Agrupa os dados por mês e tipo, e calcula a soma dos valores
    soma_mensal_transacoes = ano_df.groupby(['mes', 'tipo'])['valor'].sum()

    # Criar o dicionário final
    grafico_crescimento_receitas_despesas = {}
    saldo_do_ano = None
    for _mes in range(1, 13):
        if saldo_do_ano is None:
            saldo_do_ano = saldo_inicial_ano

        credito = saldo_do_ano if saldo_do_ano > 0 else Decimal('0.00')
        debito = abs(saldo_do_ano) if saldo_do_ano < 0 else Decimal('0.00')

        receitas_mes = Decimal(soma_mensal_transacoes.get((_mes, Transacao.TYPE_INCOME), Decimal('0.00')))
        despesas_mes = Decimal(soma_mensal_transacoes.get((_mes, Transacao.TYPE_EXPENSE), Decimal('0.00')))

        # verifica se o mês sendo analisado passou do mês atual
        if _mes > hoje_datetime.month:
            receitas_mes = Decimal('0.00')
            despesas_mes = Decimal('0.00')
            credito = Decimal('0.00')
            debito = Decimal('0.00')

        grafico_crescimento_receitas_despesas[mes_em_portugues(_mes)] = {
            'receitas': f"{receitas_mes:.2f}",
            'despesas': f"{despesas_mes:.2f}",
            'credito': f"{credito:.2f}",
            'debito': f"{debito:.2f}"
        }

        saldo_atual = receitas_mes - abs(despesas_mes)
        saldo_do_ano += Decimal(saldo_atual)

    # ######################################### #
    #  MÉDIA DOS ÚLTIMOS 3 MESES POR CATEGORIA  #
    # ######################################### #

    ano_df['data'] = pd.to_datetime(ano_df['data'])

    # Calcula o período de três meses atrás a partir da data máxima
    tres_meses_atras = ano_df['data'].max() - pd.DateOffset(months=3)

    # Filtra o DataFrame para os últimos três meses
    ultimos_3_meses_df = ano_df[ano_df['data'] >= tres_meses_atras]
    ultimos_3_meses_df = ultimos_3_meses_df[ultimos_3_meses_df['tipo'] == Transacao.TYPE_EXPENSE]
    ultimos_3_meses_df = ultimos_3_meses_df[ultimos_3_meses_df['categoria'] != 'Não categorizado']

    # Cria uma tabela pivô preenchendo os valores ausentes com zero
    tabela_pivot = ultimos_3_meses_df.pivot_table(index='categoria',
                                                  columns='mes',
                                                  values='valor',
                                                  aggfunc='sum',
                                                  fill_value=0)

    media_despesas_por_categoria = tabela_pivot.mean(axis=1)

    media_despesas_por_categoria.rename('media_gastos', inplace=True)

    # Converte a série em um DataFrame
    media_despesas_por_categoria = media_despesas_por_categoria.reset_index()

    # Ordena o DataFrame pela coluna 'media_gastos' em ordem decrescente
    media_despesas_por_categoria = media_despesas_por_categoria.sort_values(by='media_gastos', ascending=False)

    # Reseta o índice
    media_despesas_por_categoria.reset_index(inplace=True)

    # Formata a coluna 'media_gastos' para duas casas decimais
    media_despesas_por_categoria['media_gastos'] = media_despesas_por_categoria['media_gastos'].apply(
        lambda x: '{:.2f}'.format(x))

    # Cria uma lista de dicionários a partir do DataFrame
    media_despesas_por_categoria_list = media_despesas_por_categoria.head(7).to_dict(orient='records')
    # Transforma a lista de dicionários em uma lista de tuplas (nome da categoria, média de gastos)
    media_3_meses_despesas_por_categoria = {entry['categoria']: entry['media_gastos'] for entry in
                                            media_despesas_por_categoria_list}

    data = {
        'receitas': f"{receitas:.2f}",
        'despesas': f"{despesas:.2f}",
        'saldoTotal': f"{saldo_do_mes:.2f}",
        'saldoMesAnterior': f"{saldo_do_mes_anterior:.2f}",
        'reservas': f"{reservas:.2f}",
        'despesasPorCategorias': despesas_por_categorias,
        'despesasPorSubcategorias': despesas_por_subcategorias,
        'crescimentoReceitasDespesas': grafico_crescimento_receitas_despesas,
        'despesasFuturas': grafico_despesas_futuras,
        'mediaGastosCategorias': media_3_meses_despesas_por_categoria,
        'transacoes': lista_transacoes_do_mes,
    }

    return JsonResponse(data)


def prepare_transactions_dataframe(dataframe):
    # Prepare the DataFrame
    dataframe['valor'] = dataframe['valor'].astype(float)
    dataframe['data'] = pd.to_datetime(dataframe['data'])
    dataframe['dia'] = dataframe['data'].dt.day
    dataframe['mes'] = dataframe['data'].dt.month
    dataframe['ano'] = dataframe['data'].dt.year
    # Prepara categorias
    dataframe['categoria_parent'].replace('', np.nan, inplace=True)
    dataframe['categoria'] = dataframe.apply(
        lambda row: row['categoria_parent'] if pd.notna(row['categoria_parent']) else row['categoria_descricao'], axis=1
    )
    dataframe['subcategoria'] = dataframe.apply(
        lambda row: row['categoria_descricao'] if pd.notna(row['categoria_parent']) else '', axis=1
    )
    # remove unnecessary columns
    dataframe.drop(['categoria_descricao', 'categoria_parent'], axis=1, inplace=True)
    # Ajusta valores para transações de saída
    dataframe.loc[dataframe['tipo'] == Transacao.TYPE_EXPENSE, 'valor'] *= -1

    return dataframe
