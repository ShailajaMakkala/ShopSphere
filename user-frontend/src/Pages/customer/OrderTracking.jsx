import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
    CheckCircle,
    Package,
    Warehouse,
    Ship,
    Truck,
    Box,
    ArrowLeft,
    Calendar,
    Clock
} from "lucide-react";
import { useSelector, useDispatch } from "react-redux";

import { fetchOrders } from "../../Store";

const OrderTracking = () => {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [order, setOrder] = useState(null);
    const { orders, isLoading } = useSelector((state) => state.order);
    const dispatch = useDispatch();

    useEffect(() => {
        if (orders.length === 0 && !isLoading) {
            dispatch(fetchOrders());
        }
    }, [dispatch, orders.length, isLoading]);

    // Find order from state
    useEffect(() => {
        const foundOrder = orders.find(o => String(o.id) === orderId || o.transaction_id === orderId || String(o.order_number) === orderId);
        if (foundOrder) {
            setOrder(foundOrder);
        }
    }, [orderId, orders]);



    const steps = [
        { id: "pending", label: "Order Placed", icon: <CheckCircle size={20} /> },
        { id: "confirmed", label: "Confirmed by Vendor", icon: <Warehouse size={20} /> },
        { id: "shipping", label: "In Transit", icon: <Ship size={20} /> },
        { id: "out_for_delivery", label: "Out for Delivery", icon: <Truck size={20} /> },
        { id: "delivered", label: "Delivered", icon: <Box size={20} /> },
    ];

    const getStatusIndex = (status) => {
        // Special mapping for delivery agent states
        if (status === 'out_for_delivery') return 3;
        const index = steps.findIndex(step => step.id === status);
        return index === -1 ? 0 : index;
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 border-4 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-orange-400 font-bold animate-pulse">Syncing tracking data...</p>
                </div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4 font-sans text-center">
                <div className="max-w-md">
                    <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Box className="text-gray-300" size={32} />
                    </div>
                    <h2 className="text-2xl font-black text-gray-900 mb-2">Order Not Found</h2>
                    <p className="text-gray-500 mb-8">We couldn't find an order with the ID <span className="text-orange-400 font-bold">#{orderId}</span>. Please verify the ID or check your order history.</p>
                    <button
                        onClick={() => navigate("/profile/orders")}
                        className="px-8 py-4 bg-gray-900 text-white text-[11px] font-black uppercase tracking-widest rounded-2xl hover:bg-gray-800 transition-all shadow-xl shadow-gray-200"
                    >
                        Go to My Orders
                    </button>
                </div>
            </div>
        );
    }


    // Harmonize status field name (backend sends 'status', frontend was looking for 'order_status')
    const currentStatus = order.status || order.order_status || "pending";
    const currentStepIndex = getStatusIndex(currentStatus);
    const progressPercent = (currentStepIndex / (steps.length - 1)) * 100;

    return (
        <div className="min-h-screen bg-[#fafafa] pt-8 pb-16 px-4 sm:px-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-5 mb-10">
                    <button
                        onClick={() => navigate(-1)}
                        className="w-11 h-11 flex items-center justify-center bg-white rounded-2xl shadow-sm border border-gray-100 text-gray-400 hover:text-gray-900 hover:shadow-md transition-all active:scale-95 shrink-0"
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <div className="flex-1">
                        <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight uppercase leading-none">
                            TRACK ORDER
                        </h1>
                        <p className="text-[10px] sm:text-[11px] font-black text-gray-400 uppercase tracking-widest mt-1.5 opacity-80">
                            Estimated delivery: <span className="text-orange-500">{order.estimated_delivery || "2-4 Business Days"}</span>
                        </p>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

                    {/* LEFT COLUMN: Tracking Visuals */}
                    <div className="lg:col-span-8 space-y-8">

                        {/* Summary Header Card */}
                        <div className="bg-white rounded-[32px] p-6 sm:p-8 border border-gray-100 shadow-sm overflow-hidden relative group">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-orange-50/30 rounded-full -mr-16 -mt-16 blur-3xl transition-all group-hover:bg-orange-100/40" />

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 relative z-10">
                                <div className="space-y-1">
                                    <p className="text-[9px] font-black text-gray-400 uppercase tracking-[2px]">Placed On</p>
                                    <p className="text-sm font-black text-gray-900">
                                        {new Date(order.created_at).toLocaleDateString("en-IN", {
                                            day: "2-digit", month: "short"
                                        })}
                                    </p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[9px] font-black text-gray-400 uppercase tracking-[2px]">Amount</p>
                                    <p className="text-sm font-black text-gray-900">₹{Number(order.total_amount).toFixed(2)}</p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[9px] font-black text-gray-400 uppercase tracking-[2px]">Ship To</p>
                                    <p className="text-sm font-black text-gray-900 truncate pr-2">{order.customer_name || "Valued User"}</p>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[9px] font-black text-gray-400 uppercase tracking-[2px]">Order ID</p>
                                    <p className="text-sm font-black text-orange-400 tracking-tighter">#{order.id}</p>
                                </div>
                            </div>
                        </div>

                        {/* Progress Timeline Page */}
                        <div className="bg-white rounded-[32px] p-8 sm:p-12 border border-gray-100 shadow-sm">

                            {/* Desktop Horizontal (md+) */}
                            <div className="hidden md:block relative mt-16 mb-24 px-4">
                                {/* Base Line */}
                                <div className="absolute top-1/2 left-0 w-full h-[6px] bg-gray-100 -translate-y-1/2 rounded-full" />

                                {/* Active Line */}
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progressPercent}%` }}
                                    transition={{ duration: 1.2, ease: "easeInOut" }}
                                    className="absolute top-1/2 left-0 h-[6px] bg-gradient-to-r from-orange-400 to-purple-500 -translate-y-1/2 z-10 rounded-full"
                                />

                                {/* Moving Truck */}
                                <motion.div
                                    initial={{ left: 0 }}
                                    animate={{ left: `${progressPercent}%` }}
                                    transition={{ duration: 1.8, ease: "backOut", delay: 0.3 }}
                                    className="absolute top-1/2 -translate-y-12 -translate-x-1/2 z-20"
                                >
                                    <div className="bg-white p-3 rounded-2xl shadow-xl border border-orange-100 ring-4 ring-orange-50/50">
                                        <Truck size={24} className="text-orange-500 animate-pulse" />
                                        <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rotate-45 border-r border-b border-orange-50"></div>
                                    </div>
                                </motion.div>

                                {/* Steps Circles */}
                                <div className="flex justify-between relative z-10 pt-1">
                                    {steps.map((step, index) => {
                                        const isCompleted = index < currentStepIndex;
                                        const isCurrent = index === currentStepIndex;
                                        return (
                                            <div key={step.id} className="relative flex flex-col items-center">
                                                <div className={`w-11 h-11 rounded-full flex items-center justify-center border-4 transition-all duration-500 ${isCompleted ? "bg-orange-500 border-white text-white shadow-lg" :
                                                    isCurrent ? "bg-white border-orange-400 text-orange-500 scale-125 z-20" :
                                                        "bg-white border-gray-100 text-gray-200"
                                                    }`}>
                                                    {isCompleted ? <CheckCircle size={18} strokeWidth={3} /> : React.cloneElement(step.icon, { size: 18 })}
                                                </div>
                                                <div className="absolute -bottom-20 w-32 text-center">
                                                    <p className={`text-[10px] font-black uppercase tracking-widest mt-4 ${isCurrent ? "text-orange-500" : isCompleted ? "text-gray-900" : "text-gray-300"
                                                        }`}>
                                                        {step.label}
                                                    </p>
                                                    {isCurrent && (
                                                        <span className="text-[8px] font-black bg-orange-50 text-orange-400 px-2.5 py-1 rounded-full uppercase tracking-tight mt-1 inline-block">
                                                            Currently Here
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Mobile Vertical (default) */}
                            <div className="md:hidden space-y-10 pl-2">
                                {steps.map((step, index) => {
                                    const isCompleted = index < currentStepIndex;
                                    const isCurrent = index === currentStepIndex;
                                    const isLast = index === steps.length - 1;

                                    return (
                                        <div key={step.id} className="flex gap-6 relative">
                                            {/* Vertical Line */}
                                            {!isLast && (
                                                <div className={`absolute left-[21px] top-12 bottom-[-40px] w-1 rounded-full transition-colors duration-500 ${isCompleted ? "bg-orange-500" : "bg-gray-100"
                                                    }`} />
                                            )}

                                            {/* Icon Circle */}
                                            <div className={`w-11 h-11 rounded-2xl flex items-center justify-center border-2 shrink-0 z-10 transition-all duration-500 ${isCompleted ? "bg-orange-500 border-orange-500 text-white shadow-lg shadow-orange-200" :
                                                isCurrent ? "bg-white border-orange-400 text-orange-500 scale-110 shadow-xl" :
                                                    "bg-white border-gray-100 text-gray-300"
                                                }`}>
                                                {isCompleted ? <CheckCircle size={20} strokeWidth={3} /> : React.cloneElement(step.icon, { size: 20 })}
                                            </div>

                                            {/* Label Content */}
                                            <div className="pt-1.5 flex flex-col justify-center">
                                                <p className={`text-xs font-black uppercase tracking-widest leading-none ${isCurrent ? "text-orange-500" : isCompleted ? "text-gray-900" : "text-gray-300"
                                                    }`}>
                                                    {step.label}
                                                </p>
                                                {isCurrent && (
                                                    <div className="flex items-center gap-2 mt-2">
                                                        <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.5 }} className="w-1.5 h-1.5 rounded-full bg-orange-400" />
                                                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">Active Now</span>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Mobile Active Asset */}
                                            {isCurrent && (
                                                <div className="absolute right-0 top-0 opacity-20">
                                                    <Truck size={48} className="text-orange-400 rotate-[-15deg]" />
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Additional Info Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-4">
                            <div className="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-12 h-12 bg-orange-50 text-orange-500 rounded-2xl flex items-center justify-center shadow-inner">
                                        <Package size={22} />
                                    </div>
                                    <h3 className="text-xs font-black text-gray-900 uppercase tracking-[2px]">Shipment Status</h3>
                                </div>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center text-[13px]">
                                        <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Courier</span>
                                        <span className="text-gray-900 font-black">ShopSphere Global Logistics</span>
                                    </div>
                                    <div className="flex justify-between items-center text-[13px]">
                                        <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Vessel</span>
                                        <span className="text-gray-900 font-black">SS-EX-3401</span>
                                    </div>
                                    <div className="flex justify-between items-center text-[13px]">
                                        <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Total Weight</span>
                                        <span className="text-gray-900 font-black">2.48 KG</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-2xl flex items-center justify-center shadow-inner">
                                        <Clock size={22} />
                                    </div>
                                    <h3 className="text-xs font-black text-gray-900 uppercase tracking-[2px]">Latest Refresh</h3>
                                </div>
                                <div className="flex gap-4">
                                    <div className="w-1 bg-gradient-to-b from-purple-500 to-purple-200 rounded-full" />
                                    <div>
                                        <p className="text-[13px] font-black text-gray-900 mb-1">Process Completed at Hub</p>
                                        <p className="text-[11px] text-gray-400 font-bold leading-relaxed pr-4">Sorting and final quality checks for your items have been completed at our primary distribution center.</p>
                                        <div className="mt-3 py-1.5 px-3 bg-purple-50 rounded-lg inline-flex items-center gap-2">
                                            <div className="w-1 h-1 rounded-full bg-purple-600 animate-ping" />
                                            <span className="text-[9px] font-black text-purple-600 uppercase tracking-widest">34 Minutes Ago</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Secondary Actions & Support (lg+) */}
                    <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-28">
                        {/* Help Card */}
                        <div className="bg-gray-900 rounded-[32px] p-8 text-white relative overflow-hidden shadow-2xl">
                            <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -mr-20 -mt-20 blur-3xl" />
                            <h3 className="text-xl font-black mb-4 relative z-10">Need help?</h3>
                            <p className="text-gray-400 text-sm font-bold leading-relaxed mb-8 relative z-10">
                                If you have any questions regarding your delivery or if tracking hasn't updated in 24 hours, our support team is here to assist.
                            </p>
                            <button onClick={() => window.Tawk_API?.maximize()} className="w-full py-4 bg-white text-gray-900 rounded-2xl font-black text-[11px] uppercase tracking-widest hover:bg-orange-400 hover:text-white transition-all transform active:scale-95 shadow-xl relative z-10">
                                Live Chat Support
                            </button>
                        </div>

                        {/* Footer Buttons */}
                        <div className="space-y-3">
                            <button
                                onClick={() => navigate("/profile/orders")}
                                className="w-full py-5 bg-white border border-gray-100 rounded-3xl text-gray-900 font-black text-[11px] uppercase tracking-[2px] hover:bg-gray-50 transition-all flex items-center justify-center gap-3 shadow-sm active:scale-98"
                            >
                                <ArrowLeft size={14} /> Back to My Orders
                            </button>
                            <button
                                onClick={() => window.print()}
                                className="w-full py-5 bg-white border border-gray-100 rounded-3xl text-gray-400 font-black text-[11px] uppercase tracking-[2px] hover:text-gray-900 hover:bg-gray-50 transition-all flex items-center justify-center gap-3 shadow-sm active:scale-98"
                            >
                                Print Receipt
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrderTracking;

