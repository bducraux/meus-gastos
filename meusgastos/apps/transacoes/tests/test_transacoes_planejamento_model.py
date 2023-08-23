import pytest
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from meusgastos.apps.transacoes.models import Planejamento
from meusgastos.apps.categorias.models import Categoria


@pytest.fixture
def create_planejamento():
    def _create_planejamento(**kwargs):
        return Planejamento.objects.create(**kwargs)

    return _create_planejamento


@pytest.mark.django_db
def test_get_planejamentos_ativos_do_mes(create_planejamento):
    active_planejamento = create_planejamento(
        mes=date(2023, 8, 1),
        valor=Decimal('100.00'),
        repeticoes=0,
        categoria=Categoria.objects.create(
            cod='CAT',
            tipo='E',
            descricao='Test Category'
        ),
        status=Planejamento.STATUS_ACTIVE
    )

    inactive_planejamento = create_planejamento(
        mes=date(2023, 7, 1),
        valor=Decimal('150.00'),
        repeticoes=0,
        categoria=Categoria.objects.create(
            cod='CAT',
            tipo='E',
            descricao='Test Category'
        ),
        status=Planejamento.STATUS_INACTIVE
    )

    future_planejamento = create_planejamento(
        mes=date(2023, 9, 1),
        valor=Decimal('200.00'),
        repeticoes=3,
        categoria=Categoria.objects.create(
            cod='CAT',
            tipo='E',
            descricao='Test Category'
        ),
        status=Planejamento.STATUS_ACTIVE
    )

    active_planejamentos = Planejamento.get_planejamentos_ativos_do_mes(date(2023, 8, 1))

    assert active_planejamento in active_planejamentos
    assert inactive_planejamento not in active_planejamentos
    assert future_planejamento not in active_planejamentos


@pytest.mark.django_db
def test_gerar_lista_planejamento_anual(create_planejamento):
    categoria1 = Categoria.objects.create(
        cod='CAT1',
        tipo='E',
        descricao='Test Category 1'
    )
    categoria2 = Categoria.objects.create(
        cod='CAT1',
        tipo='E',
        descricao='Test Category 2'
    )

    planejamento_1 = create_planejamento(
        mes=date(2023, 8, 1),
        valor=Decimal('100.00'),
        repeticoes=0,
        categoria=categoria1,
        status=Planejamento.STATUS_ACTIVE
    )

    planejamento_2 = create_planejamento(
        mes=date(2023, 9, 1),
        valor=Decimal('150.00'),
        repeticoes=3,
        categoria=categoria2,
        status=Planejamento.STATUS_ACTIVE
    )

    data_inicio = date(2023, 7, 1)
    planejamento_anual = Planejamento.gerar_lista_planejamento_anual(data_inicio)

    assert len(planejamento_anual) == 6  # Gera lista para 5 meses a partir de agosto

    assert planejamento_anual['Julho']['total'] == Decimal('0.00')
    assert planejamento_anual['Julho'].get(categoria1.descricao) is None
    assert planejamento_anual['Julho'].get(categoria2.descricao) is None

    assert planejamento_anual['Agosto']['total'] == planejamento_1.valor
    assert planejamento_anual['Agosto'].get(categoria1.descricao) == planejamento_1.valor
    assert planejamento_anual['Agosto'].get(categoria2.descricao) is None

    assert planejamento_anual['Setembro']['total'] == planejamento_1.valor + planejamento_2.valor
    assert planejamento_anual['Setembro'].get(categoria1.descricao) == planejamento_1.valor
    assert planejamento_anual['Setembro'].get(categoria2.descricao) == planejamento_2.valor

    assert planejamento_anual['Outubro']['total'] == planejamento_1.valor + planejamento_2.valor
    assert planejamento_anual['Outubro'].get(categoria1.descricao) == planejamento_1.valor
    assert planejamento_anual['Outubro'].get(categoria2.descricao) == planejamento_2.valor

    assert planejamento_anual['Novembro']['total'] == planejamento_1.valor + planejamento_2.valor
    assert planejamento_anual['Novembro'].get(categoria1.descricao) == planejamento_1.valor
    assert planejamento_anual['Novembro'].get(categoria2.descricao) == planejamento_2.valor

    assert planejamento_anual['Dezembro']['total'] == planejamento_1.valor
    assert planejamento_anual['Dezembro'].get(categoria1.descricao) == planejamento_1.valor
    assert planejamento_anual['Dezembro'].get(categoria2.descricao) is None
