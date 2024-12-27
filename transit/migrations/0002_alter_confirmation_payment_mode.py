# Generated by Django 5.1 on 2024-11-24 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='payment_mode',
            field=models.CharField(choices=[('cash', 'Cash'), ('card', 'Card'), ('online', 'Online')], default='cash', max_length=20),
        ),
    ]