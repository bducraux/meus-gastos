import os
import pytest
from django.conf import settings
from django.core.management import call_command

from meusgastos.apps.core.extratores_de_dados.extrator_ofx_bradesco import extrator_ofx_bradesco


@pytest.fixture
def setup_test_data():
    # Carrega as categorias da fixture antes de executar os testes
    call_command('loaddata', 'categorias', app_label='categorias')

    # Obtém o diretório base do projeto Django
    base_dir = settings.BASE_DIR

    # Constrói o caminho completo para o arquivo OFX
    fake_ofx_file_path = os.path.join(base_dir, "importacoes/extrato/extrato_sample.ofx")

    # Simula a extração e gravação das transações no banco de dados
    extrator_ofx_bradesco(fake_ofx_file_path)
