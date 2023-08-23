import pytest
from decimal import Decimal

from django.test import Client
from conftest import setup_test_data
from meusgastos.apps.core.utils import mes_em_portugues
import time_machine


@time_machine.travel("2022-12-31 00:00 +0000")
@pytest.mark.django_db
def test_dashboard_data_view(client, setup_test_data):
    # SET EXPECTED DATA
    expected_oveview_data = {
        'Janeiro': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Fevereiro': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('4920.0'),
            'saldoTotal': Decimal('80.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Março': {
            'receitas': Decimal('5080.0'),
            'despesas': Decimal('5120.0'),
            'saldoTotal': Decimal('-40.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('80.0')
        },
        'Abril': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('-40.0')
        },
        'Maio': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Junho': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Julho': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5100.0'),
            'saldoTotal': Decimal('-100.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Agosto': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('-100.0')
        },
        'Setembro': {
            'receitas': Decimal('5000.0'),
            'despesas': Decimal('4900.0'),
            'saldoTotal': Decimal('100.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('0.0')
        },
        'Outubro': {
            'receitas': Decimal('5100.0'),
            'despesas': Decimal('5000.0'),
            'saldoTotal': Decimal('100.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('100.0')
        },
        'Novembro': {
            'receitas': Decimal('5100.0'),
            'despesas': Decimal('4900.0'),
            'saldoTotal': Decimal('200.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('100.0')
        },
        'Dezembro': {
            'receitas': Decimal('5200.0'),
            'despesas': Decimal('5200.0'),
            'saldoTotal': Decimal('0.0'),
            'reservas': Decimal('0.0'),
            'saldoMesAnterior': Decimal('200.0')
        }
    }
    
    expected_gastos_por_categorias = {
        'Janeiro': {
            'Alimentação': float(70.0),
            'Aprimoramento': float(600.0),
            'Filhos': float(1500.0),
            'Moradia': float(2120.0),
            'Supermercado': float(710.0)
        },
        'Fevereiro': {
            'Aprimoramento': float(600.0),
            'Filhos': float(1500.0),
            'Moradia': float(2120.0),
            'Supermercado': float(700.0)
        },
        'Março': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Saúde': 100.0,
            'Supermercado': 800.0
        },
        'Abril': {
            'Alimentação': 100.0,
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 640.0
        },
        'Maio': {
            'Alimentação': 80.0,
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Saúde': 100.0,
            'Supermercado': 600.0
        },
        'Junho': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 780.0
        },
        'Julho': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Saúde': 100.0,
            'Supermercado': 780.0
        },
        'Agosto': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 680.0
        },
        'Setembro': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 680.0
        },
        'Outubro': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 780.0
        },
        'Novembro': {
            'Aprimoramento': 600.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 680.0},
        'Dezembro': {
            'Aprimoramento': 600.0,
            'Cartão de Crédito': 520.0,
            'Compras': 280.0,
            'Filhos': 1500.0,
            'Moradia': 2120.0,
            'Supermercado': 180.0
        }
    }

    expected_gastos_por_subcategorias = {
        'Janeiro': {
            'Alimentação': {'Padaria': 50.0, 'Restaurante': 20.0},
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Fevereiro': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Março': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0},
            'Saúde': {'Drogaria': 100.0}
        },
        'Abril': {
            'Alimentação': {'Restaurante': 100.0},
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Maio': {
            'Alimentação': {'Lanchonete': 80.0},
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0},
            'Saúde': {'Drogaria': 100.0}
        },
        'Junho': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Julho': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0},
            'Saúde': {'Drogaria': 100.0}
        },
        'Agosto': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Setembro': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Outubro': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Novembro': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        },
        'Dezembro': {
            'Aprimoramento': {'Inglês': 600.0},
            'Filhos': {'Escola': 1500.0},
            'Moradia': {'Aluguel': 1000.0, 'Condomínio': 1000.0, 'Internet': 120.0}
        }
    }

    expected_crescimento_receitas_despesas = {
        'Janeiro': {'receitas': '5000.00', 'despesas': '5000.00', 'credito': '0.00', 'debito': '0.00'},
        'Fevereiro': {'receitas': '5000.00', 'despesas': '4920.00', 'credito': '0.00', 'debito': '0.00'},
        'Março': {'receitas': '5000.00', 'despesas': '5120.00', 'credito': '80.00', 'debito': '0.00'},
        'Abril': {'receitas': '5000.00', 'despesas': '4960.00', 'credito': '0.00', 'debito': '40.00'},
        'Maio': {'receitas': '5000.00', 'despesas': '5000.00', 'credito': '0.00', 'debito': '0.00'},
        'Junho': {'receitas': '5000.00', 'despesas': '5000.00', 'credito': '0.00', 'debito': '0.00'},
        'Julho': {'receitas': '5000.00', 'despesas': '5100.00', 'credito': '0.00', 'debito': '0.00'},
        'Agosto': {'receitas': '5000.00', 'despesas': '4900.00', 'credito': '0.00', 'debito': '100.00'},
        'Setembro': {'receitas': '5000.00', 'despesas': '4900.00', 'credito': '0.00', 'debito': '0.00'},
        'Outubro': {'receitas': '5000.00', 'despesas': '5000.00', 'credito': '100.00', 'debito': '0.00'},
        'Novembro': {'receitas': '5000.00', 'despesas': '4900.00', 'credito': '100.00', 'debito': '0.00'},
        'Dezembro': {'receitas': '5000.00', 'despesas': '5200.00', 'credito': '200.00', 'debito': '0.00'}
    }

    expected_despesas_futuras = {}

    expected_media_gastos_categorias = {
        'Moradia': '2120.00',
        'Filhos': '1500.00',
        'Aprimoramento': '600.00',
        'Supermercado': '546.67',
        'Cartão de Crédito': '173.33',
        'Compras': '93.33'
    }

    expected_transaction_list = {
        'Janeiro': [
            {'data': '2022-01-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-01-05T00:00:00', 'tipo': 'S', 'descricao': 'Padaria', 'categoria': 'Alimentação',
             'subcategoria': 'Padaria', 'valor': 50.0},
            {'data': '2022-01-09T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Mercado das Frutas',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 600.0},
            {'data': '2022-01-09T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Restaurante do Ze',
             'categoria': 'Alimentação', 'subcategoria': 'Restaurante', 'valor': 20.0},
            {'data': '2022-01-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-01-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-01-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-01-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-01-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-01-20T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Supermercado Pague Menos',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 110.0}
        ],
        'Fevereiro': [
            {'data': '2022-02-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-02-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-02-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-02-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-02-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-02-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-02-25T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Supermercado Pague Menos',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 700.0}
        ],
        'Março': [
            {'categoria': 'Ajuste', 'data': '2022-03-01T00:00:00', 'descricao': 'Ajuste de crédito mês anterior',
             'subcategoria': '', 'tipo': 'E', 'valor': 80.0},
            {'data': '2022-03-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-03-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola 02/08',
             'categoria': 'Filhos', 'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-03-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-03-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-03-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-03-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-03-19T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Drogaria', 'categoria': 'Saúde',
             'subcategoria': 'Drogaria', 'valor': 100.0},
            {'data': '2022-03-25T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Supermercado Carrefour',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 800.0}
        ],
        'Abril': [
            {'categoria': 'Ajuste', 'data': '2022-04-01T00:00:00', 'descricao': 'Ajuste de débito mês anterior',
             'subcategoria': '', 'tipo': 'S', 'valor': -40.0},
            {'data': '2022-04-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-04-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-04-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-04-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-04-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-04-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-04-20T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Restaurante Bom Sabor',
             'categoria': 'Alimentação', 'subcategoria': 'Restaurante', 'valor': 100.0},
            {'data': '2022-04-25T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Supermercado Carrefour',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 640.0}
        ],
        'Maio': [
            {'data': '2022-05-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-05-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-05-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-05-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-05-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-05-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-05-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Drogaria', 'categoria': 'Saúde',
             'subcategoria': 'Drogaria', 'valor': 100.0},
            {'data': '2022-05-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Supermercado',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 100.0},
            {'data': '2022-05-25T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Lanchonete',
             'categoria': 'Alimentação', 'subcategoria': 'Lanchonete', 'valor': 80.0},
            {'data': '2022-05-27T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Hortifruti',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 500.0}
        ],
        'Junho': [
            {'data': '2022-06-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-06-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-06-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-06-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-06-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-06-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-06-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Mercado Popular',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 780.0}
        ],
        'Julho': [
            {'data': '2022-07-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-07-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-07-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-07-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-07-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-07-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-07-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Mercado Popular',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 780.0},
            {'data': '2022-07-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Drogaria', 'categoria': 'Saúde',
             'subcategoria': 'Drogaria', 'valor': 100.0}
        ],
        'Agosto': [
            {'categoria': 'Ajuste', 'data': '2022-08-01T00:00:00', 'descricao': 'Ajuste de débito mês anterior',
             'subcategoria': '', 'tipo': 'S', 'valor': -100.0},
            {'data': '2022-08-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-08-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-08-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-08-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-08-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-08-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-08-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Mercado Popular',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 680.0}
        ],
        'Setembro': [
            {'data': '2022-09-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-09-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-09-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-09-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-09-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-09-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-09-20T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Mercado Popular',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 680.0}
        ],
        'Outubro': [
            {'categoria': 'Ajuste', 'data': '2022-10-01T00:00:00', 'descricao': 'Ajuste de crédito mês anterior',
             'subcategoria': '', 'tipo': 'E', 'valor': 100.0},
            {'data': '2022-10-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-10-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-10-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-10-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-10-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-10-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-10-25T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Supermercado Pao de Acucar',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 780.0}
        ],
        'Novembro': [
            {'categoria': 'Ajuste', 'data': '2022-11-01T00:00:00', 'descricao': 'Ajuste de crédito mês anterior',
             'subcategoria': '', 'tipo': 'E', 'valor': 100.0},
            {'data': '2022-11-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-11-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-11-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-11-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-11-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-11-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-11-25T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Supermercado Pao de Acucar',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 680.0}
        ],
        'Dezembro': [
            {'categoria': 'Ajuste', 'data': '2022-12-01T00:00:00', 'descricao': 'Ajuste de crédito mês anterior',
             'subcategoria': '', 'tipo': 'E', 'valor': 200.0},
            {'data': '2022-12-01T00:00:00', 'tipo': 'E', 'descricao': 'Salario', 'categoria': 'Salário',
             'subcategoria': '', 'valor': 5000.0},
            {'data': '2022-12-10T00:00:00', 'tipo': 'S', 'descricao': 'Transfe Pix Des: Escola', 'categoria': 'Filhos',
             'subcategoria': 'Escola', 'valor': 1500.0},
            {'data': '2022-12-10T00:00:00', 'tipo': 'S', 'descricao': 'Conta Telefone Vivo Fixo-nac Dig-999999',
             'categoria': 'Moradia', 'subcategoria': 'Internet', 'valor': 120.0},
            {'data': '2022-12-10T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Curso de Ingles Fisk',
             'categoria': 'Aprimoramento', 'subcategoria': 'Inglês', 'valor': 600.0},
            {'data': '2022-12-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Aluguel', 'categoria': 'Moradia',
             'subcategoria': 'Aluguel', 'valor': 1000.0},
            {'data': '2022-12-15T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Condominio',
             'categoria': 'Moradia', 'subcategoria': 'Condomínio', 'valor': 1000.0},
            {'data': '2022-12-25T00:00:00', 'tipo': 'S', 'descricao': 'Pagto Cobranca Cartao de Credito',
             'categoria': 'Cartão de Crédito', 'subcategoria': '', 'valor': 520.0},
            {'data': '2022-12-25T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Compras no Shopping',
             'categoria': 'Compras', 'subcategoria': '', 'valor': 280.0},
            {'data': '2022-12-25T00:00:00', 'tipo': 'S', 'descricao': 'Visa Electron Hortifruti',
             'categoria': 'Supermercado', 'subcategoria': '', 'valor': 180.0}
        ]
    }
    
    # Crie um objeto Client para fazer a solicitação
    client = Client()

    # Defina os parâmetros da URL para o mês e ano que você deseja testar
    year = 2022

    for month in range(1, 13):
        # Faça a solicitação para a URL da view
        response = client.get(f'/data/?month={month}&year={year}')

        # Verifique se a resposta foi bem-sucedida (código de status 200)
        assert response.status_code == 200

        # Verifique se a resposta contém os dados esperados (isso depende dos dados reais retornados)
        data = response.json()  # Converte o conteúdo JSON da resposta em um dicionário

        month_name = mes_em_portugues(month)

        # Verifica se os dados de visão geral são os esperados
        assert Decimal(data['receitas']) == expected_oveview_data[month_name]['receitas']
        assert Decimal(data['despesas']) == expected_oveview_data[month_name]['despesas']
        assert Decimal(data['saldoTotal']) == expected_oveview_data[month_name]['saldoTotal']
        assert Decimal(data['reservas']) == expected_oveview_data[month_name]['reservas']
        assert Decimal(data['saldoMesAnterior']) == expected_oveview_data[month_name]['saldoMesAnterior']

        # Verifica se os dados de gastos por categoria são os esperados
        assert data['despesasPorCategorias'] == expected_gastos_por_categorias[month_name]

        # Verifica se os dados de gastos por subcategoria são os esperados
        assert data['despesasPorSubcategorias'] == expected_gastos_por_subcategorias[month_name]

        # Verifica se os dados de despesas futuras são os esperados
        assert data['despesasFuturas'] == expected_despesas_futuras

        # Verifica se os dados de média de gastos por categoria são os esperados
        assert data['mediaGastosCategorias'] == expected_media_gastos_categorias

        # Verifica se os dados de crescimento de receita e despesa são os esperados
        assert data['crescimentoReceitasDespesas'][month_name] == expected_crescimento_receitas_despesas[month_name]

        # Verifica as transações do mês
        assert data['transacoes'] == expected_transaction_list[month_name]
