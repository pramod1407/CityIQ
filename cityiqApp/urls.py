from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chat-history/', views.get_chat_history, name='chat_history'),
    path('api/clear-chat/', views.clear_chat, name='clear_chat'),
]