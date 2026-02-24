# Admin Order Management & Tracking Implementation Plan

This plan outlines the steps to add order listing, detailed order views, and tracking capabilities to the ShopSphere Admin Dashboard.

## Proposed Changes

### Backend (Duplicate/ShopSphere/superAdmin)

#### [MODIFY] [serializers.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/serializers.py)
- Import `Order`, `OrderItem`, `Address`, `OrderTracking` from `user.models`.
- Add `AdminOrderListSerializer` for summary views.
- Add `AdminOrderDetailSerializer` for detailed views including items and tracking.

#### [MODIFY] [api_views.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/api_views.py)
- Implement `AdminOrderViewSet` using `viewsets.ReadOnlyModelViewSet`.
- Include filtering by status and order number.

#### [MODIFY] [api_urls.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/api_urls.py)
- Register `router.register(r'orders', AdminOrderViewSet, basename='admin_orders')`.

---

### Frontend (ShopSphere_Frontend/Adminservice)

#### [NEW] [OrderManagement.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/admin/OrderManagement.jsx)
- List view for all orders with columns for Order ID, Customer, Amount, Status, and Date.
- Search and filter functionality.

#### [NEW] [OrderDetail.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/admin/OrderDetail.jsx)
- Detailed view of a single order.
- Display customer information, shipping address, and line items.
- Visual tracking timeline for order status updates.

#### [MODIFY] [App.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/App.jsx)
- Add routes for `/orders` and `/orders/:id`.

#### [MODIFY] [Sidebar.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/components/Sidebar.jsx)
- Add "Orders" to the navigation menu.

#### [MODIFY] [AdminDashboard.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/admin/AdminDashboard.jsx)
- Add order-related statistics (Total Orders, Pending, Delivered).
- Link stats cards to the filtered Order Management page.

#### [MODIFY] [axios.js](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/Adminservice/src/api/axios.js)
- Add `fetchOrders`, `fetchOrderDetail`, and `updateOrderStatus` functions.

## Verification Plan

### Automated Tests
- Verify API responses for the new order endpoints using terminal scripts.

### Manual Verification
- Navigate to the new Orders page from the sidebar.
- Click an order to view its details and verify tracking history is displayed.
- Test filtering by status.
