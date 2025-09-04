# Generated manually for current location fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_transaction_device_fingerprint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='current_lat',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Current transaction latitude', max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='current_lng',
            field=models.DecimalField(blank=True, decimal_places=6, help_text='Current transaction longitude', max_digits=9, null=True),
        ),
    ]