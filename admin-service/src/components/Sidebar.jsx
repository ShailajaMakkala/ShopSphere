import React, { useEffect, useRef, useCallback } from 'react';
import {
    LayoutDashboard,
    Users,
    Store,
    Package,
    ShoppingCart,
    BarChart3,
    Settings,
    ClipboardList,
    Sun,
    Moon,
    LogOut,
    MessageSquare,
    RefreshCcw,
    X
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';

const Sidebar = ({ isSidebarOpen, setIsSidebarOpen, activePage = 'Dashboard', onLogout }) => {
    const navigate = useNavigate();
    const { isDarkMode, toggleTheme } = useTheme();
    const sidebarRef = useRef(null);
    const touchStartX = useRef(0);
    const touchCurrentX = useRef(0);

    const menuItems = [
        { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
        { name: 'Users', icon: Users, path: '/users' },
        { name: 'Vendors', icon: Store, path: '/vendors' },
        { name: 'Vendor Requests', icon: ClipboardList, path: '/vendors/requests' },
        { name: 'Orders', icon: ClipboardList, path: '/orders' },
        { name: 'Returns', icon: RefreshCcw, path: '/returns' },
        { name: 'Delivery Agents', icon: Store, path: '/delivery/agents' },
        { name: 'Delivery Requests', icon: ClipboardList, path: '/delivery/requests' },
        { name: 'Products', icon: Package, path: '/products' },
        { name: 'Reports', icon: BarChart3, path: '/reports' },
        { name: 'Deletion Requests', icon: ClipboardList, path: '/deletion-requests' },
        { name: 'Commission Settings', icon: Settings, path: '/settings/commission' },
        { name: 'Queries', icon: MessageSquare, path: '/queries' },
    ];

    // Determine device type based on window width
    const getDeviceType = useCallback(() => {
        if (typeof window === 'undefined') return 'desktop';
        if (window.innerWidth < 768) return 'mobile';
        if (window.innerWidth < 1024) return 'tablet';
        return 'desktop';
    }, []);

    // Close sidebar on mobile when navigating
    const handleNavClick = (path) => {
        navigate(path);
        if (getDeviceType() === 'mobile') {
            setIsSidebarOpen(false);
        }
    };

    // Swipe-to-close logic for mobile
    useEffect(() => {
        const sidebar = sidebarRef.current;
        if (!sidebar) return;

        const handleTouchStart = (e) => {
            touchStartX.current = e.touches[0].clientX;
        };

        const handleTouchMove = (e) => {
            touchCurrentX.current = e.touches[0].clientX;
        };

        const handleTouchEnd = () => {
            const diff = touchStartX.current - touchCurrentX.current;
            // If swiped left more than 80px, close the sidebar
            if (diff > 80 && getDeviceType() === 'mobile') {
                setIsSidebarOpen(false);
            }
        };

        sidebar.addEventListener('touchstart', handleTouchStart, { passive: true });
        sidebar.addEventListener('touchmove', handleTouchMove, { passive: true });
        sidebar.addEventListener('touchend', handleTouchEnd, { passive: true });

        return () => {
            sidebar.removeEventListener('touchstart', handleTouchStart);
            sidebar.removeEventListener('touchmove', handleTouchMove);
            sidebar.removeEventListener('touchend', handleTouchEnd);
        };
    }, [getDeviceType, setIsSidebarOpen]);

    const deviceType = getDeviceType();
    const isMobile = deviceType === 'mobile';
    const isTablet = deviceType === 'tablet';

    // Mobile: full-screen drawer overlay
    if (isMobile) {
        return (
            <AnimatePresence>
                {isSidebarOpen && (
                    <>
                        {/* Overlay */}
                        <Motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60]"
                            onClick={() => setIsSidebarOpen(false)}
                        />
                        {/* Drawer */}
                        <Motion.aside
                            ref={sidebarRef}
                            initial={{ x: '-100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '-100%' }}
                            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                            className={`fixed inset-y-0 left-0 z-[70] w-72 border-r overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-[#0f172a] border-slate-800' : 'bg-white border-slate-100'}`}
                        >
                            <div className={`flex flex-col h-full ${isDarkMode ? 'bg-[#0f172a]' : 'bg-white'}`}>
                                {/* Header with close button */}
                                <div className={`flex items-center justify-between p-5 border-b transition-colors duration-300 ${isDarkMode ? 'border-slate-800' : 'border-slate-100'}`}>
                                    <div className="flex items-center gap-0 group cursor-pointer" onClick={() => handleNavClick('/dashboard')}>
                                        <img src="/s_logo.png" alt="ShopSphere" className="w-12 h-12 object-contain" />
                                        <div className="flex flex-col -ml-3">
                                            <span className={`text-lg font-bold leading-none tracking-wide ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                                                hopSphere
                                            </span>
                                            <span className="text-[9px] font-semibold uppercase tracking-normal mt-0.5 text-slate-500">Admin Portal</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setIsSidebarOpen(false)}
                                        className={`p-2 rounded-xl transition-all ${isDarkMode ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`}
                                    >
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>

                                {/* Navigation */}
                                <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto custom-scrollbar">
                                    {menuItems.map((item) => {
                                        const isActive = item.name === activePage;
                                        return (
                                            <button
                                                key={item.name}
                                                onClick={() => handleNavClick(item.path)}
                                                className={`flex items-center gap-3 px-4 py-3.5 text-sm font-semibold rounded-xl transition-all duration-200 group w-full text-left ${isActive
                                                    ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white shadow-lg shadow-blue-500/20'
                                                    : isDarkMode ? 'text-slate-400 hover:bg-slate-800/50 hover:text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-blue-600'
                                                    }`}
                                            >
                                                <item.icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : isDarkMode ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-400 group-hover:text-blue-600'}`} />
                                                <span className="flex-1 truncate">{item.name}</span>
                                            </button>
                                        );
                                    })}
                                </nav>

                                {/* Bottom Section */}
                                <div className="p-3 mt-auto space-y-2">
                                    <button
                                        onClick={toggleTheme}
                                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-300 group ${isDarkMode
                                            ? 'bg-slate-800/40 border-slate-700 text-amber-400 hover:bg-slate-800'
                                            : 'bg-slate-50 border-slate-100 text-blue-600 hover:bg-white shadow-sm'
                                            }`}
                                    >
                                        {isDarkMode ? (
                                            <div className="flex items-center gap-3 w-full">
                                                <Sun className="w-4 h-4" />
                                                <span className="text-xs font-bold uppercase tracking-normal">Light Mode</span>
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-3 w-full">
                                                <Moon className="w-4 h-4" />
                                                <span className="text-xs font-bold uppercase tracking-normal text-slate-600">Dark Mode</span>
                                            </div>
                                        )}
                                    </button>

                                    <div className={`flex items-center gap-3 p-3 rounded-xl border transition-colors duration-300 ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-100'}`}>
                                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-emerald-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20 text-sm shrink-0">
                                            A
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-xs font-semibold truncate ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>ADMIN USER</p>
                                            <p className="text-[10px] text-slate-500 font-bold truncate">SUPER ADMIN</p>
                                        </div>
                                        <button
                                            onClick={onLogout}
                                            className={`p-2 rounded-lg transition-all shrink-0 ${isDarkMode ? 'hover:bg-slate-700 text-slate-500 hover:text-rose-400' : 'hover:bg-white text-slate-400 hover:text-rose-600'}`}
                                            title="Logout"
                                        >
                                            <LogOut className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </Motion.aside>
                    </>
                )}
            </AnimatePresence>
        );
    }

    // Tablet: icons-only collapsed sidebar (always visible)
    if (isTablet) {
        return (
            <Motion.aside
                initial={false}
                animate={{
                    width: isSidebarOpen ? '16rem' : '4.5rem',
                }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className={`relative z-40 border-r overflow-hidden transition-colors duration-300 shrink-0 ${isDarkMode ? 'bg-[#0f172a] border-slate-800' : 'bg-white border-slate-100'}`}
            >
                <div className={`flex flex-col h-full ${isSidebarOpen ? 'w-64' : 'w-[4.5rem]'} ${isDarkMode ? 'bg-[#0f172a]' : 'bg-white'}`}>
                    <div className={`flex items-center ${isSidebarOpen ? 'justify-between p-5' : 'justify-center p-4'} border-b transition-colors duration-300 ${isDarkMode ? 'border-slate-800' : 'border-slate-100'}`}>
                        {isSidebarOpen ? (
                            <div className="flex items-center gap-0 group cursor-pointer" onClick={() => navigate('/dashboard')}>
                                <img src="/s_logo.png" alt="ShopSphere" className="w-14 h-14 object-contain" />
                                <div className="flex flex-col -ml-4">
                                    <span className={`text-lg font-bold leading-none tracking-wide ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                                        hopSphere
                                    </span>
                                    <span className="text-[9px] font-semibold uppercase tracking-normal mt-0.5 text-slate-500">Admin Portal</span>
                                </div>
                            </div>
                        ) : (
                            <div className="cursor-pointer" onClick={() => navigate('/dashboard')}>
                                <img src="/s_logo.png" alt="ShopSphere" className="w-10 h-10 object-contain" />
                            </div>
                        )}
                    </div>

                    <nav className={`flex-1 ${isSidebarOpen ? 'px-4' : 'px-2'} py-4 space-y-1 overflow-y-auto custom-scrollbar`}>
                        {menuItems.map((item) => {
                            const isActive = item.name === activePage;
                            return (
                                <button
                                    key={item.name}
                                    onClick={() => navigate(item.path)}
                                    title={!isSidebarOpen ? item.name : ''}
                                    className={`flex items-center ${isSidebarOpen ? 'gap-3 px-4' : 'justify-center px-0'} py-3 text-sm font-semibold rounded-xl transition-all duration-200 group w-full ${isActive
                                        ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white shadow-lg shadow-blue-500/20'
                                        : isDarkMode ? 'text-slate-400 hover:bg-slate-800/50 hover:text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-blue-600'
                                        }`}
                                >
                                    <item.icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : isDarkMode ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-400 group-hover:text-blue-600'}`} />
                                    {isSidebarOpen && <span className="flex-1 truncate text-left">{item.name}</span>}
                                </button>
                            );
                        })}
                    </nav>

                    <div className={`${isSidebarOpen ? 'p-4' : 'p-2'} mt-auto space-y-2`}>
                        <button
                            onClick={toggleTheme}
                            title={!isSidebarOpen ? (isDarkMode ? 'Light Mode' : 'Dark Mode') : ''}
                            className={`w-full flex items-center ${isSidebarOpen ? 'gap-3 px-4' : 'justify-center'} py-3 rounded-xl border transition-all duration-300 ${isDarkMode
                                ? 'bg-slate-800/40 border-slate-700 text-amber-400'
                                : 'bg-slate-50 border-slate-100 text-blue-600 shadow-sm'
                                }`}
                        >
                            {isDarkMode ? <Sun className="w-4 h-4 shrink-0" /> : <Moon className="w-4 h-4 shrink-0" />}
                            {isSidebarOpen && (
                                <span className={`text-xs font-bold uppercase tracking-normal ${isDarkMode ? '' : 'text-slate-600'}`}>
                                    {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                                </span>
                            )}
                        </button>

                        <div className={`flex items-center ${isSidebarOpen ? 'gap-3 p-3' : 'justify-center p-2'} rounded-xl border transition-colors duration-300 ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-100'}`}>
                            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-emerald-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20 text-sm shrink-0">
                                A
                            </div>
                            {isSidebarOpen && (
                                <>
                                    <div className="flex-1 min-w-0">
                                        <p className={`text-xs font-semibold truncate ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>ADMIN USER</p>
                                        <p className="text-[10px] text-slate-500 font-bold truncate">SUPER ADMIN</p>
                                    </div>
                                    <button
                                        onClick={onLogout}
                                        className={`p-2 rounded-lg transition-all shrink-0 ${isDarkMode ? 'hover:bg-slate-700 text-slate-500 hover:text-rose-400' : 'hover:bg-white text-slate-400 hover:text-rose-600'}`}
                                    >
                                        <LogOut className="w-4 h-4" />
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </Motion.aside>
        );
    }

    // Desktop: full sidebar (original behavior)
    return (
        <Motion.aside
            initial={false}
            animate={{
                width: isSidebarOpen ? '16rem' : '0rem',
                opacity: isSidebarOpen ? 1 : 0,
            }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className={`relative z-40 border-r overflow-hidden transition-colors duration-300 shrink-0 ${isDarkMode ? 'bg-[#0f172a] border-slate-800' : 'bg-white border-slate-100'}`}
        >
            <div className={`flex flex-col h-full w-64 ${isDarkMode ? 'bg-[#0f172a]' : 'bg-white'}`}>
                <div className={`flex items-center justify-between p-6 border-b transition-colors duration-300 ${isDarkMode ? 'border-slate-800' : 'border-slate-100'}`}>
                    <div className="flex items-center gap-0 group cursor-pointer relative -translate-y-1.5" onClick={() => navigate('/dashboard')}>
                        <img src="/s_logo.png" alt="ShopSphere" className="w-16 h-16 object-contain transition-transform duration-300 group-hover:scale-105" />
                        <div className="flex flex-col -ml-5">
                            <span className={`text-xl font-bold leading-none tracking-wide transition-colors duration-300 group-hover:text-blue-400 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                                hopSphere
                            </span>
                            <span className="text-[9px] font-semibold uppercase tracking-normal mt-0.5 text-slate-500">Admin Portal</span>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto custom-scrollbar">
                    {menuItems.map((item) => {
                        const isActive = item.name === activePage;
                        return (
                            <button
                                key={item.name}
                                onClick={() => navigate(item.path)}
                                className={`flex items-center gap-3 px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 group w-full text-left ${isActive
                                    ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white shadow-lg shadow-blue-500/20'
                                    : isDarkMode ? 'text-slate-400 hover:bg-slate-800/50 hover:text-white' : 'text-slate-500 hover:bg-slate-50 hover:text-blue-600'
                                    }`}
                            >
                                <item.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : isDarkMode ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-400 group-hover:text-blue-600'}`} />
                                <span className="flex-1">{item.name}</span>
                            </button>
                        );
                    })}
                </nav>

                <div className="p-4 mt-auto space-y-3">
                    <button
                        onClick={toggleTheme}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-300 group ${isDarkMode
                            ? 'bg-slate-800/40 border-slate-700 text-amber-400 hover:bg-slate-800 hover:border-amber-400/50'
                            : 'bg-slate-50 border-slate-100 text-blue-600 hover:bg-white hover:border-blue-200 shadow-sm'
                            }`}
                    >
                        {isDarkMode ? (
                            <div className="flex items-center gap-3 w-full">
                                <Sun className="w-4 h-4 transition-transform group-hover:rotate-45" />
                                <span className="text-xs font-bold uppercase tracking-normal">Light Mode</span>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3 w-full">
                                <Moon className="w-4 h-4 transition-transform group-hover:-rotate-12" />
                                <span className="text-xs font-bold uppercase tracking-normal text-slate-600">Dark Mode</span>
                            </div>
                        )}
                    </button>

                    <div className={`flex items-center gap-3 p-3 rounded-xl border transition-colors duration-300 ${isDarkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-100'}`}>
                        <div className="relative group">
                            <div className={`absolute inset-0 blur-md opacity-20 bg-blue-600 rounded-full transition-opacity group-hover:opacity-40`}></div>
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-emerald-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20 relative z-10">
                                A
                            </div>
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className={`text-xs font-semibold truncate transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>ADMIN USER</p>
                            <p className="text-[10px] text-slate-500 font-bold truncate">SUPER ADMIN</p>
                        </div>
                        <button
                            onClick={onLogout}
                            className={`p-2 rounded-lg transition-all ${isDarkMode ? 'hover:bg-slate-700 text-slate-500 hover:text-rose-400' : 'hover:bg-white text-slate-400 hover:text-rose-600 shadow-sm hover:shadow-md'}`}
                            title="Logout"
                        >
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </Motion.aside>
    );
};

export default Sidebar;
