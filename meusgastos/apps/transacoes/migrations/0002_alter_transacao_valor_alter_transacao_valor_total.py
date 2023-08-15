# Generated by Django 4.2.4 on 2023-08-09 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transacoes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='valor',
            field=models.DecimalField(decimal_places=2, help_text='Valor da transação, sem os items.', max_digits=10, verbose_name='Valor'),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='valor_total',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Valor total da transação, incluindo os items.', max_digits=10, verbose_name='Valor Total'),
        ),
    ]
