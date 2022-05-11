# Generated by Django 4.0.4 on 2022-05-11 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('levelupapi', '0003_event_attendees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='levelupapi.game'),
        ),
    ]
