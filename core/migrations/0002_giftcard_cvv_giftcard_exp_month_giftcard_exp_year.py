# Generated by Django 5.1.6 on 2025-02-21 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcard',
            name='cvv',
            field=models.CharField(default='0000', max_length=4),
        ),
        migrations.AddField(
            model_name='giftcard',
            name='exp_month',
            field=models.CharField(default='01', max_length=2),
        ),
        migrations.AddField(
            model_name='giftcard',
            name='exp_year',
            field=models.CharField(default='2025', max_length=4),
        ),
    ]
