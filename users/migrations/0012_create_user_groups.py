from django.db import migrations

def create_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='RestaurantOwner')
    Group.objects.get_or_create(name='Customer')

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # Update to your latest migration
    ]

    operations = [
        migrations.RunPython(create_user_groups),
    ]