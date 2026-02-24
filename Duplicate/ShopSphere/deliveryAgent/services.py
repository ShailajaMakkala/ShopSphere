"""
deliveryAgent/services.py
Auto-assignment service: matches a confirmed order to the best available
delivery agent in the same city or service area.
"""
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import DeliveryAgentProfile, DeliveryAssignment, DeliveryTracking


import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')
        
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def auto_assign_order(order):
    """
    Try to auto-assign `order` to the best available delivery agent.

    Matching criteria:
      1. Pincode Match (Tier 1)
      2. City Match (Tier 2)
      
    Priority within Tiers:
      - Physical Proximity (if coordinates available)
      - Workload (fewest active assignments)
    """
    # ── Determine delivery city from order ──────────────────────────────────
    delivery_address = getattr(order, 'delivery_address', None)
    if not delivery_address:
        return None

    delivery_city = (delivery_address.city or '').strip().lower()
    delivery_state = (delivery_address.state or '').strip().lower()
    delivery_pincode = (delivery_address.pincode or '').strip()
    delivery_lat = delivery_address.latitude
    delivery_lon = delivery_address.longitude

    # Removed immediate return if no city, to allow global fallback if one agent is available

    # ── Guard: already has an assignment ────────────────────────────────────
    if DeliveryAssignment.objects.filter(order=order).exists():
        return None

    # ── Find all eligible agents ─────────────────────────────────────────
    # We include all approved, active, and non-blocked agents.
    # We will prioritize 'available' and 'on_delivery' status later in sorting.
    candidates = DeliveryAgentProfile.objects.filter(
        approval_status='approved',
        is_blocked=False,
        is_active=True,
    )

    matched_pincode = []  # Tier 1: Exact Pincode
    matched_region = []   # Tier 2: Same Pincode Region (First 3 digits)
    matched_city = []     # Tier 3: Same City

    for agent in candidates:
        agent_city = (agent.city or '').strip().lower()
        service_cities = [c.strip().lower() for c in (agent.service_cities or []) if c]
        service_pincodes = [str(p).strip() for p in (agent.service_pincodes or []) if p]
        
        # 1. Check Exact Pincode Match
        pincode_match = delivery_pincode in service_pincodes or agent.postal_code == delivery_pincode
        
        # 2. Check Regional Match (First 3 digits of Pincode)
        region_match = False
        if not pincode_match and len(delivery_pincode) >= 3:
            delivery_prefix = delivery_pincode[:3]
            agent_prefixes = [p[:3] for p in service_pincodes if len(p) >= 3]
            region_match = delivery_prefix in agent_prefixes or (agent.postal_code or '')[:3] == delivery_prefix

        # 3. Check City/State Match
        city_match = (
            agent_city == delivery_city
            or delivery_city in service_cities
            or delivery_state in service_cities
        )

        if pincode_match or region_match or city_match:
            active_count = DeliveryAssignment.objects.filter(
                agent=agent,
                status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
            ).count()
            
            # Status Weight: available(0), on_delivery(1), on_break(2), offline(3)
            status_map = {'available': 0, 'on_delivery': 1, 'on_break': 2, 'offline': 3}
            status_weight = status_map.get(agent.availability_status, 4)

            # Calculate distance if coordinates available
            distance = haversine_distance(delivery_lat, delivery_lon, agent.latitude, agent.longitude)
            
            # Tiered assignment
            if pincode_match:
                matched_pincode.append((agent, status_weight, distance, active_count))
            elif region_match:
                matched_region.append((agent, status_weight, distance, active_count))
            else:
                matched_city.append((agent, status_weight, distance, active_count))

    # Selection Priority: Tier 1 > Tier 2 > Tier 3
    if matched_pincode:
        tier_candidates = matched_pincode
    elif matched_region:
        tier_candidates = matched_region
    elif matched_city:
        tier_candidates = matched_city
    else:
        # ── Tier 4: Global Fallback (Any agent if no local match) ───────────
        # This solves the "No agents available" issue when only one agent is 
        # present but city/pincode doesn't match perfectly.
        tier_candidates = []
        for agent in candidates:
             # Just use workload and status for global fallback
             active_count = DeliveryAssignment.objects.filter(
                 agent=agent,
                 status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
             ).count()
             status_map = {'available': 0, 'on_delivery': 1, 'on_break': 2, 'offline': 3}
             status_weight = status_map.get(agent.availability_status, 4)
             tier_candidates.append((agent, status_weight, 999999, active_count))

    if not tier_candidates:
        return None

    # Sort logic: 
    # 1. Availability Status (Weight)
    # 2. Proximity (Distance)
    # 3. Number of active orders (Load balance)
    tier_candidates.sort(key=lambda x: (x[1], x[2], x[3]))
    best_agent = tier_candidates[0][0]

    # ── Compute delivery fee ─────────────────────────────────────────────────
    # Simple rule: ₹50 base, +₹30 if out-of-city vs agent's primary city
    is_same_city = (best_agent.city or '').strip().lower() == delivery_city
    delivery_fee = Decimal('50.00') if is_same_city else Decimal('80.00')

    # ── Build assignment ─────────────────────────────────────────────────────
    estimated_date = timezone.now().date() + timedelta(days=2)

    # Build pickup address from order vendor(s)
    # Use first item's vendor shop address if available
    pickup_address = "Vendor Warehouse"
    try:
        first_item = order.items.select_related('vendor').first()
        if first_item and first_item.vendor:
            v = first_item.vendor
            pickup_address = f"{v.shop_name}, {v.address or ''}"
    except Exception:
        pass

    delivery_addr_text = (
        f"{delivery_address.address_line1}, "
        f"{delivery_address.city}, "
        f"{delivery_address.state} - {delivery_address.pincode}"
    )

    assignment = DeliveryAssignment.objects.create(
        agent=best_agent,
        order=order,
        status='assigned',
        pickup_address=pickup_address,
        delivery_address=delivery_addr_text,
        delivery_city=delivery_address.city,
        estimated_delivery_date=estimated_date,
        delivery_fee=delivery_fee,
        customer_contact=delivery_address.phone or '',
    )

    # First tracking record
    DeliveryTracking.objects.create(
        delivery_assignment=assignment,
        latitude=0,
        longitude=0,
        address=f"Assigned – {delivery_address.city}",
        status='Order Assigned to Agent',
        notes=f"Auto-assigned to {best_agent.user.username} for delivery to {delivery_address.city}",
    )

    # Update order status based on current state:
    # - If 'shipping' (vendor has shipped), move to 'out_for_delivery' since an agent is now assigned
    # - If 'pending', advance to 'confirmed'
    # - If already 'confirmed', leave it as-is (agent assigned but not yet shipping)
    if order.status == 'shipping':
        order.status = 'out_for_delivery'
        order.save(update_fields=['status'])
    elif order.status == 'pending':
        order.status = 'confirmed'
        order.save(update_fields=['status'])
    # 'confirmed' status: leave unchanged — vendor still needs to ship

    return assignment


