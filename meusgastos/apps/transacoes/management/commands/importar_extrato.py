from django.core.management.base import BaseCommand

from meusgastos.apps.core.extratores_de_dados.extrator_ofx_bradesco import extrator_ofx_bradesco


class Command(BaseCommand):
    help = ('Importa extrato de transações do arquivo OFX e grava no banco de dados. '
            'Esse script foi testado com arquivos OFX do Bradesco.')

    def add_arguments(self, parser):
        parser.add_argument('ofx_file_path', type=str, help='Caminho para o arquivo OFX')

    def handle(self, *args, **kwargs):
        ofx_file_path = kwargs['ofx_file_path']

        try:
            extrator_ofx_bradesco(ofx_file_path)
            self.stdout.write(self.style.SUCCESS('Transações importadas com sucesso!'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(e))
