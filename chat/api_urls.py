from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('events/', views.EventListAPIView.as_view(), name='event-list'),
    path('events/create/', views.EventCreateAPIView.as_view(), name='event-create'),
    path('register/', views.RegisterAPIView.as_view(), name='user-register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # refreshトークンによるaccessトークンの再取得
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),  # 全category取得
    # 特定のカテゴリーのサブカテゴリーを取得
    path('categories/<int:category_id>/subcategories/', views.SubCategoriesByCategoryAPIView.as_view(), name='subcategories-by-category'),
    # サブカテゴリーのURLパターン
    path('subcategories/', views.SubCategoryListAPIView.as_view(), name='subcategory-list'),

]
