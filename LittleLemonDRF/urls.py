from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu-items/', views.menu_items),
    # path('menu-items/<int:id>', views.single_item),
    # path('secret/', views.secret),
    # path('roles/', views.roles),
    # path('api-token-auth/', obtain_auth_token),
    # path('throttle-check/', views.throttle_check),
    # path('throttle-check-auth/', views.throttle_check_auth),
    # path('me/', views.me),
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:ids>', views.manager_removal),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:ids>', views.delivery_crew_removal),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('category', views.CategoriesView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),

]