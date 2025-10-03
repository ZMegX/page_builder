from .models import Order, Review, Document
from django.contrib import admin
from users.models import RestaurantProfile

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer__username', 'restaurant__name', 'id')
    
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'registration_number', 'cuisine_type', 'phone_number', 'logo',  )
    list_filter = ('theme_choice', 'name',)
    search_fields = ('name', 'registration_number', 'cuisine_type', 'phone_number',)
admin.site.register(RestaurantProfile, RestaurantProfileAdmin)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'reviewer_name', 'rating', 'has_owner_reply', 'is_approved', 'created_at')
    list_filter = ('restaurant', 'is_approved', 'rating', 'reply_created_at')
    search_fields = ('reviewer_name', 'comment', 'owner_reply')
    readonly_fields = ('created_at', 'reply_created_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('restaurant', 'user', 'reviewer_name', 'rating', 'comment', 'created_at', 'is_approved')
        }),
        ('Owner Reply', {
            'fields': ('owner_reply', 'reply_created_at'),
            'classes': ('collapse',),
        }),
    )
    
    def has_owner_reply(self, obj):
        return obj.has_reply()
    has_owner_reply.boolean = True
    has_owner_reply.short_description = 'Has Reply'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'doc_type', 'order', 'is_published', 'view_count', 'created_at')
    list_filter = ('category', 'doc_type', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_published')
    readonly_fields = ('embed_url', 'view_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'doc_type', 'order')
        }),
        ('File Upload', {
            'fields': ('file',),
            'description': 'Upload a PDF or image file (for PDFs, screenshots, etc.)'
        }),
        ('Google Doc Link', {
            'fields': ('google_doc_url', 'embed_url'),
            'description': 'Paste the sharing link from Google Docs/Slides/Sheets. Embed URL will be auto-generated.'
        }),
        ('Status', {
            'fields': ('is_published', 'view_count', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Regenerate embed URL if Google Doc URL changed
        if obj.google_doc_url:
            obj.embed_url = obj.generate_embed_url()
        super().save_model(request, obj, form, change)