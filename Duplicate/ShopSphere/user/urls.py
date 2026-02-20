from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('user_login', views.login_api, name='user_login'),
    path('google_login', views.google_login_api, name='google_login'),
    path('register', views.register_api, name='register'),
    path('logout', views.logout_api, name='logout'),

    # Shop / Product
   
    path('', views.home_api, name='user_products'),
    path('products', views.home_api, name='user_products_json'),
    path('product/<int:product_id>', views.product_detail, name='user_product_detail'),
    path('submit_review/<int:product_id>', views.submit_review_api, name='submit_review_api'),

    # Cart
    path('cart', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    
    
    path('checkout', views.checkout_view, name='checkout'),
    path('process_payment', views.process_payment, name='process_payment'),

    # User Profile / Orders
    path('my_orders', views.my_orders, name='my_orders'),
    path('address', views.address_page, name="address_page"),
    path('delete-address/<int:id>', views.delete_address, name="delete_address"),
    path('update-address/<int:id>', views.update_address, name="update_address"),

    #Reviews
#     '''path('my_reviews', views.user_reviews, name='user_reviews'),
#     path('submit_review/<int:product_id>', views.submit_review, name='submit_review'),
    path('delete_review/<int:product_id>', views.delete_review_api, name='delete_review_api'),
#     path('edit_review/<int:review_id>', views.edit_review, name='edit_review'),'''
#     path('review_product/<int:product_id>', views.review_product, name='review_product')
    path('trending/', views.trending_products, name='trending_products'),   

    # Auth / Forgot Password
    path('auth/', views.auth_page, name='auth'),

    # --- Password Reset URLs ---
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]