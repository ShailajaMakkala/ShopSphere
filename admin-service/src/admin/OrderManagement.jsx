import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import {
    PanelLeftClose,
    PanelLeftOpen,
    ClipboardList,
    Search,
    Filter,
    Calendar,
    ChevronLeft,
    ChevronRight,
    Package,
    ArrowUpRight,
    Hash,
    Activity,
    ShieldCheck,
    Zap,
    BarChart3,
    Menu
} from 'lucide-react';
import { fetchAdminOrders, logout } from '../api/axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '../context/ThemeContext';
import NotificationBell from '../components/NotificationBell';

const OrderManagement = () => {
    const navigate = useNavigate();
    const { isDarkMode } = useTheme();
    const [orders, setOrders] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(() => window.innerWidth >= 1024);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 768) setIsSidebarOpen(false);
            else if (window.innerWidth >= 1024) setIsSidebarOpen(true);
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const loadOrders = async () => {
        setIsLoading(true);
        try {
            const data = await fetchAdminOrders({
                page: currentPage,
                search: searchTerm,
                status: statusFilter
            });
            setOrders(data.results || []);
            setTotalPages(Math.ceil(data.count / 20) || 1);
        } catch (error) {
            console.error("Failed to fetch orders", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadOrders();
    }, [currentPage, statusFilter]);

    const handleSearch = (e) => {
        e.preventDefault();
        setCurrentPage(1);
        loadOrders();
    };

    const getStatusColor = (status) => {
        const s = (status || '').toLowerCase();
        switch (s) {
            case 'pending': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
            case 'confirmed': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
            case 'processing': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
            case 'shipping':
            case 'shipped': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'out_for_delivery': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
            case 'delivered': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'cancelled': return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
            default: return isDarkMode ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-slate-50 text-slate-600 border-slate-100';
        }
    };

    // Mobile order card
    const OrderCard = ({ order, index }) => (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => navigate(`/orders/${order.id}`)}
            className={`p-4 rounded-2xl border cursor-pointer transition-all active:scale-[0.98] ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800 hover:border-blue-500/30' : 'bg-white border-slate-100 shadow-sm hover:shadow-md'}`}
        >
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl border flex items-center justify-center shrink-0 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-blue-400' : 'bg-white shadow-sm border-slate-100 text-blue-600'}`}>
                        <Hash className="w-4 h-4" />
                    </div>
                    <div>
                        <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{order.order_number}</div>
                        <div className="text-[9px] text-slate-500 font-semibold uppercase flex items-center gap-1 mt-0.5">
                            <Calendar className="w-3 h-3" /> {new Date(order.created_at).toLocaleDateString()}
                        </div>
                    </div>
                </div>
                <span className={`px-3 py-1.5 rounded-lg text-[9px] font-semibold uppercase border ${getStatusColor(order.status)}`}>
                    {order.status}
                </span>
            </div>
            <div className="flex items-center justify-between">
                <div className={`text-xs font-bold truncate flex-1 mr-3 ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>{order.customer_email}</div>
                <div className={`text-base font-semibold shrink-0 ${isDarkMode ? 'text-blue-400' : 'text-blue-700'}`}>₹{parseFloat(order.total_amount).toLocaleString()}</div>
            </div>
        </motion.div>
    );

    return (
        <div className={`flex h-screen font-sans overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a] text-slate-100' : 'bg-[#F8FAFC] text-slate-900'}`}>
            <Sidebar isSidebarOpen={isSidebarOpen} setIsSidebarOpen={setIsSidebarOpen} activePage="Orders" onLogout={logout} />

            <div className="flex-1 flex flex-col min-w-0 transition-all duration-300">
                <header className={`border-b px-4 sm:px-6 lg:px-8 h-14 sm:h-16 lg:h-20 flex items-center justify-between sticky top-0 z-20 transition-all duration-300 ${isDarkMode ? 'bg-[#0f172a]/80 border-slate-800 backdrop-blur-md' : 'bg-white border-slate-100 shadow-sm'}`}>
                    <div className="flex items-center gap-2 sm:gap-4">
                        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className={`p-2 rounded-xl border transition-all ${isDarkMode ? 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white' : 'bg-white border-slate-200 text-slate-400 hover:text-blue-600 shadow-sm'}`}>
                            <span className="md:hidden"><Menu className="w-5 h-5" /></span>
                            <span className="hidden md:block">
                                {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
                            </span>
                        </button>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className={`text-sm sm:text-base lg:text-lg font-semibold tracking-normal ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>Execution Grid</h1>
                                <span className={`text-[8px] font-semibold px-1.5 py-0.5 rounded-md uppercase tracking-normal hidden sm:inline-flex ${isDarkMode ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-blue-50 text-blue-600 border border-blue-100'}`}>Real-time</span>
                            </div>
                            <p className="text-[9px] sm:text-[10px] text-slate-500 font-bold uppercase tracking-normal hidden sm:block">Global Order Synchronization</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-4 lg:gap-6">
                        <NotificationBell />
                        <div className={`hidden xl:flex items-center border rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase tracking-normal gap-2 ${isDarkMode ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                            <Zap className="w-3.5 h-3.5" /> Core Status
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 lg:p-8 bg-transparent">
                    <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6 lg:space-y-8">
                        {/* Stats - 2 col mobile, 4 col desktop */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
                            {[
                                { label: 'Total Volume', value: orders.length, icon: BarChart3, color: 'blue' },
                                { label: 'Active Transit', value: orders.filter(o => ['shipped', 'out_for_delivery'].includes(o.status?.toLowerCase())).length, icon: Activity, color: 'emerald' },
                                { label: 'Clearance', value: orders.filter(o => o.status?.toLowerCase() === 'delivered').length, icon: ShieldCheck, color: 'emerald' },
                                { label: 'Pending Auth', value: orders.filter(o => o.status?.toLowerCase() === 'pending').length, icon: Calendar, color: 'amber' }
                            ].map((stat, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className={`p-4 sm:p-5 lg:p-6 rounded-2xl sm:rounded-[2rem] lg:rounded-[2.5rem] border transition-all duration-300 group ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800 hover:border-slate-700 hover:bg-[#1e293b]/80' : 'bg-white border-slate-100 shadow-sm hover:shadow-xl'}`}
                                >
                                    <div className="flex items-center gap-3 sm:gap-5">
                                        <div className={`w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center transition-all group-hover:scale-110 shrink-0 ${stat.color === 'blue' ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-600') :
                                            stat.color === 'emerald' ? (isDarkMode ? 'bg-emerald-500/10 text-emerald-400' : 'bg-emerald-50 text-emerald-600') :
                                                (isDarkMode ? 'bg-amber-500/10 text-amber-400' : 'bg-amber-50 text-amber-600')
                                            }`}>
                                            <stat.icon className="w-5 h-5 sm:w-6 sm:h-6" />
                                        </div>
                                        <div>
                                            <p className="text-[8px] sm:text-[9px] font-semibold uppercase tracking-normal text-slate-500 mb-0.5 sm:mb-1">{stat.label}</p>
                                            <p className={`text-lg sm:text-xl lg:text-2xl font-semibold tracking-normal ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{stat.value}</p>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Search & Filter - Stack on mobile */}
                        <div className={`p-3 sm:p-4 rounded-2xl sm:rounded-[2.5rem] lg:rounded-[3rem] border transition-all duration-300 flex flex-col md:flex-row gap-3 sm:gap-4 items-stretch md:items-center ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white border-slate-100 shadow-sm'}`}>
                            <form onSubmit={handleSearch} className="relative flex-1 w-full group">
                                <Search className={`absolute left-4 sm:left-5 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors ${isDarkMode ? 'text-slate-500 group-focus-within:text-blue-400' : 'text-slate-400 group-focus-within:text-blue-600'}`} />
                                <input
                                    type="text"
                                    placeholder="Trace command (ID, Email)..."
                                    className={`w-full pl-10 sm:pl-12 pr-4 sm:pr-6 py-3 sm:py-4 rounded-xl sm:rounded-[2rem] text-sm focus:outline-none focus:ring-4 transition-all font-bold tracking-normal uppercase ${isDarkMode
                                        ? 'bg-slate-900/50 border-slate-800 text-white placeholder-slate-600 focus:ring-blue-500/10 focus:border-blue-500'
                                        : 'bg-slate-50 border-transparent text-slate-900 placeholder-slate-400 focus:ring-blue-500/5 focus:bg-white focus:border-blue-200 shadow-inner'
                                        }`}
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </form>
                            <div className="flex items-center gap-3 w-full md:w-auto">
                                <div className={`px-3 sm:px-4 py-3 sm:py-4 rounded-xl sm:rounded-[2rem] flex items-center gap-3 flex-1 md:min-w-[220px] transition-colors ${isDarkMode ? 'bg-slate-900/50 border border-slate-800' : 'bg-slate-100'}`}>
                                    <Filter className="w-4 h-4 text-slate-500 shrink-0" />
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => {
                                            setStatusFilter(e.target.value);
                                            setCurrentPage(1);
                                        }}
                                        className="bg-transparent text-[10px] font-semibold uppercase tracking-normal focus:outline-none w-full text-slate-400"
                                    >
                                        <option value="">Status: Universal</option>
                                        <option value="pending">Pending Auth</option>
                                        <option value="processing">In Processor</option>
                                        <option value="shipping">Logistics Transit</option>
                                        <option value="out_for_delivery">Final Mile</option>
                                        <option value="delivered">Success Final</option>
                                        <option value="cancelled">Node Kill</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Orders - Cards on mobile, Table on desktop */}
                        {/* Mobile Card View */}
                        <div className="block lg:hidden space-y-3">
                            <AnimatePresence>
                                {isLoading ? (
                                    Array(3).fill(0).map((_, i) => (
                                        <div key={i} className={`animate-pulse p-4 rounded-2xl border ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-100'}`}>
                                            <div className={`h-16 rounded-xl w-full ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`} />
                                        </div>
                                    ))
                                ) : orders.length === 0 ? (
                                    <div className="flex flex-col items-center text-center py-16">
                                        <Package className="mx-auto mb-4 w-12 h-12 opacity-20" />
                                        <p className="text-sm text-slate-500 font-semibold">No orders found</p>
                                    </div>
                                ) : (
                                    orders.map((order, index) => (<OrderCard key={order.id} order={order} index={index} />))
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Desktop Table View */}
                        <div className={`hidden lg:block rounded-[3rem] border overflow-hidden transition-all duration-300 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800 shadow-sm shadow-blue-500/5' : 'bg-white border-slate-100 shadow-md'}`}>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead className={`border-b transition-colors duration-300 ${isDarkMode ? 'bg-slate-900/40 border-slate-800' : 'bg-slate-50/50 border-slate-100'}`}>
                                        <tr>
                                            {['Transmission Identity', 'Entity Endpoint', 'Payload Value', 'Logistics Protocol', 'Admin Control'].map(h => (
                                                <th key={h} className="px-10 py-6 text-[10px] font-semibold text-slate-500 uppercase tracking-normal">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className={`divide-y transition-colors duration-300 ${isDarkMode ? 'divide-slate-800' : 'divide-slate-50'}`}>
                                        <AnimatePresence>
                                            {isLoading ? (
                                                Array(5).fill(0).map((_, i) => (
                                                    <tr key={i} className="animate-pulse">
                                                        <td colSpan="5" className="px-10 py-10"><div className={`h-14 rounded-3xl w-full ${isDarkMode ? 'bg-slate-800/50' : 'bg-slate-100'}`} /></td>
                                                    </tr>
                                                ))
                                            ) : orders.length === 0 ? (
                                                <motion.tr
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    exit={{ opacity: 0 }}
                                                >
                                                    <td colSpan="5" className="px-10 py-32 text-center text-slate-500 uppercase tracking-normal font-semibold opacity-50">
                                                        <Package className="mx-auto mb-6 w-16 h-16 opacity-10" />
                                                        No Signals Detected in this domain
                                                    </td>
                                                </motion.tr>
                                            ) : orders.map((order, index) => (
                                                <motion.tr
                                                    key={order.id}
                                                    initial={{ opacity: 0, x: -10 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: index * 0.05 }}
                                                    className={`group transition-all duration-300 ${isDarkMode ? 'hover:bg-blue-500/5' : 'hover:bg-blue-50/50'}`}
                                                >
                                                    <td className="px-10 py-8">
                                                        <div className="flex items-center gap-6">
                                                            <div className={`w-14 h-14 rounded-2xl border flex items-center justify-center transition-all duration-500 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-blue-400 group-hover:border-blue-500/30' : 'bg-white shadow-sm border-slate-100 text-blue-600 group-hover:border-blue-200'}`}>
                                                                <Hash className="w-6 h-6" />
                                                            </div>
                                                            <div>
                                                                <div className={`text-base font-semibold tracking-normal ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{order.order_number}</div>
                                                                <div className="text-[9px] text-slate-500 font-semibold uppercase tracking-normal flex items-center gap-2 mt-1">
                                                                    <Calendar className="w-3.5 h-3.5" /> {new Date(order.created_at).toLocaleDateString()}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-10 py-8">
                                                        <div className={`text-xs font-bold tracking-normal ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>{order.customer_email}</div>
                                                    </td>
                                                    <td className="px-10 py-8">
                                                        <div className={`text-lg font-semibold ${isDarkMode ? 'text-blue-400' : 'text-blue-700'}`}>₹{parseFloat(order.total_amount).toLocaleString()}</div>
                                                    </td>
                                                    <td className="px-10 py-8">
                                                        <span className={`px-4 py-2 rounded-xl text-[9px] font-semibold uppercase tracking-normal border transition-all ${getStatusColor(order.status)}`}>
                                                            {order.status}
                                                        </span>
                                                    </td>
                                                    <td className="px-10 py-8">
                                                        <button
                                                            onClick={() => navigate(`/orders/${order.id}`)}
                                                            className={`flex items-center gap-3 px-6 py-3 rounded-2xl text-[10px] font-semibold uppercase tracking-normal transition-all border group/btn ${isDarkMode ? 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-blue-500/50 hover:bg-blue-500/10' : 'bg-white border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-600 hover:shadow-lg hover:shadow-blue-500/10 active:scale-95'}`}
                                                        >
                                                            Open Nexus <ArrowUpRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1" />
                                                        </button>
                                                    </td>
                                                </motion.tr>
                                            ))}
                                        </AnimatePresence>
                                    </tbody>
                                </table>
                            </div>

                            <div className={`px-10 py-8 border-t flex items-center justify-between transition-colors ${isDarkMode ? 'bg-slate-900/30 border-slate-800' : 'bg-slate-50/50 border-slate-100'}`}>
                                <div className="flex items-center gap-4">
                                    <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-normal">Data Page</span>
                                    <div className={`px-4 py-2 rounded-xl text-[10px] font-semibold transition-all ${isDarkMode ? 'bg-slate-900 text-blue-400' : 'bg-white text-blue-600 shadow-sm'}`}>
                                        {currentPage} / {totalPages}
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button
                                        disabled={currentPage === 1}
                                        onClick={() => setCurrentPage(prev => prev - 1)}
                                        className={`p-3 rounded-2xl transition-all border disabled:opacity-20 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800' : 'bg-white border-slate-100 text-slate-400 hover:text-blue-600 shadow-sm hover:shadow-md'}`}
                                    >
                                        <ChevronLeft className="w-6 h-6" />
                                    </button>
                                    <button
                                        disabled={currentPage === totalPages}
                                        onClick={() => setCurrentPage(prev => prev + 1)}
                                        className={`p-3 rounded-2xl transition-all border disabled:opacity-20 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800' : 'bg-white border-slate-100 text-slate-400 hover:text-blue-600 shadow-sm hover:shadow-md'}`}
                                    >
                                        <ChevronRight className="w-6 h-6" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Mobile Pagination */}
                        <div className="flex lg:hidden items-center justify-between py-2">
                            <div className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold ${isDarkMode ? 'bg-slate-800 text-blue-400' : 'bg-white text-blue-600 shadow-sm'}`}>
                                {currentPage} / {totalPages}
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    disabled={currentPage === 1}
                                    onClick={() => setCurrentPage(prev => prev - 1)}
                                    className={`p-2.5 rounded-xl transition-all border disabled:opacity-20 ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-400' : 'bg-white border-slate-200 text-slate-400 shadow-sm'}`}
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                </button>
                                <button
                                    disabled={currentPage === totalPages}
                                    onClick={() => setCurrentPage(prev => prev + 1)}
                                    className={`p-2.5 rounded-xl transition-all border disabled:opacity-20 ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-400' : 'bg-white border-slate-200 text-slate-400 shadow-sm'}`}
                                >
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default OrderManagement;
