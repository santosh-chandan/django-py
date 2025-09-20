from django.contrib import admin
from .models import Post
from app.comments.models import Comment

# -----------------------------
# Inline example (if Post had comments, tasks, etc.)
# -----------------------------
class CommentInline(admin.TabularInline):
    model = Comment  # assume you have Comment model related to Post
    extra = 1         # Number of empty forms to display
    readonly_fields = ['created_at', 'updated_at']
    fields = ('author', 'content', 'created_at', 'updated_at')
    show_change_link = True

# -----------------------------
# Post Admin
# -----------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'id', 
        'title', 
        'user', 
        'is_published', 
        'created_at', 
        'updated_at'
    )
    
    # Make some fields clickable to go to change form
    list_display_links = ('id', 'title')

    # Filters on right sidebar
    list_filter = ('is_published', 'created_at', 'user')
    
    # Add search capability for quick lookup
    search_fields = ('title', 'body', 'user__username')
    
    # Fields that are read-only in admin form
    readonly_fields = ('id', 'user', 'created_at', 'updated_at')
    
    # Fields shown in the edit/add form
    fields = ('title', 'body', 'user', 'is_published', 'created_at', 'updated_at')
    
    # Inline related objects
    inlines = [CommentInline]

    # Ordering by newest first
    ordering = ('-created_at',)

    # -----------------------------
    # Custom actions
    # -----------------------------
    # -----------------------------
    # Modern style actions
    # -----------------------------
    @admin.action(description="Mark selected posts as published")
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} post(s) marked as published.")

    @admin.action(description="Mark selected posts as unpublished")
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} post(s) marked as unpublished.")

    # -----------------------------
    # Auto-set user on save
    # -----------------------------
    def save_model(self, request, obj, form, change):
        """
        Automatically set user if creating new object
        """
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    # -----------------------------
    # Object-level permission (read-only for non-users)
    # -----------------------------
    def get_readonly_fields(self, request, obj=None):
        """
        Make fields readonly for non-user users
        """
        ro_fields = list(self.readonly_fields)
        if obj and obj.user != request.user and not request.user.is_superuser:
            # Make all fields readonly for non-user
            ro_fields += ['title', 'body', 'is_published']
        return ro_fields

    def has_change_permission(self, request, obj=None):
        """
        Only users or superusers can edit
        """
        if obj is None:
            return True  # To show list view
        return obj.user == request.user or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """
        Only users or superusers can delete
        """
        if obj is None:
            return True
        return obj.user == request.user or request.user.is_superuser


'''

Django admin calls it internally

In the Django admin, the ModelAdmin class defines certain hooks to check permissions. Some of the important ones are:

Method	When Django admin calls it
has_add_permission(self, request)	When rendering the "Add" button/form
has_change_permission(self, request, obj=None)	When rendering the list view or change form
has_delete_permission(self, request, obj=None)	When rendering the "Delete" button/form
has_view_permission(self, request, obj=None)	When rendering list/detail views in Django 2.1+



How Django uses it internally:

When you visit a change page, Django calls admin.has_change_permission(request, obj) to see if you are allowed to edit that object.

When you click the Delete button in the admin, Django calls admin.has_delete_permission(request, obj) to see if the button should appear and whether the deletion is allowed.

These methods return True or False, and Django enforces permissions accordingly.


Signature matters
def has_delete_permission(self, request, obj=None):


self → the ModelAdmin instance

request → the current HttpRequest (contains user, session, etc.)

obj → the specific model instance (if None, usually the list view)


Django admin internally calls this every has_delete_permission ( like ) it needs to check deletion rights, so your logic runs automatically in that context.

'''

'''

Hook	When it runs
save_model	Before saving object
delete_model	Before deleting object
get_queryset	When fetching list of objects
get_readonly_fields	When rendering the form
has_change_permission	When checking if user can edit
has_delete_permission	When checking if user can delete
get_form	Customize form dynamically

'''
