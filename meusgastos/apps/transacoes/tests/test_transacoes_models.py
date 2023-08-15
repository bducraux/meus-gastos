import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from meusgastos.apps.transacoes.models import Transacao, TransacaoItem
from meusgastos.apps.categorias.models import Categoria


@pytest.fixture
def create_transaction():
    def _create_transaction(**kwargs):
        transaction = Transacao.objects.create(**kwargs)
        return transaction

    return _create_transaction


@pytest.fixture
def create_transaction_item():
    def _create_transaction_item(transaction, **kwargs):
        transaction_item = TransacaoItem.objects.create(transacao=transaction, **kwargs)
        return transaction_item

    return _create_transaction_item


@pytest.mark.django_db
def test_transaction_item_value_exceeds_total(create_transaction, create_transaction_item):
    expense_transaction = create_transaction(
        identificacao='Test Expense Transaction',
        memo='Debit transaction memo',
        valor=Decimal('-100.00'),
        tipo=Transacao.TYPE_EXPENSE,
        data='2023-01-01'
    )

    with pytest.raises(ValidationError):
        item = create_transaction_item(expense_transaction, descricao='Item 1', valor=Decimal('-110.00'))

    credit_transaction = create_transaction(
        identificacao='Test Credit Transaction',
        memo='Credit transaction memo',
        valor=Decimal('100.00'),
        tipo=Transacao.TYPE_INCOME,
        data='2023-01-01'
    )

    with pytest.raises(ValidationError):
        item = create_transaction_item(credit_transaction, descricao='Item 1', valor=Decimal('110.00'))


@pytest.mark.django_db
def test_transaction_item_category_type_mismatch(create_transaction, create_transaction_item):
    transaction = create_transaction(
        identificacao='Test Transaction 2',
        memo='Transaction memo 2',
        valor=Decimal('-100.00'),
        valor_total=Decimal('-100.00'),
        data='2023-01-01',
        tipo=Transacao.TYPE_EXPENSE
    )

    categoria = Categoria.objects.create(
        cod='CAT',
        tipo=Transacao.TYPE_INCOME,
        descricao='Categoria de Teste'
    )

    with pytest.raises(ValidationError):
        create_transaction_item(transaction, descricao='Item 1', valor=Decimal('-30.00'), categoria=categoria)

    # verifica se o item foi criado mesmo com o erro
    assert transaction.items.all().count() == 0


@pytest.mark.django_db
def test_get_remaining_value():
    categoria = Categoria.objects.create(
        cod='CAT',
        tipo=Transacao.TYPE_EXPENSE,
        descricao='Categoria de Teste'
    )

    transaction = Transacao.objects.create(
        identificacao='Test Transaction',
        memo='Transaction memo',
        valor=Decimal('-100.00'),
        data='2023-01-01',
        tipo=Transacao.TYPE_EXPENSE
    )

    item = TransacaoItem.objects.create(
        transacao=transaction,
        descricao='Item 1',
        valor=Decimal('-30.00'),
        categoria=categoria
    )

    remaining_value = transaction.valor_total - item.valor

    assert remaining_value == transaction.valor


# testa se o valor da transação é atualizado após deletar um item, usa o teste anterior como base
@pytest.mark.django_db
def test_inserting_and_deleting_items(create_transaction, create_transaction_item):
    transaction = create_transaction(
        identificacao='Test Transaction 2',
        memo='Transaction memo 2',
        valor=Decimal('-100.00'),
        valor_total=Decimal('-100.00'),
        data='2023-01-01',
        tipo=Transacao.TYPE_EXPENSE
    )

    item1 = create_transaction_item(transaction, descricao='Item 1', valor=Decimal('-20.00'))
    expected_remaining_value = Decimal(-80.00)
    assert transaction.valor == expected_remaining_value
    item2 = create_transaction_item(transaction, descricao='Item 2', valor=Decimal('-20.00'))
    expected_remaining_value = Decimal(-60.00)
    assert transaction.valor == expected_remaining_value
    item3 = create_transaction_item(transaction, descricao='Item 3', valor=Decimal('-20.00'))
    expected_remaining_value = Decimal(-40.00)
    assert transaction.valor == expected_remaining_value
    item4 = create_transaction_item(transaction, descricao='Item 4', valor=Decimal('-20.00'))
    expected_remaining_value = Decimal(-20.00)
    assert transaction.valor == expected_remaining_value
    item5 = create_transaction_item(transaction, descricao='Item 5', valor=Decimal('-20.00'))
    expected_remaining_value = Decimal(0.00)
    assert transaction.valor == expected_remaining_value

    item1.delete()
    expected_remaining_value = Decimal(-20.00)
    assert transaction.valor == expected_remaining_value
    item2.delete()
    expected_remaining_value = Decimal(-40.00)
    assert transaction.valor == expected_remaining_value
    item3.delete()
    expected_remaining_value = Decimal(-60.00)
    assert transaction.valor == expected_remaining_value
    item4.delete()
    expected_remaining_value = Decimal(-80.00)
    assert transaction.valor == expected_remaining_value
    item5.delete()
    expected_remaining_value = Decimal(-100.00)
    assert transaction.valor == expected_remaining_value


