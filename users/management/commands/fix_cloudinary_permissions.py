"""
Management command to fix Cloudinary file permissions
Converts private files to public access
"""
from django.core.management.base import BaseCommand
import cloudinary
import cloudinary.api
from users.models import Document


class Command(BaseCommand):
    help = 'Fix Cloudinary file permissions to make PDFs publicly accessible'

    def handle(self, *args, **options):
        self.stdout.write('Fixing Cloudinary file permissions...')
        
        # Get all documents with files
        documents = Document.objects.exclude(file='')
        
        fixed_count = 0
        error_count = 0
        
        for doc in documents:
            try:
                if doc.file:
                    # Get the public_id from the CloudinaryField
                    public_id = doc.file.public_id
                    
                    # Update the resource to public
                    cloudinary.api.update(
                        public_id,
                        resource_type='raw',  # PDFs are stored as 'raw' type
                        type='upload',
                        access_mode='public'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Fixed: {doc.title} ({public_id})')
                    )
                    fixed_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error fixing {doc.title}: {str(e)}')
                )
                error_count += 1
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✓ Fixed: {fixed_count} files'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {error_count} files'))
        self.stdout.write('='*50)
