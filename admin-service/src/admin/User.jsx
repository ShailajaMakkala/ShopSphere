import React, { useState, useMemo, useEffect } from 'react';
import {
    Users,
    Search,
    PanelLeftClose,
    PanelLeftOpen,
    Ban,
    UserCheck,
    Filter,
    ShieldCheck,
    AlertTriangle,
    ArrowUpRight,
    SearchX,
    Clock,
    Mail,
    Loader2,
    RefreshCcw,
    AlertCircle,
    Menu,
    ChevronDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import NotificationBell from '../components/NotificationBell';
import { useUsers } from '../context/UserContext';
import { useTheme } from '../context/ThemeContext';
import { logout } from '../api/axios';
import { toast } from 'react-hot-toast';

const UserManagement = () => {
    const { users, isLoading, error, stats, updateUserStatus, reloadUsers } = useUsers();
    const { isDarkMode } = useTheme();
    const [isSidebarOpen, setIsSidebarOpen] = useState(() => window.innerWidth >= 1024);
    const [searchTerm, setSearchTerm] = useState('');
    const [activeTab, setActiveTab] = useState('ALL');
    const [roleFilter, setRoleFilter] = useState('ALL');
    const [isActionModalOpen, setIsActionModalOpen] = useState(false);
    const [pendingAction, setPendingAction] = useState(null);
    const [isActioning, setIsActioning] = useState(false);
    const [blockReason, setBlockReason] = useState('');

    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 768) setIsSidebarOpen(false);
            else if (window.innerWidth >= 1024) setIsSidebarOpen(true);
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const tabCounts = useMemo(() => ({
        ALL: stats.total,
        ACTIVE: stats.active,
        BLOCKED: stats.blocked
    }), [stats]);

    const filteredUsers = useMemo(() => {
        return users.filter(user => {
            const matchesSearch = (user.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                (user.email || '').toLowerCase().includes(searchTerm.toLowerCase());
            const matchesTab = activeTab === 'ALL' || user.status === activeTab;
            const matchesRole = roleFilter === 'ALL' || user.role === roleFilter;
            return matchesSearch && matchesTab && matchesRole;
        });
    }, [users, searchTerm, activeTab, roleFilter]);

    const handleActionClick = (user, action) => {
        setPendingAction({ user, action });
        setIsActionModalOpen(true);
        setBlockReason('');
    };

    const confirmAction = async () => {
        if (!pendingAction) return;
        setIsActioning(true);
        const success = await updateUserStatus(
            pendingAction.user.id,
            pendingAction.action === 'BLOCK' ? 'BLOCKED' : 'ACTIVE',
            blockReason
        );

        if (success) {
            toast.success(`User successfully ${pendingAction.action === 'BLOCK' ? 'restricted' : 'restored'}`);
            setIsActionModalOpen(false);
            setBlockReason('');
        } else {
            toast.error('Governance operation failed. Check system logs.');
        }
        setIsActioning(false);
    };

    const getStatusStyles = (status) => {
        switch (status) {
            case 'ACTIVE': return isDarkMode ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-emerald-50 text-emerald-600 border-emerald-100';
            case 'BLOCKED': return isDarkMode ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-rose-50 text-rose-500 border-rose-100';
            default: return isDarkMode ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-slate-50 text-slate-500 border-slate-100';
        }
    };

    const getRiskColor = (score) => {
        if (score >= 70) return { bar: 'bg-rose-500', text: 'text-rose-500 font-bold' };
        if (score >= 40) return { bar: 'bg-amber-400', text: 'text-amber-500 font-bold' };
        return { bar: isDarkMode ? 'bg-emerald-500' : 'bg-emerald-400', text: isDarkMode ? 'text-emerald-400 font-medium' : 'text-emerald-600 font-medium' };
    };

    const getRoleStyles = (role) => {
        switch (role) {
            case 'vendor': return isDarkMode ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-blue-50 text-blue-600 border-blue-100';
            case 'delivery': return isDarkMode ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 'bg-purple-50 text-purple-600 border-purple-100';
            default: return isDarkMode ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-slate-50 text-slate-500 border-slate-100';
        }
    };

    // Mobile card view for user
    const UserCard = ({ user }) => (
        <div className={`p-4 rounded-2xl border transition-all ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white border-slate-100 shadow-sm'}`}>
            <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center font-semibold text-base shrink-0 ${isDarkMode ? 'bg-[#0f172a] border-slate-800 text-blue-400' : 'bg-white border-slate-100 text-blue-600'}`}>
                    {(user.name || user.email || '?').charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                    <div className={`text-sm font-bold truncate ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{user.name || '—'}</div>
                    <div className="flex items-center gap-2">
                        <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase border ${getRoleStyles(user.role)}`}>
                            {user.role === 'customer' ? 'User' : user.role === 'vendor' ? 'Merchant' : 'Agent'}
                        </span>
                        <div className="text-[10px] text-slate-500 font-bold uppercase">UID #{user.id}</div>
                    </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-[9px] font-semibold uppercase border shrink-0 ${getStatusStyles(user.status)}`}>
                    {user.status}
                </span>
            </div>

            <div className="space-y-2 mb-3">
                <div className={`flex items-center gap-2 text-xs ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    <Mail className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span className="truncate">{user.email}</span>
                </div>
                <div className={`flex items-center gap-2 text-xs ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                    <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{user.joinDate}</span>
                </div>
            </div>

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1">
                    <span className={`text-[11px] ${getRiskColor(user.riskScore ?? 0).text}`}>{user.riskScore ?? 0}%</span>
                    <div className={`h-1.5 flex-1 max-w-[80px] rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
                        <div className={`h-full transition-all duration-700 ${getRiskColor(user.riskScore ?? 0).bar}`} style={{ width: `${user.riskScore ?? 0}%` }} />
                    </div>
                </div>

                {user.status === 'ACTIVE' ? (
                    <button
                        onClick={() => handleActionClick(user, 'BLOCK')}
                        className={`flex items-center gap-1.5 px-3 py-2 text-[10px] font-semibold uppercase rounded-xl transition-all border ${isDarkMode
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/20 hover:bg-rose-500 hover:text-white'
                            : 'bg-rose-50 text-rose-600 border-rose-200 hover:bg-rose-600 hover:text-white'
                            }`}
                    >
                        <Ban className="w-3 h-3" /> Block
                    </button>
                ) : (
                    <button
                        onClick={() => handleActionClick(user, 'UNBLOCK')}
                        className={`flex items-center gap-1.5 px-3 py-2 text-[10px] font-semibold uppercase rounded-xl transition-all border ${isDarkMode
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500 hover:text-white'
                            : 'bg-emerald-50 text-emerald-600 border-emerald-200 hover:bg-emerald-600 hover:text-white'
                            }`}
                    >
                        <UserCheck className="w-3 h-3" /> Restore
                    </button>
                )}
            </div>
        </div>
    );

    return (
        <div className={`flex h-screen font-sans overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a] text-slate-100' : 'bg-[#F8FAFC] text-slate-900'}`}>
            <Sidebar isSidebarOpen={isSidebarOpen} setIsSidebarOpen={setIsSidebarOpen} activePage="Users" onLogout={logout} />

            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className={`border-b px-4 sm:px-6 lg:px-8 py-3 sm:py-4 lg:py-5 flex items-center justify-between z-20 sticky top-0 transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a]/80 border-slate-800 backdrop-blur-md' : 'bg-white border-slate-200'}`}>
                    <div className="flex items-center gap-2 sm:gap-4">
                        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`}>
                            <span className="md:hidden"><Menu className="w-5 h-5" /></span>
                            <span className="hidden md:block">
                                {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
                            </span>
                        </button>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className={`text-base sm:text-lg lg:text-xl font-bold ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>User Governance</h1>
                                <span className="bg-emerald-500/10 text-emerald-500 text-[9px] font-semibold px-2 py-0.5 rounded-full uppercase border border-emerald-500/20 tracking-normal leading-none hidden sm:inline-flex">Live</span>
                            </div>
                            <p className="text-[9px] sm:text-[10px] text-slate-500 font-bold uppercase tracking-normal hidden sm:block">Access control and status management</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-4">
                        <button
                            onClick={() => reloadUsers()}
                            disabled={isLoading}
                            className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 ${isLoading ? 'opacity-50' : 'bg-gradient-to-r from-blue-600 to-emerald-600 hover:scale-105'}`}
                        >
                            <RefreshCcw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                            <span className="hidden sm:inline">Refresh</span>
                        </button>
                        <NotificationBell />
                        <div className={`hidden xl:flex items-center border rounded-full px-3 py-1.5 text-[9px] font-semibold uppercase tracking-normal gap-2 ${isDarkMode ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' : 'bg-blue-50 border-blue-100 text-blue-600'}`}>
                            <ShieldCheck className="w-3.5 h-3.5" /> SuperAdmin
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 lg:p-8 space-y-4 sm:space-y-6 lg:space-y-8">
                    {/* Stat Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
                        <StatCard label="Total Registered" value={stats.total} icon={Users} color="blue" isDarkMode={isDarkMode} />
                        <StatCard label="Active Users" value={stats.active} icon={UserCheck} color="emerald" isDarkMode={isDarkMode} />
                        <StatCard label="Restricted Access" value={stats.blocked} icon={Ban} color="rose" isDarkMode={isDarkMode} />
                    </div>

                    {/* Error banner */}
                    {error && (
                        <div className={`flex items-center gap-3 p-4 sm:p-5 rounded-xl sm:rounded-2xl border ${isDarkMode ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-rose-50 border-rose-100 text-rose-600'}`}>
                            <AlertCircle className="w-5 h-5 shrink-0" />
                            <span className="text-sm font-semibold flex-1">{error}</span>
                            <button onClick={() => reloadUsers()} className="ml-auto text-xs font-semibold underline shrink-0">Retry</button>
                        </div>
                    )}

                    {/* Toolbar */}
                    <div className="flex flex-col gap-3 sm:gap-4 lg:flex-row lg:gap-6 items-stretch lg:items-center justify-between">
                        {/* Tabs */}
                        <div className={`flex p-1 rounded-xl sm:rounded-2xl border shadow-sm w-full lg:w-auto overflow-x-auto transition-colors duration-300 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white border-slate-200'}`}>
                            {['ALL', 'ACTIVE', 'BLOCKED'].map(tab => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`flex-1 lg:flex-none px-4 sm:px-6 py-2.5 rounded-lg sm:rounded-xl text-[10px] font-semibold uppercase tracking-normal transition-all whitespace-nowrap ${activeTab === tab
                                        ? isDarkMode ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'bg-slate-900 text-white shadow-lg'
                                        : isDarkMode ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-50'
                                        }`}
                                >
                                    {tab}
                                    <span className={`ml-1.5 sm:ml-2 px-1.5 py-0.5 rounded-md text-[9px] ${activeTab === tab ? 'bg-white/20 text-white' : isDarkMode ? 'bg-slate-800 text-slate-500' : 'bg-slate-100 text-slate-500'}`}>
                                        {tabCounts[tab]}
                                    </span>
                                </button>
                            ))}
                        </div>

                        {/* Search & Role Filter */}
                        <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full lg:w-auto">
                            <select
                                value={roleFilter}
                                onChange={(e) => setRoleFilter(e.target.value)}
                                className={`w-full sm:w-40 px-4 py-3 border rounded-xl sm:rounded-2xl text-xs font-semibold uppercase tracking-normal focus:outline-none focus:ring-4 transition-all ${isDarkMode ? 'bg-slate-900 border-slate-800 text-white focus:ring-blue-500/10 focus:border-blue-500' : 'bg-white border-slate-200 text-slate-900 focus:ring-blue-500/5 focus:border-blue-500'}`}
                            >
                                <option value="ALL">All Roles</option>
                                <option value="customer">Customers</option>
                                <option value="vendor">Merchants</option>
                                <option value="delivery">Delivery Agents</option>
                            </select>
                            <div className="relative flex-1 lg:w-80">
                                <Search className={`absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                                <input
                                    type="text"
                                    placeholder="Search by name or email..."
                                    className={`w-full pl-11 pr-4 py-3 border rounded-xl sm:rounded-2xl text-sm focus:outline-none focus:ring-4 transition-all font-medium ${isDarkMode ? 'bg-slate-900 border-slate-800 text-white focus:ring-blue-500/10 focus:border-blue-500' : 'bg-white border-slate-200 text-slate-900 focus:ring-blue-500/5 focus:border-blue-500'}`}
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Users - Table on desktop, Cards on mobile */}
                    {/* Mobile Card View */}
                    <div className="block lg:hidden space-y-3">
                        {isLoading ? (
                            Array(3).fill(0).map((_, i) => (
                                <div key={i} className={`animate-pulse p-4 rounded-2xl border ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-100'}`}>
                                    <div className={`h-16 rounded-xl w-full ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`} />
                                </div>
                            ))
                        ) : filteredUsers.length > 0 ? (
                            filteredUsers.map(user => <UserCard key={user.id} user={user} />)
                        ) : (
                            <div className="flex flex-col items-center text-center py-12">
                                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 border ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-100'}`}>
                                    <SearchX className="w-8 h-8 text-slate-300" />
                                </div>
                                <h3 className={`text-base font-bold mb-1 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>No matches found</h3>
                                <p className="text-sm text-slate-400 font-medium max-w-xs">Broaden your search criteria or adjust the filters.</p>
                            </div>
                        )}
                    </div>

                    {/* Desktop Table View */}
                    <div className={`hidden lg:block rounded-[2.5rem] border shadow-sm overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800' : 'bg-white border-slate-200'}`}>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead className={`border-b transition-colors duration-300 ${isDarkMode ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50/50 border-slate-100'}`}>
                                    <tr>
                                        {['User Details', 'Role', 'Contact', 'Risk Potential', 'Account Status', 'Joined Date', 'Governance'].map(h => (
                                            <th key={h} className="px-8 py-5 text-[10px] font-semibold text-slate-500 uppercase tracking-normal">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className={`divide-y transition-colors duration-300 ${isDarkMode ? 'divide-slate-800' : 'divide-slate-50'}`}>
                                    {isLoading ? (
                                        Array(5).fill(0).map((_, i) => (
                                            <tr key={i} className="animate-pulse">
                                                <td colSpan="6" className="px-8 py-8"><div className={`h-10 rounded-2xl w-full ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`} /></td>
                                            </tr>
                                        ))
                                    ) : filteredUsers.length > 0 ? (
                                        filteredUsers.map(user => (
                                            <tr key={user.id} className={`group transition-colors ${isDarkMode ? 'hover:bg-slate-800/50' : 'hover:bg-slate-50/50'}`}>
                                                <td className="px-8 py-6">
                                                    <div className="flex items-center gap-4">
                                                        <div className={`w-12 h-12 rounded-2xl shadow-sm border flex items-center justify-center font-semibold text-lg transition-all ${isDarkMode ? 'bg-[#0f172a] border-slate-800 text-blue-400 group-hover:border-blue-500' : 'bg-white border-slate-100 text-blue-600 group-hover:scale-110'}`}>
                                                            {(user.name || user.email || '?').charAt(0).toUpperCase()}
                                                        </div>
                                                        <div>
                                                            <div className={`text-sm font-bold mb-0.5 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{user.name || '—'}</div>
                                                            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-normal">UID #{user.id}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase border whitespace-nowrap ${getRoleStyles(user.role)}`}>
                                                        {user.role === 'customer' ? 'Customer' : user.role === 'vendor' ? 'Merchant' : 'Agent'}
                                                    </span>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className={`flex items-center gap-2 text-xs font-bold ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                                        <Mail className="w-3.5 h-3.5 text-slate-500" /> {user.email}
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="group/risk relative flex flex-col gap-2 min-w-[120px]">
                                                        <div className="flex items-center justify-between text-[11px] tracking-normal">
                                                            <span className={getRiskColor(user.riskScore ?? 0).text}>{user.riskScore ?? 0}%</span>
                                                            {(user.riskScore ?? 0) >= 70 && <AlertTriangle className="w-3 h-3 text-rose-500" />}
                                                        </div>
                                                        <div className={`h-1.5 w-full rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
                                                            <div
                                                                className={`h-full transition-all duration-700 ${getRiskColor(user.riskScore ?? 0).bar}`}
                                                                style={{ width: `${user.riskScore ?? 0}%` }}
                                                            />
                                                        </div>
                                                        <div className="absolute bottom-full left-0 mb-2 hidden group-hover/risk:flex flex-col gap-1 bg-[#1e293b] text-white text-[10px] font-bold rounded-xl px-3 py-2.5 shadow-2xl z-10 w-44 border border-slate-700">
                                                            <div className="text-slate-400 uppercase tracking-normal mb-1">Risk Breakdown</div>
                                                            <div className="flex justify-between"><span className="text-slate-400">Cancelled Orders</span><span>{user.cancelled_orders ?? 0}</span></div>
                                                            <div className="flex justify-between"><span className="text-slate-400">Return Requests</span><span>{user.return_requests ?? 0}</span></div>
                                                            <div className="flex justify-between"><span className="text-slate-400">Failed Payments</span><span>{user.failed_payments ?? 0}</span></div>
                                                            <div className="flex justify-between"><span className="text-slate-400">Total Orders</span><span>{user.total_orders ?? 0}</span></div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="flex flex-col gap-1">
                                                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-normal border w-fit transition-all ${getStatusStyles(user.status)}`}>
                                                            {user.status}
                                                        </span>
                                                        {user.status === 'BLOCKED' && user.blocked_reason && (
                                                            <span className="text-[10px] text-slate-500 font-medium truncate max-w-[160px]" title={user.blocked_reason}>
                                                                {user.blocked_reason}
                                                            </span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className={`flex items-center gap-2 text-xs font-bold ${isDarkMode ? 'text-slate-400' : 'text-slate-700'}`}>
                                                        <Clock className="w-3.5 h-3.5 text-slate-500" /> {user.joinDate}
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="flex items-center gap-2">
                                                        {user.status === 'ACTIVE' ? (
                                                            <button
                                                                onClick={() => handleActionClick(user, 'BLOCK')}
                                                                className={`flex items-center gap-2 px-4 py-2 text-[10px] font-semibold uppercase tracking-normal rounded-xl transition-all border shadow-sm ${isDarkMode
                                                                    ? 'bg-rose-500/10 text-rose-400 border-rose-500/20 hover:bg-rose-500 hover:text-white'
                                                                    : 'bg-rose-50 text-rose-600 border-rose-200 hover:bg-rose-600 hover:text-white'
                                                                    }`}
                                                            >
                                                                <Ban className="w-3.5 h-3.5" /> Block
                                                            </button>
                                                        ) : (
                                                            <button
                                                                onClick={() => handleActionClick(user, 'UNBLOCK')}
                                                                className={`flex items-center gap-2 px-4 py-2 text-[10px] font-semibold uppercase tracking-normal rounded-xl transition-all border shadow-sm ${isDarkMode
                                                                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500 hover:text-white'
                                                                    : 'bg-emerald-50 text-emerald-600 border-emerald-200 hover:bg-emerald-600 hover:text-white'
                                                                    }`}
                                                            >
                                                                <UserCheck className="w-3.5 h-3.5" /> Restore
                                                            </button>
                                                        )}
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="6" className="px-8 py-20">
                                                <div className="flex flex-col items-center text-center">
                                                    <div className="w-20 h-20 bg-slate-50 rounded-[2rem] flex items-center justify-center mb-6 border border-slate-100 shadow-inner">
                                                        <SearchX className="w-10 h-10 text-slate-300" />
                                                    </div>
                                                    <h3 className="text-lg font-bold text-slate-900 mb-1">No matches found</h3>
                                                    <p className="text-sm text-slate-400 font-medium max-w-xs">Broaden your search criteria or adjust the filters to find the intended accounts.</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                        <div className={`px-8 py-4 flex items-center justify-between border-t transition-colors duration-300 ${isDarkMode ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50/50 border-slate-100'}`}>
                            <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-normal">
                                Live Directory • {filteredUsers.length} of {users.length} Users
                            </div>
                            <div className="flex items-center gap-4 text-[10px] font-semibold text-slate-500 tracking-normal uppercase transition-colors">
                                ISO Compliance Secured <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
                            </div>
                        </div>
                    </div>
                </main >
            </div >

            {/* Confirmation Modal */}
            < AnimatePresence >
                {isActionModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-slate-950/60 backdrop-blur-md"
                            onClick={() => !isActioning && setIsActionModalOpen(false)}
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
                            className={`rounded-2xl sm:rounded-[2.5rem] p-6 sm:p-10 max-w-sm w-full relative z-10 shadow-2xl border transition-colors duration-300 ${isDarkMode ? 'bg-[#1e293b] border-slate-700' : 'bg-white border-slate-100'}`}
                        >
                            <div className={`w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-[2rem] flex items-center justify-center mb-6 sm:mb-8 border mx-auto ${pendingAction?.action === 'BLOCK' ? 'bg-rose-500/10 border-rose-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
                                {pendingAction?.action === 'BLOCK' ? <AlertTriangle className="w-8 h-8 sm:w-10 sm:h-10 text-rose-500" /> : <ShieldCheck className="w-8 h-8 sm:w-10 sm:h-10 text-emerald-500" />}
                            </div>
                            <h2 className={`text-xl sm:text-2xl font-semibold text-center mb-3 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>Governance Event</h2>
                            <p className="text-sm text-slate-500 text-center font-bold leading-relaxed mb-6 px-2 sm:px-4">
                                {pendingAction?.action === 'BLOCK' ? (
                                    <>You are about to <span className="text-rose-500">Restrict Access</span> for <span className={`${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{pendingAction?.user.name}</span>.</>
                                ) : (
                                    <>You are about to <span className="text-emerald-500">Restore Access</span> for <span className={`${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{pendingAction?.user.name}</span>.</>
                                )}
                            </p>

                            {pendingAction?.action === 'BLOCK' && (
                                <textarea
                                    placeholder="Reason for blocking (optional)"
                                    value={blockReason}
                                    onChange={e => setBlockReason(e.target.value)}
                                    rows={2}
                                    className={`w-full mb-6 px-4 py-3 border rounded-xl sm:rounded-2xl text-sm font-bold transition-all resize-none focus:outline-none focus:ring-4 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-white focus:ring-rose-500/10 focus:border-rose-500/50' : 'bg-slate-50 border-slate-200 text-slate-700 focus:ring-rose-500/10 focus:border-rose-400'}`}
                                />
                            )}

                            <div className="flex flex-col gap-3 sm:gap-4">
                                <button
                                    onClick={confirmAction}
                                    disabled={isActioning}
                                    className={`w-full py-3.5 sm:py-4 text-white rounded-xl sm:rounded-2xl text-[10px] font-semibold uppercase tracking-normal shadow-xl transition-all flex items-center justify-center gap-2 ${pendingAction?.action === 'BLOCK' ? 'bg-rose-600 shadow-rose-900/40 hover:bg-rose-500' : 'bg-gradient-to-r from-blue-600 to-emerald-600 shadow-blue-900/40 hover:scale-[1.02]'}`}
                                >
                                    {isActioning ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm Authorization'}
                                </button>
                                <button
                                    onClick={() => setIsActionModalOpen(false)}
                                    disabled={isActioning}
                                    className={`w-full py-3.5 sm:py-4 border rounded-xl sm:rounded-2xl text-[10px] font-semibold uppercase tracking-normal transition-all ${isDarkMode ? 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'}`}
                                >
                                    Cancel
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence >
        </div >
    );
};

const StatCard = ({ label, value, icon: Icon, color, isDarkMode }) => {
    const colors = {
        blue: isDarkMode ? 'text-blue-400 bg-blue-500/10 border-blue-500/20 shadow-blue-500/5' : 'text-blue-600 bg-blue-50 border-blue-100 shadow-blue-500/5',
        rose: isDarkMode ? 'text-rose-400 bg-rose-500/10 border-rose-500/20 shadow-rose-500/5' : 'text-rose-500 bg-rose-50 border-rose-100 shadow-rose-500/5',
        emerald: isDarkMode ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20 shadow-emerald-500/5' : 'text-emerald-600 bg-emerald-50 border-emerald-100 shadow-emerald-500/5',
    };

    return (
        <div className={`p-5 sm:p-6 lg:p-8 rounded-2xl sm:rounded-[1.5rem] lg:rounded-[2rem] border shadow-sm relative group overflow-hidden transition-all duration-300 ${isDarkMode ? 'bg-[#1e293b]/50 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-100 hover:border-slate-200'}`}>
            <div className={`absolute top-0 right-0 p-8 scale-150 opacity-10 group-hover:scale-125 transition-transform duration-1000 ${colors[color].split(' ')[0]}`}>
                <Icon className="w-24 h-24" />
            </div>
            <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl flex items-center justify-center mb-4 sm:mb-6 shadow-sm border transition-colors duration-300 ${colors[color]}`}>
                <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div className={`text-[10px] font-semibold uppercase tracking-normal mb-1 ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>{label}</div>
            <div className="flex items-end justify-between">
                <div className={`text-2xl sm:text-3xl font-semibold leading-none ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{value ?? '—'}</div>
                <div className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-1 rounded-lg ${isDarkMode ? 'bg-emerald-500/10 text-emerald-400' : 'bg-emerald-50 text-emerald-500'}`}>
                    <ArrowUpRight className="w-3 h-3" /> LIVE
                </div>
            </div>
        </div>
    );
};

export default UserManagement;
