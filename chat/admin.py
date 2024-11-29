from django.contrib import admin
from .models import Event, CustomUser, Category, SubCategory, Hashtag


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'sent_at', 'event')
    search_fields = ('user__username', 'message')


admin.site.register(Hashtag)
admin.site.register(Event)
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(SubCategory)
