from django.db import models


# model para gravar o saldo final de cada mês para ser usando no calculo do mes seguinte
class SaldoFinal(models.Model):
    mes = models.IntegerField(verbose_name='Mês')
    ano = models.IntegerField(verbose_name='Ano')
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-mes']
        verbose_name = 'Saldo Final'
        verbose_name_plural = 'Saldos Finais'
        unique_together = ['mes', 'ano']

    def __str__(self):
        return f"Saldo Final {self.mes.strftime('%m/%Y')} - {self.valor}"
