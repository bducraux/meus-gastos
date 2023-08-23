import pytest
from datetime import date
from conftest import setup_test_data
from meusgastos.apps.transacoes.utils import get_balance_at_given_date


@pytest.mark.django_db
def test_get_balance_at_given_date(setup_test_data):
    # check balance at 01/03/2022
    date_to_check = date(2022, 3, 1)
    expected_balance = 80
    balance = get_balance_at_given_date(date_to_check)

    assert balance == expected_balance

    # check balance at 01/01/2023
    date_to_check = date(2023, 1, 1)
    expected_balance = 0
    balance = get_balance_at_given_date(date_to_check)

    assert balance == expected_balance
