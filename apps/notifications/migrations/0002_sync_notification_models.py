from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notificationpreference',
            old_name='email_new_message',
            new_name='email_chat',
        ),
        migrations.RenameField(
            model_name='notificationpreference',
            old_name='email_booking_updates',
            new_name='email_booking',
        ),
        migrations.RenameField(
            model_name='notificationpreference',
            old_name='push_new_message',
            new_name='push_chat',
        ),
        migrations.RenameField(
            model_name='notificationpreference',
            old_name='push_booking_updates',
            new_name='push_booking',
        ),
        migrations.AddField(
            model_name='notificationpreference',
            name='email_system',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notificationpreference',
            name='push_system',
            field=models.BooleanField(default=True),
        ),
        migrations.RemoveField(
            model_name='pushsubscription',
            name='updated_at',
        ),
    ]
