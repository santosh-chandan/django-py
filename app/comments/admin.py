from django.contrib import admin
# Register your models here.
from django.utils.html import format_html
from .models import Comment

# -----------------------------
# Comment Admin
# -----------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # -----------------------------
    # List display with color-coded status
    # -----------------------------
    list_display = ('id', 'content', 'author', 'created_at', 'updated_at')
    list_display_links = ('id', 'author')
    list_filter = ('author', 'created_at')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)
    
    # -----------------------------
    # Read-only fields
    # -----------------------------
    readonly_fields = ('id', 'author', 'created_at', 'updated_at')

    # -----------------------------
    # Collapsible Fieldsets
    # -----------------------------
    fieldsets = (
        ('Main', {'fields': ('author', 'post', 'content')}),
        ('Meta', {'fields': ('created_at', 'updated_at')}),
    )

    # -----------------------------
    # Colored Status
    # -----------------------------
    # def colored_status(self, obj):
    #     """
    #     Display 'Published' in green, 'Draft' in red.
    #     """
    #     color = "green" if obj.is_published else "red"
    #     status = "Published" if obj.is_published else "Draft"
    #     return format_html('<b><span style="color: {};">{}</span></b>', color, status)
    # colored_status.short_description = 'Status'
    # colored_status.admin_order_field = 'is_published'

    # -----------------------------
    # Auto-set owner on save
    # -----------------------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # -----------------------------
    # Object-level permissions
    # -----------------------------
    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if obj and obj.author != request.user and not request.user.is_superuser:
            ro_fields += ['title', 'body', 'is_published']
        return ro_fields

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True  # allow access to list view
        return obj.author == request.user or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.author == request.user or request.user.is_superuser


'''

Features explained

CommentInline - Edit comments related to each post directly on the Post admin page. Supports readonly timestamps and change links.

colored_status - Dynamically shows Published in green and Draft in red in the admin list. Makes scanning easy.

fieldsets - Organizes fields into sections: collapsible Post Content and Meta Info, wide section for publication controls.

inlines - Shows related models (comments) right inside the post form. Can add/remove inline objects.

Custom actions (make_published, make_unpublished) - Run bulk actions from list view.

Auto-set owner - save_model ensures that new posts automatically belong to the logged-in user.

Object-level permissions - Non-owners cannot edit or delete posts (except superusers).

Read-only fields - Prevent critical metadata (owner, created_at, updated_at) from being edited.

Collapsible sections - Makes forms cleaner for long content.

'''
