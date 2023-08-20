# Generated by Django 4.2.3 on 2023-08-16 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_rename_ingredients_ingredient_rename_tags_tag_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='count',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=20, verbose_name='Единицы измерения'),
        ),
    ]