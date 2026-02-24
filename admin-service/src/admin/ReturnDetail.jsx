import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    RefreshCcw,
    AlertCircle,
    CheckCircle2,
    Truck,
    CreditCard,
    ArrowLeft,
    Clock,
    XCircle,
    Tag,
    User,
    Package,
    ShieldCheck,
    PanelLeftClose,
    PanelLeftOpen
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchReturnDetail, approveReturn, rejectReturn, processRefund, logout } from '../api/axios';
import Sidebar from '../components/Sidebar';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';

const STATUS_CONFIG = {
    requested: { label: 'Requested', color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-100', icon: Clock, gradient: 'from-orange-400 to-orange-600 shadow-orange-500/30' },
    approved: { label: 'Approved', color: 'text-purple-700', bg: 'bg-purple-50', border: 'border-purple-100', icon: CheckCircle2, gradient: 'from-purple-500 to-purple-700 shadow-purple-500/30' },
    pickup_assigned: { label: 'Assigned', color: 'text-indigo-700', bg: 'bg-indigo-50', border: 'border-indigo-100', icon: Truck, gradient: 'from-indigo-500 to-indigo-700 shadow-indigo-500/30' },
    picked_up: { label: 'In Transit', color: 'text-fuchsia-700', bg: 'bg-fuchsia-50', border: 'border-fuchsia-100', icon: Truck, gradient: 'from-fuchsia-500 to-fuchsia-700 shadow-fuchsia-500/30' },
    received: { label: 'Verified', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-100', icon: RefreshCcw, gradient: 'from-emerald-500 to-emerald-700 shadow-emerald-500/30' },
    completed: { label: 'Refunded', color: 'text-slate-700', bg: 'bg-slate-100', border: 'border-slate-200', icon: CheckCircle2, gradient: 'from-slate-600 to-slate-800 shadow-slate-500/30' },
    rejected: { label: 'Rejected', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-100', icon: XCircle, gradient: 'from-rose-500 to-rose-700 shadow-rose-500/30' }
};

const ReturnDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isDarkMode } = useTheme();
    const [returnReq, setReturnReq] = useState(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    useEffect(() => {
        loadDetail();
    }, [id]);

    const loadDetail = async () => {
        try {
            setLoading(true);
            const data = await fetchReturnDetail(id);
            setReturnReq(data);
        } catch (error) {
            toast.error('Failed to load return details');
            navigate('/returns');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        if (!confirm('Approve this return request?')) return;
        try {
            setActionLoading(true);
            await approveReturn(id);
            toast.success('Return request approved');
            await loadDetail();
        } catch (error) {
            toast.error('Failed to approve');
        } finally {
            setActionLoading(false);
        }
    };

    const handleReject = async () => {
        const reason = prompt('Enter reason for rejection:');
        if (!reason) return;
        try {
            setActionLoading(true);
            await rejectReturn(id, reason);
            toast.success('Return request rejected');
            await loadDetail();
        } catch (error) {
            toast.error('Failed to reject');
        } finally {
            setActionLoading(false);
        }
    };

    const handleProcessRefund = async () => {
        if (!confirm('Mark refund as processed?')) return;
        try {
            setActionLoading(true);
            await processRefund(id);
            toast.success('Refund processed successfully');
            await loadDetail();
        } catch (error) {
            toast.error('Failed to process refund');
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className={`flex h-screen items-center justify-center transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a]' : 'bg-[#F8FAFC]'}`}>
                <div className="flex flex-col items-center gap-6">
                    <div className="relative">
                        <div className="w-16 h-16 rounded-full border-4 border-orange-500/20 border-t-orange-500 animate-spin shadow-2xl" />
                        <RefreshCcw className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-orange-500" />
                    </div>
                    <p className={`text-[10px] font-black uppercase tracking-[0.3em] ${isDarkMode ? 'text-slate-500' : 'text-orange-600 animate-pulse'}`}>Decrypting Return Vector</p>
                </div>
            </div>
        );
    }

    if (!returnReq) return null;
    const config = STATUS_CONFIG[returnReq.status] || STATUS_CONFIG.requested;

    return (
        <div className={`flex h-screen font-sans overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a] text-slate-100' : 'bg-[#F8FAFC] text-slate-900'}`}>
            <Sidebar isSidebarOpen={isSidebarOpen} activePage="Returns" onLogout={logout} />

            <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 overflow-hidden ${!isDarkMode && 'bg-gradient-to-br from-[#fff5f5] via-[#fef3f2] to-[#f3e8ff]'}`}>
                {/* Header */}
                <header className={`border-b px-8 h-20 flex items-center justify-between sticky top-0 z-20 transition-all duration-300 ${isDarkMode ? 'bg-[#0f172a]/80 border-slate-800 backdrop-blur-md' : 'bg-white/80 border-slate-100 backdrop-blur-md shadow-sm'}`}>
                    <div className="flex items-center gap-4">
                        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className={`p-2 rounded-xl border transition-all ${isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white' : 'bg-white border-slate-200 text-slate-400 hover:text-orange-600 shadow-sm'}`}>
                            {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
                        </button>
                        <div className={`w-px h-6 hidden sm:block mx-2 ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`} />
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/returns')}
                                className={`w-10 h-10 flex items-center justify-center border rounded-xl transition-all shadow-sm active:scale-95 ${isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white' : 'bg-white border-slate-200 text-slate-400 hover:text-orange-600'}`}
                            >
                                <ArrowLeft size={18} />
                            </button>
                            <div>
                                <h1 className={`text-lg font-black tracking-tight ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>Return Dossier</h1>
                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] leading-none">Security Clearance: Verified</p>
                            </div>
                        </div>
                    </div>

                    <div className={`px-4 py-1.5 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center gap-2 border bg-white shadow-xl shadow-orange-500/5 ${config.bg} ${config.color} ${config.border}`}>
                        <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-tr ${config.gradient}`}></div>
                        {returnReq.status_display}
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-4 md:p-8">
                    <div className="max-w-5xl mx-auto space-y-8 pb-32">
                        {/* Profile Section */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`rounded-[3rem] p-8 md:p-12 relative overflow-hidden border transition-all duration-500 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white/90 backdrop-blur-xl border-white shadow-2xl shadow-orange-950/5'}`}
                        >
                            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-orange-400/5 to-purple-500/5 rounded-full translate-x-1/2 -translate-y-1/2 blur-3xl opacity-50" />

                            <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center md:items-start">
                                <div className={`w-32 h-32 rounded-[2.5rem] flex items-center justify-center text-4xl font-black transition-all bg-gradient-to-tr ${config.gradient} text-white shadow-2xl rotate-3`}>
                                    {returnReq.order_number?.charAt(0) || 'R'}
                                </div>

                                <div className="flex-1 text-center md:text-left">
                                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mb-6">
                                        <span className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-[0.2em] border ${config.bg} ${config.color} ${config.border} bg-white shadow-sm`}>
                                            Ref: {returnReq.order_number}
                                        </span>
                                        <span className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-[0.2em] border ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-500' : 'bg-white text-slate-400 border-slate-100 shadow-sm'}`}>
                                            Protocol ID: #{id}
                                        </span>
                                    </div>
                                    <h2 className={`text-4xl font-black tracking-tight mb-3 uppercase ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{returnReq.product_name}</h2>
                                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-8">
                                        <div className="flex items-center gap-2 text-slate-500 text-xs font-black uppercase tracking-widest">
                                            <User size={14} className="text-orange-500" /> {returnReq.user?.name || 'Authorized Buyer'}
                                        </div>
                                        <div className="flex items-center gap-2 text-slate-500 text-xs font-black uppercase tracking-widest">
                                            <Package size={14} className="text-purple-500" /> Unit Count: 01
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {/* Execution Matrix */}
                            <section className={`rounded-[2.5rem] p-8 border transition-all duration-300 flex flex-col items-center justify-center gap-6 relative group ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white/60 border-white shadow-xl shadow-orange-500/5'}`}>
                                <div className="absolute top-4 right-4 text-orange-400/20 group-hover:scale-110 transition-transform">
                                    <CreditCard size={48} />
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-2">Settlement Total</p>
                                    <p className={`text-4xl font-black ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>₹{parseFloat(returnReq.return_amount).toLocaleString()}</p>
                                </div>
                                <div className={`px-6 py-2 rounded-2xl bg-gradient-to-tr ${config.gradient} text-white font-black text-[9px] uppercase tracking-[0.3em] shadow-xl`}>
                                    Refund Protocol
                                </div>
                            </section>

                            <section className={`rounded-[2.5rem] p-8 border transition-all duration-300 flex flex-col items-center justify-center gap-6 relative group ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white/60 border-white shadow-xl shadow-purple-500/5'}`}>
                                <div className="absolute top-4 right-4 text-purple-400/20 group-hover:scale-110 transition-transform">
                                    <Truck size={48} />
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-2">Assigned Agent</p>
                                    <p className={`text-xl font-black uppercase tracking-tight ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{returnReq.pickup_agent_name || 'Protocol Offline'}</p>
                                </div>
                                <div className="px-6 py-2 rounded-2xl bg-purple-100 text-purple-700 border border-purple-200 font-black text-[9px] uppercase tracking-[0.3em] shadow-sm">
                                    Logistic Auth
                                </div>
                            </section>

                            <section className={`rounded-[2.5rem] p-8 border transition-all duration-300 md:col-span-2 lg:col-span-1 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white/60 border-white shadow-xl shadow-emerald-500/5'}`}>
                                <h3 className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                                    <Tag className="w-3 h-3 text-orange-500" /> Audit Context
                                </h3>
                                <div className="space-y-4">
                                    <div className={`p-4 rounded-2xl border ${isDarkMode ? 'bg-slate-900 border-slate-800' : 'bg-slate-50/50 border-slate-100 shadow-inner'}`}>
                                        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Reason Code</p>
                                        <p className="text-xs font-black uppercase tracking-tight text-slate-700">{returnReq.reason_display}</p>
                                    </div>
                                    <div className={`p-4 rounded-2xl border ${isDarkMode ? 'bg-slate-900 border-slate-800' : 'bg-slate-50/50 border-slate-100 shadow-inner'}`}>
                                        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Refund Vector</p>
                                        <p className="text-xs font-black uppercase tracking-tight text-orange-600 font-black">{returnReq.refund_status}</p>
                                    </div>
                                </div>
                            </section>

                            <section className={`md:col-span-2 rounded-[2.5rem] p-10 border transition-all duration-300 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-gradient-to-r from-orange-50 to-purple-50 border-white shadow-xl shadow-orange-500/5'}`}>
                                <h3 className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                                    <AlertCircle className="w-3 h-3 text-purple-500" /> Qualitative Narrative
                                </h3>
                                <p className={`text-base font-bold italic leading-relaxed ${isDarkMode ? 'text-slate-300' : 'text-slate-600 opacity-80'}`}>
                                    "{returnReq.description || 'No additional narrative provided in the reversal claim.'}"
                                </p>
                            </section>

                            {/* Inspection Artifacts */}
                            {returnReq.condition_notes && (
                                <section className={`md:col-span-3 rounded-[3rem] p-10 md:p-14 border transition-all duration-300 relative overflow-hidden bg-gradient-to-br from-orange-500 to-purple-600 text-white shadow-2xl shadow-orange-500/20`}>
                                    <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full translate-x-1/2 -translate-y-1/2 blur-3xl" />

                                    <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12">
                                        <div className="space-y-8">
                                            <div>
                                                <h3 className="text-xs font-black uppercase tracking-[0.4em] text-orange-200 mb-6 flex items-center gap-3">
                                                    <ShieldCheck className="w-5 h-5" /> In-Field Inspection Report
                                                </h3>
                                                <div className="bg-white/10 backdrop-blur-md p-8 rounded-[2.5rem] border border-white/20 shadow-inner">
                                                    <p className="text-xl font-bold leading-relaxed">{returnReq.condition_notes}</p>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-4 p-6 bg-black/10 rounded-3xl border border-white/10">
                                                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
                                                    <Clock size={20} />
                                                </div>
                                                <div>
                                                    <p className="text-[9px] font-black uppercase tracking-widest text-orange-200">Verification Timestamp</p>
                                                    <p className="text-sm font-bold uppercase tracking-tight">System Commited: {new Date().toLocaleDateString()}</p>
                                                </div>
                                            </div>
                                        </div>

                                        {returnReq.verification_images && (
                                            <div className="group relative">
                                                <div className="absolute -inset-4 bg-white/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                                                <div className="rounded-[3rem] overflow-hidden bg-black/5 border border-white/20 shadow-2xl relative">
                                                    <img
                                                        src={returnReq.verification_images}
                                                        alt="Proof"
                                                        className="w-full h-auto max-h-[600px] object-contain hover:scale-105 transition-transform duration-1000"
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </section>
                            )}
                        </div>
                    </div>
                </main>

                {/* Sticky Action Bar */}
                <div className={`fixed bottom-0 right-0 left-0 border-t backdrop-blur-xl transition-all duration-300 py-6 px-10 z-[100] ${isDarkMode ? 'bg-[#0f172a]/90 border-slate-800 shadow-2xl shadow-black/50' : 'bg-white/90 border-slate-100 shadow-2xl shadow-orange-500/10'}`} style={{ marginLeft: isSidebarOpen ? '16rem' : '0' }}>
                    <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-3">
                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center bg-gradient-to-tr ${config.gradient} text-white shadow-xl`}>
                                <config.icon size={22} />
                            </div>
                            <div>
                                <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] leading-none mb-1">Awaiting Final Decision: {returnReq.order_number}</p>
                                <h4 className={`text-base font-black uppercase tracking-tight ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{returnReq.status_display} Status Case</h4>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 w-full md:w-auto">
                            {returnReq.status === 'requested' && (
                                <>
                                    <button
                                        onClick={handleReject}
                                        disabled={actionLoading}
                                        className={`flex-1 md:flex-none px-10 py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all border ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 hover:border-rose-500/20' : 'bg-white border-slate-200 text-slate-400 hover:text-rose-600 hover:bg-rose-50 hover:border-rose-100'}`}
                                    >
                                        Reject Protocol
                                    </button>
                                    <button
                                        onClick={handleApprove}
                                        disabled={actionLoading}
                                        className="flex-1 md:flex-none px-12 py-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-orange-500/20 hover:shadow-orange-500/40 hover:translate-y-[-2px] active:translate-y-[1px] transition-all"
                                    >
                                        Authorize Reversal
                                    </button>
                                </>
                            )}
                            {returnReq.status === 'received' && returnReq.refund_status !== 'processed' && (
                                <button
                                    onClick={handleProcessRefund}
                                    disabled={actionLoading}
                                    className="w-full md:flex-none px-16 py-4 bg-gradient-to-r from-purple-600 to-indigo-700 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-purple-500/20 hover:shadow-purple-500/40 hover:translate-y-[-2px] active:translate-y-[1px] transition-all flex items-center justify-center gap-3"
                                >
                                    <CreditCard size={18} /> Finalize Audit & Refund
                                </button>
                            )}
                            {(returnReq.status === 'completed' || returnReq.status === 'rejected') && (
                                <div className={`flex-1 md:flex-none px-16 py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] border flex items-center gap-3 ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-500' : 'bg-slate-50 border-slate-200 text-slate-500 shadow-inner'}`}>
                                    <ShieldCheck size={18} className="text-emerald-500" /> Audit Path Fully Committed
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReturnDetail;
