from django.db import migrations



def fix_null_slugs(apps, schema_editor):
    RestaurantProfile = apps.get_model('users', 'RestaurantProfile')
    for rp in RestaurantProfile.objects.filter(slug__isnull=True):
        rp.save()  # triggers the save method to generate a slug

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_restaurantprofile_slug'),
    ]
    operations = [
        migrations.RunPython(fix_null_slugs),
    ]
