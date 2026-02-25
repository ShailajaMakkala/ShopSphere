import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { FaFacebook, FaTwitter, FaInstagram, FaLinkedin, FaHeart } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";

import HoliBlastReal from "./HoliBlastReal";

const HoliSplash = ({ color, startX, startY }) => {
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * 120 + 40;
    const targetX = Math.cos(angle) * distance;
    const targetY = Math.sin(angle) * distance;

    return (
        <motion.div
            initial={{ x: startX, y: startY, opacity: 0, scale: 0 }}
            animate={{
                x: startX + targetX,
                y: startY + targetY + 80,
                opacity: [0, 1, 1, 0],
                scale: [0, 1.2, 1.5, 0],
            }}
            transition={{
                duration: 2,
                ease: "easeOut"
            }}
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: 25,
                height: 25,
                backgroundColor: color,
                borderRadius: "50% 40% 60% 50% / 50% 60% 40% 50%", // Slightly irregular
                zIndex: 9999,
                pointerEvents: "none",
                willChange: "transform, opacity", // Hardware acceleration
                boxShadow: `0 0 15px ${color}`
            }}
        />
    );
};

const HoliExplosion = ({ x, y, colors }) => {
    return (
        <>
            {[...Array(8)].map((_, i) => ( // Reduced from 15 to 8 for performance
                <HoliSplash
                    key={i}
                    startX={x}
                    startY={y}
                    color={colors[Math.floor(Math.random() * colors.length)]}
                />
            ))}
        </>
    );
};

const Footer = () => {
    const location = useLocation();
    const [isHoliActive, setIsHoliActive] = useState(false);
    const hideOnPaths = ['/delivery', '/vendor', '/vendordashboard', '/welcome', '/login', '/signup', '/account-verification', '/verify-otp'];

    const [crackerPositions, setCrackerPositions] = useState([]);
    const holiColors = ["#ff1ad9", "#ffaa00", "#00ffcc", "#ff3333", "#33ff33", "#3333ff", "#ffff00"];

    const triggerHoli = () => {
        if (isHoliActive) return;
        setIsHoliActive(true);

        // Generate 8-10 color explosions across the screen simultaneously for a smooth look
        const count = Math.floor(Math.random() * 3) + 8;
        const positions = Array.from({ length: count }).map(() => ({
            id: Math.random(),
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight
        }));

        setCrackerPositions(positions);

        // Reduced duration to 3 seconds as the animations are now faster (1s each with delays)
        setTimeout(() => {
            setIsHoliActive(false);
            setCrackerPositions([]);
        }, 3000);

    };

    if (hideOnPaths.some(path => location.pathname.startsWith(path))) {
        return null;
    }

    return (
        <footer className="relative overflow-hidden bg-gradient-to-br from-[#1e0533] via-[#2d1050] to-[#140025] text-white py-10 sm:py-16">
            {/* Decorative elements */}
            <div className="absolute top-0 left-1/4 w-72 h-72 bg-purple-600/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-orange-400/5 rounded-full blur-[150px]" />
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 text-center md:text-left">
                    <div className="flex flex-col items-center md:items-start">
                        <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-orange-400 to-purple-400 bg-clip-text text-transparent">ShopSphere</h3>
                        <p className="text-purple-300/70 text-sm leading-relaxed max-w-xs">Your one-stop shop for everything you need. Quality products, best prices.</p>

                <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 md:gap-12">
                    <div>
                        <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 bg-gradient-to-r from-orange-400 to-purple-400 bg-clip-text text-transparent">ShopSphere</h3>
                        <p className="text-purple-300/70 text-xs sm:text-sm leading-relaxed">Your one-stop shop for everything you need. Quality products, best prices.</p>

                        <div className="flex space-x-3 mt-6">
                            <a href="#" className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-purple-300 hover:bg-orange-400 hover:text-white hover:border-orange-400 transition-all duration-300 min-w-[44px] min-h-[44px]">
                                <FaFacebook size={14} />
                            </a>
                            <a href="#" className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-purple-300 hover:bg-orange-400 hover:text-white hover:border-orange-400 transition-all duration-300 min-w-[44px] min-h-[44px]">
                                <FaTwitter size={14} />
                            </a>
                            <a href="#" className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-purple-300 hover:bg-orange-400 hover:text-white hover:border-orange-400 transition-all duration-300 min-w-[44px] min-h-[44px]">
                                <FaInstagram size={14} />
                            </a>
                            <a href="#" className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-purple-300 hover:bg-orange-400 hover:text-white hover:border-orange-400 transition-all duration-300 min-w-[44px] min-h-[44px]">
                                <FaLinkedin size={14} />
                            </a>
                        </div>
                    </div>
                    <div>
                        <h4 className="text-xs sm:text-sm font-black uppercase tracking-[0.15em] sm:tracking-[0.2em] text-orange-400 mb-4 sm:mb-6">Quick Links</h4>
                        <ul className="space-y-3">
                            <li><a href="/" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>Home</a></li>
                            <li><a href="/shop" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>Shop</a></li>
                            <li><a href="/about" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>About Us</a></li>
                            <li><a href="/contact" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>Contact</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-xs sm:text-sm font-black uppercase tracking-[0.15em] sm:tracking-[0.2em] text-orange-400 mb-4 sm:mb-6">Customer Service</h4>
                        <ul className="space-y-3">
                            <li><a href="/profile" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>My Account</a></li>
                            <li><a href="/orders" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>Order History</a></li>
                            <li><a href="/faq" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>FAQ</a></li>
                            <li><a href="/returns" className="text-purple-300/70 text-sm hover:text-orange-400 transition-colors duration-300 flex items-center gap-2 justify-center md:justify-start"><span className="w-1 h-1 rounded-full bg-purple-500/50"></span>Returns</a></li>
                        </ul>
                    </div>
                    <div className="flex flex-col items-center md:items-end justify-center">
                        <motion.button
                            whileHover={{ scale: 1.1, rotate: [0, -10, 10, 0] }}
                            whileTap={{ scale: 0.9 }}
                            onClick={triggerHoli}
                            className="relative group p-4"
                        >
                            <div className="absolute inset-0 bg-orange-500/20 blur-2xl rounded-full group-hover:bg-orange-500/40 transition-all duration-500" />
                            <img src="/s_logo.png" alt="ShopSphere Logo" className="relative w-40 h-40 object-contain drop-shadow-2xl" />
                        </motion.button>
                    </div>
                </div>

                <AnimatePresence>
                    {isHoliActive && (
                        <>
                            <HoliBlastReal />
                            <div className="fixed inset-0 pointer-events-none z-[9999]">
                                {crackerPositions.map((pos) => (
                                    <HoliExplosion
                                        key={pos.id}
                                        x={pos.x}
                                        y={pos.y}
                                        colors={holiColors}
                                    />
                                ))}
                            </div>
                        </>
                    )}

                </AnimatePresence>

                <div className="border-t border-white/5 mt-12 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">

                </div>
                <div className="border-t border-white/5 mt-8 sm:mt-12 pt-6 sm:pt-8 flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">

                    <p className="text-purple-400/60 text-sm">&copy; {new Date().getFullYear()} ShopSphere. All rights reserved.</p>
                    <p className="text-purple-400/60 text-sm flex items-center gap-1.5">
                        Made with <FaHeart className="text-orange-400 text-xs" /> by ShopSphere Team
                    </p>
                </div>
            </div>
        </footer >
    );
};

export default Footer;
