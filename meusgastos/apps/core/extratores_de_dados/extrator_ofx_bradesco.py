from sqlite3 import IntegrityError
from ofxtools.Parser import OFXTree
from ofxtools.Types import OFXSpecError
from meusgastos.apps.transacoes.models import Transacao
from meusgastos.apps.transacoes.utils import auto_categorize_transaction, is_transaction_ignored


def extrator_ofx_bradesco(ofx_file_path: str) -> bool:
    """
    Extrai as transações de um arquivo OFX do Bradesco e grava as transações no banco de dados.
    :param ofx_file_path: str - Caminho para o arquivo OFX
    :return: bool - True se as transações foram gravadas com sucesso
    :raises: ValueError - Se o arquivo OFX não for válido ou se ocorrer algum erro ao gravar as transações
    """
    # Initialize the OFX tree
    ofx_tree = OFXTree()
    # Parse the OFX file
    with open(ofx_file_path, 'rb') as ofx_file:
        ofx_tree.parse(ofx_file)
    try:
        # Get the OFX object
        ofx = ofx_tree.convert()
    except OFXSpecError as e:
        raise ValueError(f"O arquivo OFX não é válido: {e}")
    # Extract the bank_transactions
    if ofx is not None:
        try:
            for bank_account in ofx.statements:
                for bank_transaction in bank_account.transactions:
                    # check memo encoding
                    if isinstance(bank_transaction.memo, bytes):
                        bank_transaction.memo = bank_transaction.memo.decode('utf-8')

                    transaction_dict = {
                        'memo': bank_transaction.memo,
                        'tipo': 'E' if bank_transaction.trntype == "CREDIT" else 'S',
                        'data': bank_transaction.dtposted.date(),
                        'valor': bank_transaction.trnamt,
                        'valor_total': bank_transaction.trnamt,
                        'efetivado': True,
                    }
                    if is_transaction_ignored(bank_transaction.memo):
                        transaction_dict['status'] = Transacao.STATUS_IGNORED

                    categoria = auto_categorize_transaction(bank_transaction.memo)
                    if categoria is not None:
                        transaction_dict['categoria'] = categoria

                    # Seta a identificação da transação
                    identificacao = (f"{bank_transaction.checknum}|"
                                     f"{bank_transaction.dtposted.date()}|"
                                     f"{bank_transaction.trntype}|"
                                     f"{bank_transaction.trnamt}")

                    Transacao.objects.update_or_create(
                        identificacao=identificacao,
                        defaults=transaction_dict
                    )
            return True
        except IntegrityError as e:
            raise ValueError(f"Não foi possível importar as transações: {e}")
