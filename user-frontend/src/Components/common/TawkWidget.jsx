import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    MessageCircle,
    X,
    Headphones,
    Sparkles,
    Package,
    ShoppingCart,
    Ticket,
    ArrowRight,
    Bot
} from "lucide-react";
import { useNavigate } from "react-router-dom";

/**
 * TawkToWidget - Optimized for Desktop 'Chatbot' size and Mobile 'Full Screen'.
 * Authenticated users only.
 */
const TawkToWidget = () => {
    const navigate = useNavigate();
    const [isHovered, setIsHovered] = useState(false);
    const [isLoaded, setIsLoaded] = useState(false);
    const [showAssistant, setShowAssistant] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("user"));

    useEffect(() => {
        // Sync login state
        const checkAuth = () => setIsLoggedIn(!!localStorage.getItem("user"));
        window.addEventListener('storage', checkAuth);

        if (window.Tawk_API_LOADED) return;
        window.Tawk_API_LOADED = true;

        window.Tawk_API = window.Tawk_API || {};
        window.Tawk_LoadStart = new Date();

        const updateTawkUser = () => {
            if (!window.Tawk_API || typeof window.Tawk_API.setAttributes !== 'function') return;
            const storedUser = localStorage.getItem("user");
            if (storedUser) {
                try {
                    const user = JSON.parse(storedUser);
                    const lastUserId = sessionStorage.getItem("tawk_active_user");
                    if (lastUserId && lastUserId !== String(user.id)) {
                        if (typeof window.Tawk_API.endChat === 'function') window.Tawk_API.endChat();
                    }
                    sessionStorage.setItem("tawk_active_user", String(user.id));
                    window.Tawk_API.setAttributes({
                        'name': user.username || user.name || "User",
                        'email': user.email || ""
                    }, () => { });
                } catch (e) {
                    console.error("Tawk identification error:", e);
                }
            }
        };

        const loadTawk = () => {
            window.Tawk_API.onLoad = function () {
                setTimeout(() => {
                    if (window.Tawk_API) {
                        if (typeof window.Tawk_API.hideWidget === 'function') window.Tawk_API.hideWidget();
                        if (typeof window.Tawk_API.hideLauncher === 'function') window.Tawk_API.hideLauncher();

                        // RESPONSIVE SIZING LOGIC
                        if (window.innerWidth > 768 && typeof window.Tawk_API.setAttributes === 'function') {
                            // Set chatbot-like size for desktop
                            window.Tawk_API.setAttributes({
                                'width': 400,
                                'height': 550
                            }, () => { });
                        }

                        updateTawkUser();
                        setIsLoaded(true);
                    }
                }, 1000);
            };

            window.Tawk_API.onChatMessageVisitor = function () {
                setIsThinking(true);
                setTimeout(() => {
                    setIsThinking(false);
                    setShowAssistant(true);
                }, 1500);
            };

            window.Tawk_API.onChatMinimized = function () {
                if (window.Tawk_API?.hideWidget) window.Tawk_API.hideWidget();
            };
        };

        (function () {
            if (document.getElementById('tawk-to-script')) return;
            var s1 = document.createElement("script");
            var s0 = document.getElementsByTagName("script")[0];
            s1.id = 'tawk-to-script';
            s1.async = true;
            s1.src = "https://embed.tawk.to/6996aef173d8cb1c357e5b4e/1jhq9moas";
            s1.charset = "UTF-8";
            s1.setAttribute("crossorigin", "*");
            s0.parentNode.insertBefore(s1, s0);
            s1.onload = loadTawk;
        })();

        return () => window.removeEventListener('storage', checkAuth);
    }, []);

    const toggleChat = () => {
        if (window.Tawk_API?.maximize) {
            window.Tawk_API.showWidget();
            window.Tawk_API.maximize();
            setShowAssistant(false);
        }
    };

    if (!isLoggedIn) return null;

    const quickActions = [
        { icon: Package, label: "Track My Order", color: "text-orange-500", action: () => navigate('/orders') },
        { icon: ShoppingCart, label: "View My Cart", color: "text-purple-500", action: () => navigate('/cart') },
        { icon: Ticket, label: "Active Coupons", color: "text-green-500", action: () => alert("SHOP20 - 20% OFF!") }
    ];

    return (
        <div className="fixed bottom-6 right-6 z-[9999] flex flex-col items-end gap-3 pointer-events-none">
            <AnimatePresence>
                {isLoaded && (
                    <>
                        {/* Assistant Quick Menu */}
                        {showAssistant && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                                className="bg-white rounded-[28px] shadow-2xl p-5 w-64 border border-orange-50 pointer-events-auto mb-2"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <Bot size={16} className="text-orange-500" />
                                        <span className="text-[11px] font-black text-gray-900 uppercase tracking-widest">Smart Helper</span>
                                    </div>
                                    <X size={14} className="text-gray-400 cursor-pointer" onClick={() => setShowAssistant(false)} />
                                </div>
                                <div className="space-y-2">
                                    {quickActions.map((item, idx) => (
                                        <button key={idx} onClick={item.action} className="w-full flex items-center justify-between p-3 rounded-2xl hover:bg-orange-50 transition-all border border-transparent hover:border-orange-100">
                                            <div className="flex items-center gap-3">
                                                <item.icon size={18} className={item.color} />
                                                <span className="text-xs font-bold text-gray-700">{item.label}</span>
                                            </div>
                                            <ArrowRight size={14} className="text-gray-300 group-hover:text-orange-400" />
                                        </button>
                                    ))}
                                </div>
                                <button onClick={toggleChat} className="w-full mt-4 py-3 bg-gradient-to-r from-orange-400 to-purple-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg">
                                    Talk to Human
                                </button>
                            </motion.div>
                        )}

                        {/* Standard Tooltip */}
                        {!showAssistant && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.8, x: 20 }}
                                animate={isHovered ? { opacity: 1, scale: 1, x: 0 } : { opacity: 0, scale: 0.8, x: 20 }}
                                className="bg-white rounded-2xl shadow-2xl p-4 border border-orange-50 w-48 pointer-events-auto"
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <Headphones size={14} className="text-orange-500" />
                                    <span className="text-[11px] font-black text-gray-900 uppercase tracking-widest">
                                        {isThinking ? "Thinking..." : "Support Online"}
                                    </span>
                                </div>
                                <p className="text-[10px] text-gray-500 font-bold leading-relaxed">
                                    {isThinking ? "Assistant is analyzing..." : "Need help? Chat with our experts!"}
                                </p>
                            </motion.div>
                        )}

                        {/* Floating Button */}
                        <motion.button
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onMouseEnter={() => setIsHovered(true)}
                            onMouseLeave={() => setIsHovered(false)}
                            onClick={() => setShowAssistant(!showAssistant)}
                            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-400 via-purple-500 to-purple-600 shadow-xl flex items-center justify-center text-white relative pointer-events-auto overflow-hidden"
                        >
                            <div className="absolute top-3 right-3 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse" />
                            <div className="relative z-10">
                                {isThinking ? (
                                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }}>
                                        <Sparkles size={28} />
                                    </motion.div>
                                ) : showAssistant ? <X size={28} /> : <MessageCircle size={28} />}
                            </div>
                        </motion.button>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

export default TawkToWidget;
