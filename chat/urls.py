from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/search/', views.event_search, name='event_search'),
    path('event/<int:pk>/join/', views.join_event, name='join_event'),
    path('event/<int:pk>/chat/', views.chat_room, name='chat_room'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/<int:id>/', views.profile, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
