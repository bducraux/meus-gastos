# Generated by Django 4.2.4 on 2023-08-16 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transacoes', '0004_alter_planejamento_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transacao',
            name='observacao',
            field=models.TextField(blank=True, null=True, verbose_name='Observação'),
        ),
    ]
