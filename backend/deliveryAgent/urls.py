from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Template Views
    path('', views.agent_portal, name='agentPortal'),
    path('login/', views.agent_portal, name='agentLogin'),
    path('register/', views.agent_portal, name='agentRegister'),
    path('logout/', LogoutView.as_view(next_page='agentPortal'), name='logout'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    
    # Order Status Transitions (Templates)
    path('delivery/accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('delivery/pickup-order/<int:order_id>/', views.pickup_order, name='pickup_order'),
    path('delivery/start-transit/<int:order_id>/', views.start_transit, name='start_transit'),
    path('delivery/mark-arrived/<int:order_id>/', views.mark_arrived, name='mark_arrived'),
    path('delivery/complete-order/<int:order_id>/', views.complete_delivery_otp, name='complete_delivery_otp'),
    
    # Simulation/Redirects
    path('accept-order/<int:order_id>/', views.accept_order_sim, name='accept_order_sim'),
    
    # API v1
    path('api/', include('deliveryAgent.api_urls')),
]
