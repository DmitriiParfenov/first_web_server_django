# Generated by Django 4.2.3 on 2023-08-10 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_alter_product_is_published'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-published',), 'permissions': [('set_published', 'Can publish Продукт')], 'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterField(
            model_name='product',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='Опубликовано'),
        ),
    ]