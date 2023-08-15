from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache

import pandas as pd
import numpy as np

from meusgastos.apps.transacoes.models import Transacao
from meusgastos.apps.transacoes.utils import get_transactions_with_items
from meusgastos.apps.core.utils import get_month_name


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
    #           INITIALIZE VARIABLES          #
    # #########################################

    # get parameters from request
    try:
        month_to_check = int(request.GET.get('month'))
        year_to_check = int(request.GET.get('year'))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid parameters'})

    income = 0
    expenses = 0
    balance = 0
    reservas = 0
    gastos_por_categorias = {}
    gastos_por_subcategorias = {}
    income_outcome_growth_data = {}
    month_transactions_list = []
    _is_caching = False

    data = {
        'rendaTotal': income,
        'despesaTotal': expenses,
        'saltoTotal': balance,
        'reservas': reservas,
        'gastosPorCategorias': gastos_por_categorias,
        'gastosPorSubcategorias': gastos_por_subcategorias,
        'income_outcome_growth_data': income_outcome_growth_data,
        'transactions': month_transactions_list,
    }

    # #########################################
    #           CACHE TRANSACTIONS            #
    # #########################################

    # Check if the data is already in cache
    cache_key = f'dashboard_transactions_data_{year_to_check}'
    cached_data = cache.get(cache_key)

    if cached_data is not None and _is_caching is True:
        transactions = cached_data
    else:
        transactions = get_transactions_with_items(year_to_check)
        # Store the data in cache for a certain period of time
        cache.set(cache_key, transactions, timeout=60*5)  # 5 minutes in seconds

    # #########################################
    #          CREATE YEAR DATAFRAME          #
    # #########################################

    # Transform the queryset into a Pandas DataFrame
    year_df = pd.DataFrame(transactions)

    if len(year_df) == 0:
        return JsonResponse(data)

    # Prepare the DataFrame
    year_df['valor'] = year_df['valor'].astype(float)
    year_df['data'] = pd.to_datetime(year_df['data'])
    year_df['dia'] = year_df['data'].dt.day
    year_df['mes'] = year_df['data'].dt.month
    year_df['ano'] = year_df['data'].dt.year

    # Prepara categorias
    year_df['categoria_parent'].replace('', np.nan, inplace=True)
    year_df['categoria'] = year_df.apply(
        lambda row: row['categoria_parent'] if pd.notna(row['categoria_parent']) else row['categoria_descricao'], axis=1
    )
    year_df['subcategoria'] = year_df.apply(
        lambda row: row['categoria_descricao'] if pd.notna(row['categoria_parent']) else '', axis=1
    )
    # remove unnecessary columns
    year_df.drop(['categoria_descricao', 'categoria_parent'], axis=1, inplace=True)

    # Ajuusta valores para transações de saída
    year_df.loc[year_df['tipo'] == Transacao.TYPE_EXPENSE, 'valor'] *= -1

    # #########################################
    #  MONTH DATAFRAME TO BE USED IN GRAPHS   #
    # #########################################

    # Separa os dados do mês que está sendo analisado
    month_df = year_df[year_df['mes'] == month_to_check]

    # Separa os dados de renda e despesas do mês
    month_income_df = month_df[year_df['tipo'] == Transacao.TYPE_INCOME]
    month_expenses_df = month_df[year_df['tipo'] == Transacao.TYPE_EXPENSE]

    # Calculando informações para o mês
    if len(month_income_df) > 0:
        income = month_income_df['valor'].sum()

    if len(month_expenses_df) > 0:
        expenses = month_expenses_df['valor'].sum()

        # Calcular gastos por categoria
        gastos_por_categorias = month_expenses_df.groupby('categoria')['valor'].sum().apply(
            lambda x: round(x, 2)).to_dict()

        # Calcular gastos por subcategoria
        gastos_por_subcategorias = {}
        for (categoria, subcategoria), valor in month_expenses_df.groupby(
                ['categoria', 'subcategoria'])['valor'].sum().items():
            if subcategoria != '':
                if categoria not in gastos_por_subcategorias:
                    gastos_por_subcategorias[categoria] = {}
                gastos_por_subcategorias[categoria][subcategoria] = round(valor, 2)

    # saldo final do mês
    balance = income - expenses

    # prepara o dataframe para ser enviado para o frontend
    month_df.drop(['dia', 'mes', 'ano'], axis=1, inplace=True)
    column_order = ['data', 'tipo', 'descricao', 'categoria', 'subcategoria', 'valor']
    month_df = month_df[column_order]

    month_transactions_list = month_df.to_dict(orient='records')

    # #############################################################
    #         GRÁFICOS ANUAIS
    # #############################################################

    # Agrupar os dados por mês e tipo, e calcular a soma dos valores
    month_grouped_data = year_df.groupby(['mes', 'tipo'])['valor'].sum()

    # Criar o dicionário final
    income_outcome_by_month = {}
    for month in range(1, 13):
        income_outcome_by_month[get_month_name(month)] = {
            'income': month_grouped_data.get((month, Transacao.TYPE_INCOME), None),
            'outcome': month_grouped_data.get((month, Transacao.TYPE_EXPENSE), None)
        }
    income_outcome_growth_data = income_outcome_by_month

    data = {
        'rendaTotal': f"{income:.2f}",
        'despesaTotal': f"{expenses:.2f}",
        'saltoTotal': f"{balance:.2f}",
        'reservas': f"{reservas:.2f}",
        'gastosPorCategorias': gastos_por_categorias,
        'gastosPorSubcategorias': gastos_por_subcategorias,
        'income_outcome_growth_data': income_outcome_growth_data,
        'transactions': month_transactions_list,
    }

    return JsonResponse(data)
