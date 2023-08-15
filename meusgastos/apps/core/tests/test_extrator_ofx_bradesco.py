import pytest
from django.db.models import Sum

from meusgastos.apps.transacoes.models import Transacao
from conftest import setup_test_data


@pytest.mark.django_db
def test_extrator_ofx_bradesco(setup_test_data):
    # Verifique se as transações foram inseridas corretamente no banco de dados
    transacoes = Transacao.objects.all().order_by('data')
    assert len(transacoes) == 100  # Verifica se o número de transações é o esperado

    # Transações ignoradas
    assert transacoes.filter(status=Transacao.STATUS_IGNORED).count() == 5

    # Transações de entrada de salário
    assert transacoes.filter(tipo=Transacao.TYPE_INCOME).count() == 14

    # Transações de despesas
    assert transacoes.filter(tipo=Transacao.TYPE_EXPENSE).count() == 86

    # ############################
    # Transações de Janeiro
    # ############################
    assert transacoes.filter(data__month=1).count() == 10
    # Ignoradas
    assert transacoes.filter(data__month=1, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Janeiro
    janeiro_soma_renda = transacoes.filter(
        data__month=1, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert janeiro_soma_renda == 5000
    # Despesas de Janeiro
    janeiro_soma_despesas = transacoes.filter(
        data__month=1, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert janeiro_soma_despesas == -5000

    # ############################
    # Transações de Fevereiro
    # ############################
    assert transacoes.filter(data__month=2).count() == 8
    # Ignoradas
    assert transacoes.filter(data__month=2, status=Transacao.STATUS_IGNORED).count() == 1

    # Renda de Fevereiro
    fevereiro_soma_renda = transacoes.filter(
        data__month=2, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert fevereiro_soma_renda == 5000
    # Despesas de Fevereiro
    fevereiro_soma_despesas = transacoes.filter(
        data__month=2, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert fevereiro_soma_despesas == -4920

    # ############################
    # Transações de Março
    # ############################
    assert transacoes.filter(data__month=3).count() == 9
    # Ignoradas
    assert transacoes.filter(data__month=3, status=Transacao.STATUS_IGNORED).count() == 1

    # Renda de Março
    marco_soma_renda = transacoes.filter(
        data__month=3, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert marco_soma_renda == 5000
    # Despesas de Março
    marco_soma_despesas = transacoes.filter(
        data__month=3, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert marco_soma_despesas == -5120

    # ############################
    # Transações de Abril
    # ############################
    assert transacoes.filter(data__month=4).count() == 8
    # Ignoradas
    assert transacoes.filter(data__month=4, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Abril
    abril_soma_renda = transacoes.filter(
        data__month=4, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert abril_soma_renda == 5000
    # Despesas de Abril
    abril_soma_despesas = transacoes.filter(
        data__month=4, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert abril_soma_despesas == -4960

    # ############################
    # Transações de Maio
    # ############################
    assert transacoes.filter(data__month=5).count() == 10
    # Ignoradas
    assert transacoes.filter(data__month=5, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Maio
    maio_soma_renda = transacoes.filter(
        data__month=5, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert maio_soma_renda == 5000
    # Despesas de Maio
    maio_soma_despesas = transacoes.filter(
        data__month=5, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert maio_soma_despesas == -5000

    # ############################
    # Transações de Junho
    # ############################
    assert transacoes.filter(data__month=6).count() == 7
    # Ignoradas
    assert transacoes.filter(data__month=6, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Junho
    junho_soma_renda = transacoes.filter(
        data__month=6, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert junho_soma_renda == 5000
    # Despesas de Junho
    junho_soma_despesas = transacoes.filter(
        data__month=6, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert junho_soma_despesas == -5000

    # ############################
    # Transações de Julho
    # ############################
    assert transacoes.filter(data__month=7).count() == 8
    # Ignoradas
    assert transacoes.filter(data__month=7, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Julho
    julho_soma_renda = transacoes.filter(
        data__month=7, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert julho_soma_renda == 5000
    # Despesas de Julho
    julho_soma_despesas = transacoes.filter(
        data__month=7, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert julho_soma_despesas == -5100

    # ############################
    # Transações de Agosto
    # ############################
    assert transacoes.filter(data__month=8).count() == 7
    # Ignoradas
    assert transacoes.filter(data__month=8, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Agosto
    agosto_soma_renda = transacoes.filter(
        data__month=8, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert agosto_soma_renda == 5000
    # Despesas de Agosto
    agosto_soma_despesas = transacoes.filter(
        data__month=8, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert agosto_soma_despesas == -4900

    # ############################
    # Transações de Setembro
    # ############################
    assert transacoes.filter(data__month=9).count() == 8
    # Ignoradas
    assert transacoes.filter(data__month=9, status=Transacao.STATUS_IGNORED).count() == 1

    # Renda de Setembro
    setembro_soma_renda = transacoes.filter(
        data__month=9, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert setembro_soma_renda == 5000
    # Despesas de Setembro
    setembro_soma_despesas = transacoes.filter(
        data__month=9, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert setembro_soma_despesas == -4900

    # ############################
    # Transações de Outubro
    # ############################
    assert transacoes.filter(data__month=10).count() == 7
    # Ignoradas
    assert transacoes.filter(data__month=10, status=Transacao.STATUS_IGNORED).count() == 0

    # Renda de Outubro
    outubro_soma_renda = transacoes.filter(
        data__month=10, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert outubro_soma_renda == 5000
    # Despesas de Outubro
    outubro_soma_despesas = transacoes.filter(
        data__month=10, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert outubro_soma_despesas == -5000

    # ############################
    # Transações de Novembro
    # ############################
    assert transacoes.filter(data__month=11).count() == 8
    # Ignoradas
    assert transacoes.filter(data__month=11, status=Transacao.STATUS_IGNORED).count() == 1

    # Renda de Novembro
    novembro_soma_renda = transacoes.filter(
        data__month=11, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert novembro_soma_renda == 5000
    # Despesas de Novembro
    novembro_soma_despesas = transacoes.filter(
        data__month=11, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert novembro_soma_despesas == -4900

    # ############################
    # Transações de Dezembro
    # ############################
    assert transacoes.filter(data__month=12).count() == 10
    # Ignoradas
    assert transacoes.filter(data__month=12, status=Transacao.STATUS_IGNORED).count() == 1

    # Renda de Dezembro
    dezembro_soma_renda = transacoes.filter(
        data__month=12, tipo=Transacao.TYPE_INCOME, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert dezembro_soma_renda == 5000
    # Despesas de Dezembro
    dezembro_soma_despesas = transacoes.filter(
        data__month=12, tipo=Transacao.TYPE_EXPENSE, status=Transacao.STATUS_ACTIVE
    ).aggregate(total=Sum('valor'))['total']
    assert dezembro_soma_despesas == -5200
