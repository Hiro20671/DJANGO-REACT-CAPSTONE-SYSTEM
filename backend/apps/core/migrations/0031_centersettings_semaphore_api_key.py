from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_textblastlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='centersettings',
            name='semaphore_api_key',
            field=models.CharField(blank=True, help_text='Semaphore SMS Gateway API key', max_length=255, null=True),
        ),
    ]
