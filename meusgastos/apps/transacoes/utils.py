from meusgastos.apps.categorias.models import Categoria
from meusgastos.apps.transacoes.models import Transacao
from datetime import date
from django.db.models import Sum
from decimal import Decimal


def get_transactions_with_items(year: int, month: int or None = None) -> list:
    """
    Get all transactions and transaction items for a given month
    :param month: int (1-12) (month number)
    :param year: int (4 digits year)
    :return: list of transactions
    """

    if month is not None and (month < 1 or month > 12):
        raise ValueError('Month must be a number between 1 and 12')

    if len(str(year)) != 4:
        raise ValueError('Year must be a 4 digits number')

    transactions = Transacao.objects.filter(data__year=year,
                                            status=Transacao.STATUS_ACTIVE,
                                            efetivado=True)

    if month is not None:
        transactions = transactions.filter(data__month=month)

    transactions = transactions.prefetch_related('items', 'categoria').order_by('data')

    return_list = []
    for transaction in transactions:

        # se a transação não tiver itens ou se tiver items mais ainda sobrar valor na transação ela é adicionada
        # caso contrario ela é ignorada pois já foi descriminada nos items
        if transaction.items.count() == 0 or (transaction.items.count() > 0 and abs(transaction.valor) > 0):
            return_list.append({
                'data': transaction.data,
                'descricao': transaction.memo,
                'valor': transaction.valor,
                'tipo': transaction.tipo,
                'categoria_descricao': transaction.categoria.descricao if transaction.categoria else 'Não categorizado',
                'categoria_parent': transaction.categoria.parent.descricao if (
                        transaction.categoria and transaction.categoria.parent) else ''
            })

        # adiciona os items da transação na lista
        for item in transaction.items.all():
            return_list.append({
                'data': transaction.data,
                'descricao': item.descricao,
                'valor': item.valor,
                'tipo': transaction.tipo,
                'categoria_id': item.categoria.id if item.categoria else None,
                'categoria_descricao': item.categoria.descricao if item.categoria else 'Não categorizado',
                'categoria_parent': item.categoria.parent.descricao if (
                        item.categoria and item.categoria.parent) else ''
            })

    return return_list


def get_future_transactions() -> list:
    """
    Get all transactions above the current date
    :return: list of transactions
    """

    current_date = date.today()
    start_date = date(current_date.year, current_date.month, 1)

    transactions = Transacao.objects.filter(
        data__gte=start_date,
        data__year=current_date.year,
        status=Transacao.STATUS_ACTIVE,
        efetivado=False)

    transactions = transactions.prefetch_related('items', 'categoria').order_by('data')

    return_list = []
    for transaction in transactions:
        return_list.append({
            'data': transaction.data,
            'descricao': transaction.memo,
            'valor': transaction.valor,
            'tipo': transaction.tipo,
            'categoria_descricao': transaction.categoria.descricao if transaction.categoria else 'Não categorizado',
            'categoria_parent': transaction.categoria.parent.descricao if (
                    transaction.categoria and transaction.categoria.parent) else ''
        })

    return return_list


def get_month_overview(year: int, month: int) -> tuple:
    """
    Get a overview of the month with the sum of income, expenses and balance
    :param month: int (1-12) (month number)
    :param year: int (4 digits year)
    :return: dict - {'income': 1000, 'expenses': 500, 'balance': 500}
    """
    if month < 1 or month > 12:
        raise ValueError('Month must be a number between 1 and 12')

    if len(str(year)) != 4:
        raise ValueError('Year must be a 4 digits number')

    transacoes = Transacao.objects.filter(data__year=year,
                                          data__month=month,
                                          status=Transacao.STATUS_ACTIVE,
                                          efetivado=True)

    # income
    income = transacoes.filter(tipo=Transacao.TYPE_INCOME).aggregate(total_income=Sum('valor_total'))['total_income']
    income = income if income else 0

    # expenses
    expenses = transacoes.filter(tipo=Transacao.TYPE_EXPENSE).aggregate(total_expenses=Sum('valor_total'))[
        'total_expenses']
    expenses = expenses if expenses else 0

    # balance
    balance = income + expenses

    return f"{income:.2f}", f"{expenses:.2f}", f"{balance:.2f}"


def auto_categorize_transaction(memo: str) -> Categoria or None:
    """
    Auto categorize a transaction based on the keywords of the categories
    :param memo: str - memo of the transaction
    :return: Categoria or None - the category or None if not found
    """
    categories = Categoria.objects.filter(is_active=True, keywords__isnull=False)

    for category in categories:
        keywords = category.keywords.split(',')
        # remove empty strings from list
        keywords = list(filter(None, keywords))
        for keyword in keywords:
            if keyword.lower() in memo.lower():
                return category

    return None


def is_transaction_ignored(memo: str) -> bool:
    """
    Check if the transaction should be ignored
    :param memo: str - memo of the transaction
    :return: bool - True if should be ignored, False otherwise
    """
    ignore_keywords = Transacao.IGNORED_KEYWORDS

    for keyword in ignore_keywords:
        if keyword.lower() in memo.lower():
            return True

    return False


def get_balance_at_given_date(date_to_check: date) -> Decimal:
    """
    Get the balance at a given date
    :param date_to_check: date - date to check the balance
    :return: Decimal - balance at the given date
    """

    # get all transactions until the given date and sum the valor_total of income and expenses
    transactions = Transacao.objects.filter(data__lt=date_to_check,
                                            status=Transacao.STATUS_ACTIVE,
                                            efetivado=True).order_by('data')

    if not transactions:
        return Decimal(0)

    income = sum(
        [transaction.valor_total for transaction in transactions if transaction.tipo == Transacao.TYPE_INCOME]
    )
    expenses = sum(
        [transaction.valor_total for transaction in transactions if transaction.tipo == Transacao.TYPE_EXPENSE]
    )

    return Decimal(income) - abs(Decimal(expenses))