def auto_assign_return(order, return_requests=None):
    """
    Try to auto-assign a return request to the best available delivery agent.
    Returns: DeliveryAssignment or None
    """
    # 1. Eligibility & Deduplication
    if not order or not order.delivery_address:
        return None
        
    if DeliveryAssignment.objects.filter(order=order, assignment_type='return', status__in=['assigned', 'accepted', 'picked_up']).exists():
        return None

    # 2. Get Candidates (Same logic as standard delivery)
    candidates = DeliveryAgentProfile.objects.filter(
        approval_status='approved',
        is_blocked=False,
        is_active=True,
    )
    
    delivery_address = order.delivery_address
    delivery_city = (delivery_address.city or '').strip().lower()
    delivery_pincode = (delivery_address.pincode or '').strip()
    
    tier_candidates = []
    for agent in candidates:
        agent_city = (agent.city or '').strip().lower()
        service_cities = [c.strip().lower() for c in (agent.service_cities or []) if c]
        service_pincodes = [str(p).strip() for p in (agent.service_pincodes or []) if p]

        pincode_match = delivery_pincode in service_pincodes or agent.postal_code == delivery_pincode
        city_match = (agent_city == delivery_city or delivery_city in service_cities)

        if pincode_match or city_match:
            active_count = DeliveryAssignment.objects.filter(
                agent=agent,
                status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
            ).count()
            
            # Distance if coordinates available
            distance = haversine_distance(delivery_address.latitude, delivery_address.longitude, agent.latitude, agent.longitude)
            
            # Status weight (available=0, on_delivery=1, etc)
            status_map = {'available': 0, 'on_delivery': 1, 'on_break': 2, 'offline': 3}
            status_weight = status_map.get(agent.availability_status, 4)
            
            tier_candidates.append((agent, status_weight, distance, active_count))

    if not tier_candidates:
        # Global fallback
        for agent in candidates:
             active_count = DeliveryAssignment.objects.filter(agent=agent, status__in=['assigned', 'accepted', 'picked_up']).count()
             tier_candidates.append((agent, 0, 999999, active_count))

    if not tier_candidates:
        return None

    tier_candidates.sort(key=lambda x: (x[1], x[2], x[3]))
    best_agent = tier_candidates[0][0]

    # 3. Create Assignment
    # For a return, the 'pickup_address' is the CUSTOMER address
    # and 'delivery_address' is the VENDOR warehouse.
    
    cust_addr = f"{delivery_address.address_line1}, {delivery_address.city}, {delivery_address.pincode}"
    
    vendor_addr = "Admin/Vendor Warehouse"
    try:
        first_item = order.items.first()
        if first_item and first_item.vendor:
            v = first_item.vendor
            vendor_addr = f"{v.shop_name}, {v.address or ''}"
    except: pass

    # Link to the first return request if provided
    first_ret = None
    if return_requests and len(return_requests) > 0:
        from user.models import OrderReturn
        first_ret = OrderReturn.objects.filter(id=return_requests[0]).first()

    assignment = DeliveryAssignment.objects.create(
        agent=best_agent,
        order=order,
        assignment_type='return',
        return_request=first_ret,
        status='assigned',
        pickup_address=cust_addr, # Pick up from customer
        delivery_address=vendor_addr, # Deliver back to vendor
        delivery_city=delivery_address.city,
        estimated_delivery_date=timezone.now().date() + timedelta(days=2),
        delivery_fee=Decimal('40.00'), # Lower fee for returns usually
        customer_contact=delivery_address.phone or '',
    )

    # Tracking
    DeliveryTracking.objects.create(
        delivery_assignment=assignment,
        status='Return Pickup Assigned',
        notes=f"Auto-assigned return pickup to {best_agent.user.username}"
    )

    return assignment


def get_unassigned_confirmed_orders():
    """
    Return queryset of confirmed/paid orders that have no DeliveryAssignment yet.
    Useful for admin dashboard to see orders needing manual assignment.
    """
    from user.models import Order
    from django.db.models import Q

    assigned_order_ids = DeliveryAssignment.objects.values_list('order_id', flat=True)
    return Order.objects.filter(
        Q(payment_status='completed') | Q(payment_method='cod'),
        status='shipping'
    ).exclude(
        id__in=assigned_order_ids
    ).select_related('delivery_address').order_by('-created_at')
