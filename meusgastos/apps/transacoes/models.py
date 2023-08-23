# coding: utf-8
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models import Sum

from meusgastos.apps.categorias.models import Categoria
from meusgastos.apps.core.utils import mes_em_portugues


class Transacao(models.Model):
    STATUS_ACTIVE = 'ativa'
    STATUS_IGNORED = 'ignorada'
    STATUS_INACTIVE = 'inativa'

    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Ativa'),
        (STATUS_IGNORED, 'Ignorada'),
        (STATUS_INACTIVE, 'Inativa'),
    )

    TYPE_INCOME = 'E'
    TYPE_EXPENSE = 'S'

    TIPOS = (
        (TYPE_INCOME, 'Entrada'),
        (TYPE_EXPENSE, 'Saída')
    )

    IGNORED_KEYWORDS = [
        'inv fac',
        'Invest Facil',
        'Apl.invest Fac',
        'Resg Automatico Investim',
        'resgate inv fac',
    ]

    id = models.BigAutoField(primary_key=True)
    identificacao = models.CharField(verbose_name='Identificação', max_length=100, unique=True, blank=True, null=True)
    memo = models.TextField(verbose_name='Memo')
    observacao = models.TextField(verbose_name='Observação', blank=True, null=True)
    valor = models.DecimalField(
        verbose_name='Valor',
        max_digits=10,
        decimal_places=2,
        help_text='Valor da transação, sem os items.'
    )
    valor_total = models.DecimalField(
        verbose_name='Valor Total',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Valor total da transação, incluindo os items.'
    )
    data = models.DateField(verbose_name='Data')
    tipo = models.CharField(verbose_name='Tipo', choices=TIPOS, default='S', max_length=1)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        verbose_name='Categoria',
        null=True,
        blank=True
    )
    efetivado = models.BooleanField(
        default=False,
        verbose_name='Efetivada',
        help_text='Diz se a transação bancária foi aplicada na conta bancária real.'
    )
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status',
        help_text='Diz se a transação pode alterar o saldo da conta bancária ou ser usada em estatísticas.'
    )

    class Meta:
        ordering = ['-data']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return self.memo

    def get_remaining_value(self):
        # Calculate the remaining value of the transaction after deducting the item values
        total_items_value = self.items.aggregate(total=Sum('valor'))['total'] or 0
        if self.tipo == 'S':
            total_items_value *= -1
        return self.valor_total - total_items_value

    def update_valor(self):
        total_items_value = self.items.aggregate(total=Sum('valor'))['total']
        self.valor = self.valor_total - (total_items_value or 0)
        self.save(update_fields=['valor'])

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.valor_total = self.valor
        super().save(*args, **kwargs)


class TransacaoItem(models.Model):
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='items')
    descricao = models.CharField(verbose_name='Descrição', max_length=100)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        verbose_name='Categoria',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.pk:  # Se for uma criação de objeto
            self.clean()

        super().save(*args, **kwargs)
        self.transacao.update_valor()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.transacao.update_valor()

    def clean(self, *args, **kwargs):
        if self.transacao.tipo == 'S':
            valor_restante = self.transacao.valor + abs(self.valor)
            if valor_restante > 0:
                raise ValidationError('O valor somado dos itens não pode exceder o valor da transação.')
        else:
            valor_restante = self.transacao.valor - abs(self.valor)
            if valor_restante < 0:
                raise ValidationError('O valor somado dos itens não pode exceder o valor da transação.')

        # Ensure that the category type is the same of the transaction or 'T' (both)
        if self.categoria:
            if self.categoria.tipo != 'T' and self.categoria.tipo != self.transacao.tipo:
                raise ValidationError('A categoria do item deve ser do mesmo tipo da transação ou "T" (ambos).')

    def __str__(self):
        return self.descricao


class Planejamento(models.Model):
    STATUS_ACTIVE = 'ativa'
    STATUS_INACTIVE = 'inativa'

    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Ativa'),
        (STATUS_INACTIVE, 'Inativa'),
    )

    mes = models.DateField(verbose_name='Mês')
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    repeticoes = models.IntegerField(
        default=0,
        verbose_name='Repetições',
        help_text='Quantidade de meses que o planejamento deve ser repetido. 0 para se repetir mensalmente.'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        verbose_name='Categoria',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status',
        help_text='Diz se o planejamento pode alterar o saldo da conta bancária ou ser usado em estatísticas.'
    )

    class Meta:
        ordering = ['-mes']
        verbose_name = 'Planejamento'
        verbose_name_plural = 'Planejamentos'

    def __str__(self):
        return f"Planejamento {self.mes.strftime('%m/%Y')} - {self.categoria}"

    @staticmethod
    def get_planejamentos_ativos_do_mes(month: date):
        """
        Get all active planejamentos that are not expired
        :param month: date
        :return:
        """
        planejamentos = Planejamento.objects.filter(
            Q(mes__month__lte=month.month) &
            Q(status=Planejamento.STATUS_ACTIVE)
        )

        active_planejamentos = [planejamento for planejamento in planejamentos if
                                planejamento.repeticoes == 0 or planejamento.mes.month >= (month - relativedelta(
                                    months=(planejamento.repeticoes-1))).month]

        return active_planejamentos

    @staticmethod
    def gerar_lista_planejamento_anual(data_inicio: date) -> dict:
        """
        Gera uma lista com os gastos planejados para o ano começando na data_inicio
        retornando um dicionário: {'Janeiro': {'Aluguel': 1000}, 'Fevereiro': {'Aluguel': 1000}}
        :param data_inicio: date - data de início da lista
        :return: dict - dict com os gastos planejados para o ano
        """
        planejamento_anual = {}
        for i in range(12 - data_inicio.month + 1):
            mes_atual = (data_inicio.month + i - 1) % 12 + 1
            data_atual = date(year=data_inicio.year, month=mes_atual, day=1)

            planejamentos_ativos = Planejamento.get_planejamentos_ativos_do_mes(data_atual)

            planejamento_mes = {}
            valor_total_mes = Decimal('0.00')
            for planejamento in planejamentos_ativos:
                valor_total_mes += planejamento.valor
                planejamento_mes[planejamento.categoria.descricao] = planejamento.valor
            planejamento_mes['total'] = valor_total_mes

            planejamento_anual[mes_em_portugues(mes_atual)] = planejamento_mes

        return planejamento_anual
