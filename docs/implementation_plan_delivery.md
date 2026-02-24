# Delivery Agent Workflow Verification & Enhancement

The goal is to ensure the delivery agent registration and login workflow is complete and that SuperAdmin has the necessary tools to approve or reject these agents.

## Proposed Changes

### [Backend] [deliveryAgent]
- No changes needed to the models or registration logic as they are already robust.

### [Backend] [superAdmin]
#### [MODIFY] [views.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/views.py)
- Update `admin_dashboard` to include delivery agent statistics.
- Add `manage_delivery_requests` view to list pending agents.
- Add `delivery_request_detail` view to see agent information and documents.
- Add `approve_delivery_agent` and `reject_delivery_agent` views for handling approvals.
- Add `manage_delivery_agents` view to list all agents with block/unblock capabilities.

#### [MODIFY] [urls.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/urls.py)
- Add URL patterns for the new delivery agent management views.

### [Frontend] [superAdmin Templates]
#### [MODIFY] [admin_dashboard.html](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/templates/mainApp/admin_dashboard.html)
- Add stats cards for delivery agents.
- Add navigation links for agent management.

#### [NEW] [manage_delivery_requests.html](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/templates/mainApp/manage_delivery_requests.html)
- List view for pending agent requests.

#### [NEW] [delivery_request_detail.html](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/templates/mainApp/delivery_request_detail.html)
- Detailed view of an agent's application including profile and vehicle info.

#### [NEW] [approve_delivery_agent.html](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/templates/mainApp/approve_delivery_agent.html)
- Simple form to confirm approval.

#### [NEW] [reject_delivery_agent.html](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/superAdmin/templates/mainApp/reject_delivery_agent.html)
- Form to provide a reason for rejection.

## Verification Plan
### Automated Tests
- N/A (Manual verification preferred for UI flows).

### Manual Verification
1. Register a new delivery agent via the frontend (`/delivery/login` -> Sign Up).
2. Log in as Admin and verify the new request appears on the dashboard.
3. Access the request detail, verify info, and approve the agent.
4. Verify the agent can now log in to the delivery dashboard.
5. Repeat for rejection and verify the agent is blocked from logging in with a clear message.
