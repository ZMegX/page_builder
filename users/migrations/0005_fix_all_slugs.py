from django.db import migrations
from django.utils.text import slugify

def fix_all_slugs(apps, schema_editor):
    RestaurantProfile = apps.get_model('users', 'RestaurantProfile')
    for rp in RestaurantProfile.objects.all():
        # Generate slug using the same logic as your model
        base = getattr(rp, 'name', None)
        if not base:
            if getattr(rp, 'profile', None) and getattr(rp.profile, 'user', None):
                base = rp.profile.user.username
            elif getattr(rp, 'user', None) and getattr(rp.user, 'username', None):
                base = rp.user.username
            else:
                base = str(rp.pk)
        rp.slug = slugify(base)
        rp.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_fix_null_slugs'),  
    ]
    operations = [
        migrations.RunPython(fix_all_slugs),
    ]
