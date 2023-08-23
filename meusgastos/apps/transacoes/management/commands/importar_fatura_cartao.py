# Comando: python manage.py importar_fatura_cartao <caminho para o arquivo TXT>
# Este comando realiza a importação de uma fatura de cartão de crédito do banco Bradesco e cria as transações no banco
# de dados correspondentes. Compras parceladas são projetadas para os meses seguintes.

# Durante os testes extensivos realizados com dados reais de um ano de faturas, identificamos alguns desafios na geração
# de um identificador único para cada transação projetada. Infelizmente, o banco Bradesco não fornece um identificador
# exclusivo para cada compra, e certos campos, como data, memo e valor, podem se repetir em compras diferentes.
# Além disso, os valores podem variar entre parcelas de uma mesma compra parcelada.

# Para lidar com essa situação, adotamos a seguinte abordagem:
# - As transações projetadas para um cartão serão apagadas e regeradas a cada importação, assegurando que estejam
#   atualizadas e consistentes com os dados da nova fatura.
# - Introduzimos um identificador adicional para os itens da fatura que se repetem, acrescentando #1, #2 e assim por
#   diante ao final da identificacao, de modo a diferenciá-los.


# Recomendamos a importação de faturas em uma ordem cronológica, pois as transações projetadas estarão corretas e
# alinhadas com a sequência temporal das faturas.

# ATENÇÃO:
# Evite a importação duplicada de faturas de cartões de crédito, pois isso resultará na inserção duplicada das
# transações no banco de dados, gerando registros duplicados com identificadores diferentes por causa do sistema de
# incremento automático.


from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from dateutil.relativedelta import relativedelta

from meusgastos.apps.transacoes.utils import auto_categorize_transaction
from meusgastos.apps.transacoes.models import Transacao


