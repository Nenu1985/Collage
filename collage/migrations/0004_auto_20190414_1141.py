# Generated by Django 2.1.7 on 2019-04-14 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collage', '0003_auto_20190412_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(default=128)),
            ],
        ),
        migrations.AlterField(
            model_name='collage',
            name='photo_size',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='collage.PhotoSize'),
        ),
    ]
