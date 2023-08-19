from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from users.models import Subscribe, User


@register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    list_display = ('user', 'author',)