class Command(BaseCommand):
    help = 'Importa conta de arquivo TXT e grava as transações no banco de dados.'

    def add_arguments(self, parser):
        parser.add_argument('txt_file_path', type=str, help='Caminho para o arquivo TXT')

    def handle(self, *args, **kwargs):
        try:
            txt_file_path = kwargs['txt_file_path']

            # Pergunta ao usuario qual o identificador da fatura,
            # podendo ser o id da transação ou o memo / identificação
            identificador_fatura = input("Qual o identificador da fatura? (id ou memo): ")

            transacao_pagamento_cartao = self.get_transacao(identificador_fatura)
            if transacao_pagamento_cartao is None:
                return

            self.confirmar_extracao_dados(transacao_pagamento_cartao, txt_file_path)

            # Define a data e valor da fatura
            transacao_pagamento_cartao_data = transacao_pagamento_cartao.data
            transacao_pagamento_cartao_valor = transacao_pagamento_cartao.valor

            # Extrair os dados da fatura
            (lista_cartoes_extraidos,
             lista_transacoes_extraidas,
             lista_transacoes_futuras_extraidas,
             valor_items_extratidos) = self.extrair_dados_da_fatura(transacao_pagamento_cartao_data, txt_file_path)

            self.imprime_dados_extraidos(lista_transacoes_extraidas, lista_transacoes_futuras_extraidas)

            # Verificar se o valor da fatura é igual ao valor da transação
            self.verifica_valores(transacao_pagamento_cartao_valor, valor_items_extratidos)

            # Inserir as transações no banco de dados
            self.inserir_transacoes(transacao_pagamento_cartao,
                                    lista_cartoes_extraidos,
                                    lista_transacoes_extraidas,
                                    lista_transacoes_futuras_extraidas)

            self.print_success('Transações importadas com sucesso!')
        except (ImportacaoCanceladaException, KeyboardInterrupt):
            self.print_error(f"\nImportação cancelada")

    def extrair_dados_da_fatura(self, transacao_pagamento_cartao_data, txt_file_path):
        """
        Extrai os dados da fatura do cartão de crédito do arquivo TXT extraído do site do banco do Bradesco, e retorna
        uma lista de dicionários com as transações encontradas, transações futuras e o valor total da fatura.
        :param transacao_pagamento_cartao_data:
        :param txt_file_path:
        :return:
        """
        # Inicializar variáveis para armazenar os dados extraídos
        lista_transacoes = []
        lista_transacoes_futuras = []
        cartoes_extraidos = []
        valor_fatura = 0
        contador_por_memo = {}  # Dicionário para rastrear contadores por memo

        # Abrir o arquivo para leitura
        with open(txt_file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            fields = re.split(r'\s{5,}', line.strip())

            # Verifica se a linha possui 2 colunas e se a segunda coluna é relacionada ao número do cartão de 4 dígitos
            if len(fields) == 2 and re.search(r'^\d{4}$', fields[1].strip()):
                numero_cartao = fields[1].strip()
                cartoes_extraidos.append(numero_cartao)

            if len(fields) != 4:
                continue

            # Verifica se a primeira coluna é uma data válida
            try:
                date = fields[0].strip()
                data_da_compra = datetime.strptime(date, '%d/%m') + relativedelta(
                    year=transacao_pagamento_cartao_data.year)
            except ValueError:
                continue

            # Verifica se a segunda coluna é uma descrição válida
            items_ignorados_coluna_2 = ['SALDO ANTERIOR', 'PAGTO. POR DEB EM C/C']
            memo = fields[1].strip()
            if memo in items_ignorados_coluna_2:
                continue

            # Verifica se a coluna 4 é um valor válido
            try:
                valor = Decimal(fields[3].strip().replace(",", ".")) * -1
                tipo = "E" if valor > 0 else "S"
            except InvalidOperation:
                continue

            # Verifica se já existe um contador para o memo atual
            if memo in contador_por_memo:
                contador_por_memo[memo] += 1
            else:
                contador_por_memo[memo] = 1

            contador_memo = contador_por_memo[memo]

            # Verifica se a compra é uma compra parcelada
            parcelas_restantes = 0
            if re.search(r' \d+/\d+$', memo):
                match = re.search(r' (\d+)/(\d+)$', memo)
                parcela_atual, total_de_parcelas = map(int, match.groups())
                parcelas_restantes = total_de_parcelas - parcela_atual

                # verifica se a compra parcelada foi efetuada no ano anterior
                if parcela_atual > transacao_pagamento_cartao_data.month:
                    data_da_compra = data_da_compra - relativedelta(years=1)

            identificacao = (f"Item fatura do cartão {numero_cartao}|"
                             f"{data_da_compra.strftime('%d/%m/%Y')}|"
                             f"{memo}|"
                             f"{valor}|"
                             f"#{contador_memo}")
            observacao = (f"Item da fatura do cartão de crédito {numero_cartao} paga em "
                          f"{transacao_pagamento_cartao_data.strftime('%d/%m/%Y')}")

            categoria = auto_categorize_transaction(memo)

            transaction_dict = {
                'identificacao': identificacao,
                'memo': memo,
                'tipo': tipo,
                'data': transacao_pagamento_cartao_data,
                'valor': valor,
                'observacao': observacao,
                'categoria': categoria,
                'efetivado': True,
            }

            valor_fatura += valor

            lista_transacoes.append(transaction_dict)

            # Projeta as transações futuras caso a compra seja parcelada
            if parcelas_restantes > 0:
                projected_transactions = project_transactions(
                    numero_cartao,
                    transacao_pagamento_cartao_data,
                    data_da_compra,
                    memo,
                    contador_memo,
                    categoria,
                    valor,
                    parcela_atual,
                    total_de_parcelas,
                    parcelas_restantes
                )
                lista_transacoes_futuras.extend(projected_transactions)

        if len(lista_transacoes) == 0:
            self.print_error(
                f"Não foi possível encontrar nenhuma transação na "
                f"fatura {transacao_pagamento_cartao_data.strftime('%d/%m/%Y')}")
            raise ImportacaoCanceladaException()

        return cartoes_extraidos, lista_transacoes, lista_transacoes_futuras, valor_fatura

    def imprime_dados_extraidos(self, lista_transacoes, lista_transacoes_futuras):
        # Imprimir os dados extraídos
        self.print_success(f"\nTransações encontradas na fatura:")
        for transacao_fatura in lista_transacoes:
            self.imprime_transacao(transacao_fatura)

        if len(lista_transacoes_futuras) > 0:
            self.print_success(f"\nTransações futuras encontradas:")
            for transacao_fatura in lista_transacoes_futuras:
                self.imprime_transacao(transacao_fatura)

    def imprime_transacao(self, transacao_fatura):
        data_transacao = transacao_fatura['data'].strftime('%d/%m/%Y')
        dados_da_compra = transacao_fatura['identificacao'].split('|')
        numero_cartao = dados_da_compra[0]
        data_da_compra = dados_da_compra[1]
        memo = dados_da_compra[2]
        self.print_warning(f"Data da transação: {data_transacao} - Cartão: {numero_cartao} - "
                           f"Data da compra: {data_da_compra} - Memo: {memo} - "
                           f"Valor: {transacao_fatura['valor']} - "
                           f"Categoria: {transacao_fatura['categoria']}")

    def inserir_transacoes(self,
                           transacao_pagamento_cartao,
                           lista_cartoes_extraidos,
                           lista_transacoes_extraidas,
                           lista_transacoes_futuras_extraidas):
        self.print_success(f"\nTransações encontradas: {len(lista_transacoes_extraidas)} - "
                           f"Transações futuras encontradas: {len(lista_transacoes_futuras_extraidas)}")
        confirmacao = input("Deseja inserir as transações encontradas? (s/n): ")
        if confirmacao.lower() != 's':
            raise ImportacaoCanceladaException()

        with transaction.atomic():
            # Loop através das transações da lista e insere/atualiza no banco de dados
            for transacao in lista_transacoes_extraidas:
                self.inserir_ou_atualizar_transacao(transacao)

            # limpa as transações futuras dos cartões extraídos
            for cartoes_extraido in lista_cartoes_extraidos:
                Transacao.objects.filter(
                    identificacao__icontains=f"Item parcelado fatura do cartão {cartoes_extraido}").delete()

            for transacao_futura in lista_transacoes_futuras_extraidas:
                self.inserir_ou_atualizar_transacao(transacao_futura)

            # Muda o status da transação de pagamento do cartão que foi descriminada para ignorado
            transacao_pagamento_cartao.status = Transacao.STATUS_IGNORED
            transacao_pagamento_cartao.save()

    def inserir_ou_atualizar_transacao(self, transacao_data):
        identificacao = transacao_data['identificacao']
        valor = transacao_data['valor']

        # Tenta buscar a transação pelo campo de identificação
        try:
            # Se não existe, cria uma nova transação
            Transacao.objects.create(**transacao_data)
            self.print_success(f"Transação criada: {transacao_data}")
        except IntegrityError:
            self.print_error(f"Transação já existe: {transacao_data}")



    def get_transacao(self, identificador_fatura):
        if identificador_fatura.isnumeric():
            transacao_qs = Transacao.objects.filter(pk=identificador_fatura)
        else:
            transacao_qs = Transacao.objects.filter(memo__icontains=identificador_fatura)

        if not transacao_qs:
            self.print_error(
                f"Não foi possível encontrar a transação com o identificador {identificador_fatura}")
            raise ImportacaoCanceladaException()

        if transacao_qs.count() > 1:
            transacao = self.selecionar_transacao(identificador_fatura, transacao_qs)
        else:
            transacao = transacao_qs.first()

        if transacao is None:
            return None

        return transacao

    def selecionar_transacao(self, identificador_fatura, transacao_qs):
        self.print_error(f"Encontrado mais de uma transação com o identificador {identificador_fatura}")

        self.print_warning("Transações encontradas:")
        id_list = []
        for t in transacao_qs:
            self.print_warning(f"Id: {t.id} - Data: {t.data.strftime('%d/%m/%Y')} - Memo: {t.memo} - Valor: {t.valor}")
            id_list.append(t.id)

        identificador_selecionado = input("Qual o id da transação que gostaria de processar? (id): ")
        if not identificador_selecionado.isnumeric() or int(identificador_selecionado) not in id_list:
            self.print_error(f"O id informado não corresponde a nenhuma das transações encontradas.\n"
                             f"Opções válidas são: {id_list}")
            tentar_novamente = input("Deseja tentar novamente? (s/n): ")
            if tentar_novamente.lower() == 's':
                return self.selecionar_transacao(identificador_fatura, transacao_qs)

            raise ImportacaoCanceladaException()

        identificador_fatura = identificador_selecionado
        transacao = Transacao.objects.filter(pk=identificador_fatura).first()

        if not transacao:
            self.print_error(f"Não foi possível encontrar a transação com o id {identificador_fatura}")
            raise ImportacaoCanceladaException()

        return transacao

    def confirmar_extracao_dados(self, transacao, txt_file_path):
        self.print_success(f"Transação encontrada: \n "
                           f"Id: {transacao.id} - Data: {transacao.data.strftime('%d/%m/%Y')} - Memo: {transacao.memo} "
                           f"- Valor: {transacao.valor} \n"
                           f"Arquivo da fatura: \n{txt_file_path}\n")
        confirmacao = input("Confirma a extração do dados? (s/n): ")

        if confirmacao.lower() != 's':
            raise ImportacaoCanceladaException()
        return True

    def verifica_valores(self, transacao_pagamento_cartao_valor, valor_items_extratidos):
        if abs(valor_items_extratidos) != abs(transacao_pagamento_cartao_valor):
            self.print_error(
                f"\n\nO valor da fatura ({valor_items_extratidos}) é diferente do "
                f"valor da transação ({transacao_pagamento_cartao_valor})")
            raise ImportacaoCanceladaException()

    def print_success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def print_error(self, message):
        self.stdout.write(self.style.ERROR(message))

    def print_warning(self, message):
        self.stdout.write(self.style.WARNING(message))


# Função para projetar despesas parceladas
def project_transactions(numero_cartao,
                         transacao_pagamento_cartao_data,
                         data_da_compra,
                         memo,
                         contador_memo,
                         categoria,
                         valor,
                         parcela_atual,
                         total_de_parcelas,
                         parcelas_restantes):
    projected_transactions = []

    for i in range(1, parcelas_restantes + 1):
        projected_date = transacao_pagamento_cartao_data + relativedelta(months=1 * i)
        projected_memo = re.sub(r'\d+/\d+', f"{parcela_atual + i}/{total_de_parcelas}", memo)

        identificacao = (f"Item parcelado fatura do cartão {numero_cartao}|"
                         f"{data_da_compra.strftime('%d/%m/%Y')}|"
                         f"{projected_memo}|"
                         f"{valor}|"
                         f"#{contador_memo}")

        observacao = (f"Item parcelado da fatura do cartão de crédito {numero_cartao} paga em "
                      f"{transacao_pagamento_cartao_data.strftime('%d/%m/%Y')}")

        transaction_dict = {
            'identificacao': identificacao,
            'memo': projected_memo,
            'tipo': 'S',
            'data': projected_date,
            'valor': valor,
            'observacao': observacao,
            'categoria': categoria,
            'efetivado': False,
        }
        projected_transactions.append(transaction_dict)

    return projected_transactions


# Excecao para quando o usuario cancela a importacao
class ImportacaoCanceladaException(Exception):
    pass
