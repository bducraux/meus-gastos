from django.core.management.base import BaseCommand
from meusgastos.apps.transacoes.models import Transacao
from meusgastos.apps.transacoes.utils import auto_categorize_transaction
import re
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Importa conta de arquivo TXT e grava as transações no banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument('txt_file_path', type=str, help='Caminho para o arquivo TXT')

    def handle(self, *args, **kwargs):
        txt_file_path = kwargs['txt_file_path']

        self.stdout.write(self.style.SUCCESS(f"Importando transações do arquivo {txt_file_path}..."))

        # Abrir o arquivo para leitura
        with open(txt_file_path, 'r') as file:
            lines = file.readlines()

        # Inicializar uma lista para armazenar os dados extraídos
        data = []

        for line in lines:
            fields = re.split(r'\s{5,}', line.strip())
            if len(fields) == 3:
                try:
                    date = fields[0].strip()
                    base_date = datetime.strptime(date, '%d/%m/%Y')
                    description = fields[1].strip()
                    amount = float(fields[2].strip().replace(",", "."))
                except ValueError as e:
                    self.stdout.write(self.style.WARNING(f"Não foi possível converter a linha: {line}"))
                    self.stdout.write(self.style.ERROR(f"Erro: {e}"))
                    continue

                transaction_dict = {
                    'memo': description,
                    'tipo': 'S',
                    'data': base_date,
                    'valor': amount,
                    'efetivado': True,
                }

                data.append(transaction_dict)

                # Verificar se o histórico contém informações de parcelamento no final
                if re.search(r' \d+/\d+$', description):
                    match = re.search(r' (\d+)/(\d+)$', description)
                    current_month, total_months = map(int, match.groups())
                    remaining_months = total_months - current_month

                    projected_transactions = project_transactions(
                        base_date,
                        description,
                        amount,
                        current_month,
                        total_months,
                        remaining_months
                    )
                    data.extend(projected_transactions)

        # Imprimir os dados extraídos
        for transaction in data:
            print(transaction)

        self.stdout.write(self.style.SUCCESS('Transações importadas co sucesso!'))


# Função para projetar despesas parceladas
def project_transactions(base_date, description, amount, current_month, total_months, remaining_months):
    projected_transactions = []

    for i in range(1, remaining_months + 1):
        projected_date = base_date + timedelta(days=30 * i)  # Projetar para o próximo mês
        projected_description = re.sub(r'\d+/\d+', f"{current_month + i}/{total_months}", description)

        transaction_dict = {
            'memo': projected_description,
            'tipo': 'S',
            'data': projected_date,
            'valor': amount,
            'efetivado': False,
        }
        projected_transactions.append(transaction_dict)

    return projected_transactions
