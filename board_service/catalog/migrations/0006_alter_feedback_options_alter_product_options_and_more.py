# Generated by Django 4.2.3 on 2023-07-12 09:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_feedback_country'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedback',
            options={'ordering': ['-publish'], 'verbose_name': 'Обратная связь', 'verbose_name_plural': 'Обратные связи'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-changed'], 'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AddField(
            model_name='feedback',
            name='publish',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='Дата публикации'),
            preserve_default=False,
        ),
    ]
