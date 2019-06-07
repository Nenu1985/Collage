# Generated by Django 2.2.2 on 2019-06-05 07:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collage', '0006_collage_final_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='valid',
        ),
        migrations.AlterField(
            model_name='cutphoto',
            name='photo_src',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='collage.Photo'),
        ),
        migrations.DeleteModel(
            name='Collage',
        ),
    ]
