# Refactoring Frontend Ledger System

This plan outlines the steps to integrate the refactored, consolidated ledger data into the React frontend. This will ensure that vendors and administrators can see unified financial activity in a professional table format.

## Proposed Changes

### [Backend] API Layer
#### [MODIFY] [serializers.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/finance/serializers.py)
- Update `LedgerEntrySerializer` to include `gross_amount`, `commission_amount`, `net_amount`, and `order_number`.

### [Frontend] Vendor Dashboard
#### [MODIFY] [Earnings.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/ShopSphere_Frontend/src/Pages/vendor/Earnings.jsx)
- Update the "Recent Activity" list to show consolidated data rows.
- Display Gross Amount, Commission, and Net Earned for each revenue entry.
- Add "Order #" column reference where applicable.

#### [MODIFY] [Dashboard.jsx](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/ShopSphere_Frontend/ShopSphere_Frontend/src/Pages/vendor/Dashboard.jsx)
- Ensure the overview stats reflect the new logic (it should already work if using the summary API, but worth checking).

## Verification Plan

### Manual Verification
- Log in as a vendor in the React app.
- Navigate to the Earnings page.
- Verify that recent activities show the complete financial breakdown (Gross, Commission, Net).
- Check that the amounts match the backend consolidated logic.
