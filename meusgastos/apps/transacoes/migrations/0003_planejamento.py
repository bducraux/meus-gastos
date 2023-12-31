# Generated by Django 4.2.4 on 2023-08-09 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categorias', '0001_initial'),
        ('transacoes', '0002_alter_transacao_valor_alter_transacao_valor_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='Planejamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.DateField(verbose_name='Mês')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor')),
                ('repetir_mensalmente', models.BooleanField(default=False, help_text='Diz se o planejamento deve ser repetido para os próximos meses.', verbose_name='Repetir mensalmente')),
                ('repeticoes', models.IntegerField(default=0, help_text='Quantidade de meses que o planejamento deve ser repetido. \n0 para se repetir indefinidamente. \nRequer que a opção "Repetir mensalmente" esteja marcada.', verbose_name='Repetições')),
                ('status', models.CharField(choices=[('ativa', 'Ativa'), ('inativa', 'Inativa')], default='ativa', help_text='Diz se o planejamento pode alterar o saldo da conta bancária ou ser usado em estatísticas.', max_length=8, verbose_name='Status')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='categorias.categoria', verbose_name='Categoria')),
            ],
            options={
                'verbose_name': 'Planejamento Mensal',
                'verbose_name_plural': 'Planejamentos Mensais',
                'ordering': ['-mes'],
            },
        ),
    ]
