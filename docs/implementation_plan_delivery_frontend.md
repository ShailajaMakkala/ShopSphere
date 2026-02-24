# Implementation Plan: Delivery Agent Workflow Enhancements

This plan outlines the enhancements to the delivery agent (and vendor) login and dashboard experience, ensuring better feedback for pending or rejected accounts.

## Proposed Changes

### [Backend] [user/views.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/user/views.py)
- Refine `login_api` to return distinct status messages for `pending` vs `rejected` accounts (both for delivery and vendors).
- Include the `rejection_reason` in the response when an account is rejected.

### [Frontend] [DeliveryAgentLogin.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/ShopSphere_Frontend/src/Pages/delivery/DeliveryAgentLogin.jsx)
- Update `handleLoginSubmit` to parse the `status` from the backend error response.
- Add a new UI state or specific modal to show "Pending Approval" or "Rejection" details clearly to the user instead of just a toast.

### [Frontend] [dashboard.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/ShopSphere_Frontend/src/Pages/delivery/dashboard.jsx)
- Add error handling for the dashboard fetch that redirects to the login page if a 403 (Blocked/Pending) is returned, showing the appropriate message.

## Verification Plan

### Manual Verification
1.  **Pending State**: Try logging in with a newly registered (pending) agent. Verify the dashboard or login page shows a clear "Awaiting Approval" message.
2.  **Rejected State**: Reject an agent from the Admin panel with a specific reason. Try logging in as that agent and verify the reason is displayed.
3.  **Blocked State**: Block an active agent from the Admin panel. Verify that their dashboard session is terminated or they are informed upon refresh.
