from django.contrib import admin
from .models import ChatHistory, UserProfile

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query_preview', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'query', 'response')
    date_hierarchy = 'timestamp'
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('user__username', 'user__email')