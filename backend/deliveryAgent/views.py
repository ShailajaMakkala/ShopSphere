from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AgentRegistrationForm
from .models import DeliveryAgentProfile, DeliveryAssignment
from django.db.models import Sum
from django.utils import timezone

# ===== Agent Portal View =====
def agent_portal(request):
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('delivery_dashboard')

    login_form = AuthenticationForm()
    signup_form = AgentRegistrationForm()
    active_tab = 'signin'

    style = (
        'w-full p-5 bg-gray-50 border-2 border-gray-100 rounded-[2rem] '
        'font-bold tracking-wide focus:border-[#5D56D1] outline-none transition-all'
    )
    for field in login_form.fields.values():
        field.widget.attrs.update({'class': style})

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'signup':
            active_tab = 'signup'
            signup_form = AgentRegistrationForm(request.POST, request.FILES)

            if signup_form.is_valid():
                user = signup_form.save()
                # Do NOT log in the user immediately. They must wait for approval.
                messages.success(request, "Registration submitted! Please wait for administrator approval before logging in. 🚚")
                return redirect('agentPortal')
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'login':
            active_tab = 'signin'
            login_form = AuthenticationForm(request, data=request.POST)
            for field in login_form.fields.values():
                field.widget.attrs.update({'class': style})

            if login_form.is_valid():
                user = login_form.get_user()
                
                # Check for approval before logging in
                if user.role == 'delivery':
                    try:
                        profile = user.delivery_agent_profile
                        if profile.approval_status != 'approved':
                            messages.error(request, "Your delivery partner account is pending admin approval.")
                            return redirect('agentPortal')
                    except Exception:
                        messages.error(request, "Delivery profile not found.")
                        return redirect('agentPortal')

                login(request, user)
                return redirect('delivery_dashboard')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'agent_portal.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'active_tab': active_tab,
    })


# ===== Delivery Dashboard View =====
@login_required
def delivery_dashboard(request):
    if request.user.role != 'delivery':
        messages.error(request, "Access restricted to delivery agents only.")
        return redirect('agentPortal')

    try:
        agent = DeliveryAgentProfile.objects.get(user=request.user)
    except DeliveryAgentProfile.DoesNotExist:
        messages.error(request, "Delivery profile not found.")
        return redirect('agentPortal')

    # Final approval check
    if agent.approval_status != 'approved':
        messages.warning(request, "Your delivery account is still pending admin approval. Access is restricted for now.")
        logout(request)
        return redirect('agentPortal')
    
    # Separate assignments into available (assigned) and active (in progress)
    available_orders = DeliveryAssignment.objects.filter(
        agent=agent,
        status='assigned'
    ).order_by('-assigned_at')
    
    active_deliveries = DeliveryAssignment.objects.filter(
        agent=agent,
        status__in=['accepted', 'picked_up', 'in_transit', 'arrived']
    ).order_by('-assigned_at')

    # Recent delivered orders
    recent_deliveries = DeliveryAssignment.objects.filter(
        agent=agent,
        status='delivered'
    ).order_by('-completed_at')[:10]

    # Dashboard stats
    total_earnings = agent.total_earnings
    completed_orders_count = agent.completed_deliveries
    available_orders_count = available_orders.count()

    return render(request, 'delivery_dashboard.html', {
        'user': request.user,
        'agent': agent,
        'available_orders': available_orders,
        'active_deliveries': active_deliveries,
        'recent_orders': recent_deliveries,
        'total_earnings': total_earnings,
        'completed_orders_count': completed_orders_count,
        'available_orders_count': available_orders_count,
    })


@login_required
def accept_order_sim(request, order_id):
    return accept_order(request, order_id)


@login_required
def accept_order(request, order_id):
    if request.method == 'POST':
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = get_object_or_404(DeliveryAssignment, order__id=order_id, agent=agent)

            if assignment.status == 'assigned':
                assignment.accept_delivery()
                messages.success(request, f"Order #{assignment.order.order_number} accepted! Proceed to pickup.")
            else:
                messages.warning(request, f"Order is already {assignment.status}.")
                
        except Exception as e:
             messages.error(request, f"Error: {str(e)}")
    return redirect('delivery_dashboard')

@login_required
def pickup_order(request, order_id):
    if request.method == 'POST':
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = get_object_or_404(DeliveryAssignment, order__id=order_id, agent=agent)
            if assignment.status == 'accepted':
                assignment.start_delivery() # Sets to picked_up
                messages.success(request, f"Order #{assignment.order.order_number} marked as Picked Up.")
            else:
                messages.error(request, "Order must be accepted before pickup.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect('delivery_dashboard')

@login_required
def start_transit(request, order_id):
    if request.method == 'POST':
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = get_object_or_404(DeliveryAssignment, order__id=order_id, agent=agent)
            if assignment.status == 'picked_up':
                assignment.mark_in_transit()
                messages.success(request, f"Order #{assignment.order.order_number} is now In Transit.")
            else:
                messages.error(request, "Order must be picked up before starting transit.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect('delivery_dashboard')

@login_required
def mark_arrived(request, order_id):
    if request.method == 'POST':
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = get_object_or_404(DeliveryAssignment, order__id=order_id, agent=agent)
            if assignment.status == 'in_transit':
                assignment.mark_arrived() # This triggers OTP generation/sending
                messages.success(request, f"Arrived at location. OTP has been sent to the customer.")
            else:
                messages.error(request, "Order must be in transit to mark as arrived.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect('delivery_dashboard')

@login_required
def complete_delivery_otp(request, order_id):
    if request.method == 'POST':
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = get_object_or_404(DeliveryAssignment, order__id=order_id, agent=agent)
            entered_otp = request.POST.get('otp_code', '').strip()
            
            if assignment.status != 'arrived':
                messages.error(request, "Delivery must be marked as arrived before verification.")
            elif entered_otp == assignment.otp_code:
                assignment.mark_delivered()
                messages.success(request, f"Order #{assignment.order.order_number} delivered successfully! 🚚")
            else:
                messages.error(request, "Invalid OTP code. Please check with the customer.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect('delivery_dashboard')