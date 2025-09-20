from django.contrib import admin
from app.users.models import userProfile

@admin.register(userProfile)
class userAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'level')
    list_display_links = ('username',)
    list_filter = ('email',)
    search_fields = ('email', 'user__username')  # '__' ORM is works for onnly search
    ordering = ('-id',)
    readonly_fields = ('id', 'username')

    fieldsets = (
        ('Main', {'fields': ('email', 'level')}),
        ('Meta', {'fields': ('id', 'user__username')} ),
    )

    actions = ['set_level_1', 'set_level_2']

    def set_level_1(self, request, queryset):
        queryset.update(level=1)
    set_level_1.short_description = 'Level 1'

    def set_level_2(self, request, queryset):
        queryset.update(level=2)
    set_level_2.short_description = 'Level 2'

    # short_description - header title
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        return super().save_model(request, obj, form, change)


'''

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import userProfile

class UserProfileInline(admin.StackedInline):
    model = userProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Unregister default UserAdmin
admin.site.unregister(User)

# Extend UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


'''
