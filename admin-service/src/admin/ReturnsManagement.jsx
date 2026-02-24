import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    RefreshCcw,
    Clock,
    Truck,
    CheckCircle2,
    XCircle,
    ArrowLeft,
    PanelLeftClose,
    PanelLeftOpen
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAdminReturns, logout } from '../api/axios';
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

const ReturnsManagement = () => {
    const navigate = useNavigate();
    const { isDarkMode } = useTheme();
    const [returns, setReturns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    useEffect(() => {
        loadReturns();
    }, []);

    const loadReturns = async () => {
        try {
            setLoading(true);
            const data = await fetchAdminReturns({ search: '' });
            const items = Array.isArray(data) ? data : (data.results || []);
            setReturns(items);
        } catch (error) {
            toast.error('Failed to load return requests');
        } finally {
            setLoading(false);
        }
    };

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
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className={`w-10 h-10 flex items-center justify-center border rounded-xl transition-all shadow-sm active:scale-95 ${isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white' : 'bg-white border-slate-200 text-slate-400 hover:text-orange-600'}`}
                            >
                                <ArrowLeft size={18} />
                            </button>
                            <div>
                                <h1 className="text-xl font-black tracking-tight flex items-center gap-2">
                                    Returns <span className="bg-orange-600/10 text-orange-600 px-2 py-0.5 rounded-md text-[9px] uppercase font-black">Portal</span>
                                </h1>
                                <p className="text-slate-500 font-bold text-[10px] uppercase tracking-widest leading-none">Manage platform reversal requests</p>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={loadReturns}
                        className={`w-10 h-10 flex items-center justify-center border rounded-xl transition-all shadow-sm ${isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white' : 'bg-white border-slate-200 text-slate-400 hover:text-orange-600'}`}
                    >
                        <RefreshCcw size={18} />
                    </button>
                </header>

                <main className="flex-1 overflow-y-auto p-4 md:p-8">
                    <div className="max-w-4xl mx-auto">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center min-h-[400px]">
                                <div className="w-12 h-12 border-4 border-orange-100 border-t-orange-600 rounded-full animate-spin"></div>
                                <p className="mt-4 text-orange-600 font-black uppercase tracking-[0.2em] text-[10px]">Syncing Audit Grid...</p>
                            </div>
                        ) : returns.length === 0 ? (
                            <div className={`rounded-[3rem] p-16 text-center border transition-all ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white/80 backdrop-blur-md border-white shadow-xl shadow-orange-500/5'}`}>
                                <RefreshCcw className="text-orange-200 mx-auto mb-6 opacity-40" size={64} />
                                <h3 className={`text-2xl font-black uppercase tracking-tight mb-2 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>Queue Empty</h3>
                                <p className="text-slate-500 text-sm font-bold uppercase tracking-widest">No pending return requests detected.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 gap-6">
                                <AnimatePresence>
                                    {returns.map((ret, index) => {
                                        const config = STATUS_CONFIG[ret.status] || STATUS_CONFIG.requested;
                                        return (
                                            <motion.div
                                                key={ret.id}
                                                initial={{ opacity: 0, y: 20 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: index * 0.05 }}
                                                onClick={() => navigate(`/returns/${ret.id}`)}
                                                className={`group relative overflow-hidden p-8 rounded-[2.5rem] border transition-all cursor-pointer ${isDarkMode
                                                    ? 'bg-[#1e293b]/50 border-slate-800 hover:border-orange-500/40'
                                                    : 'bg-white/90 backdrop-blur-md border-white hover:border-orange-500 hover:shadow-2xl hover:shadow-orange-500/10'
                                                    }`}
                                            >
                                                <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-orange-400/5 to-purple-500/5 rounded-full translate-x-1/2 -translate-y-1/2 blur-3xl group-hover:opacity-100 transition-opacity opacity-0" />

                                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-3 mb-4">
                                                            <div className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-[0.2em] bg-white shadow-sm border ${isDarkMode ? 'border-slate-700 text-slate-400' : 'border-slate-100 text-slate-400'}`}>
                                                                Order #{ret.order_number}
                                                            </div>
                                                            <div className={`w-2 h-2 rounded-full bg-gradient-to-tr ${config.gradient}`}></div>
                                                        </div>
                                                        <h3 className={`font-black text-2xl leading-tight mb-2 transition-colors uppercase tracking-tight group-hover:text-orange-600 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                                                            {ret.product_name}
                                                        </h3>
                                                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{ret.customer_email}</p>
                                                    </div>

                                                    <div className="flex items-center gap-6">
                                                        <div className="text-right">
                                                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Return Amount</p>
                                                            <p className={`text-2xl font-black ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                                                                ₹{parseFloat(ret.return_amount).toLocaleString()}
                                                            </p>
                                                        </div>
                                                        <div className={`w-16 h-16 rounded-3xl flex items-center justify-center bg-gradient-to-tr ${config.gradient} text-white shadow-2xl rotate-3 group-hover:rotate-0 transition-transform`}>
                                                            <config.icon size={28} />
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="mt-8 pt-6 border-t flex items-center justify-between border-slate-100/50 relative z-10">
                                                    <div className={`px-5 py-2 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-sm border ${config.bg} ${config.color} ${config.border}`}>
                                                        {config.label}
                                                    </div>
                                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                                        View Full Audit Case <ArrowLeft size={12} className="rotate-180" />
                                                    </div>
                                                </div>
                                            </motion.div>
                                        );
                                    })}
                                </AnimatePresence>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default ReturnsManagement;
