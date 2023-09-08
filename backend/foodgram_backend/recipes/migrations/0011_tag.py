# Generated by Django 3.2 on 2023-08-26 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0010_auto_20230824_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('color', models.CharField(max_length=7)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
        ),
    ]