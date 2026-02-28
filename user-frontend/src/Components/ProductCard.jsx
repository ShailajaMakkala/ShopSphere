import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaHeart, FaShoppingBag, FaStar } from "react-icons/fa";

export default function ProductCard({
    item,
    navigate,
    handleWishlistClick,
    handleAddToCartClick,
    handleBuyNow,
    isInWishlist,
}) {
    const [currentImgIndex, setCurrentImgIndex] = useState(0);

    // Prepare gallery from item.images or item.gallery
    const gallery = (item.images || item.gallery || []).map(img => {
        let imgPath = typeof img === 'string' ? img : (img.image || img.url);
        if (!imgPath) return "/public/placeholder.jpg";
        if (imgPath.startsWith('http')) return imgPath;
        if (imgPath.startsWith('/')) return `http://localhost:8000${imgPath}`;
        return `http://localhost:8000/${imgPath}`;
    });

    // Fallback image
    const displayImage = gallery.length > 0 ? gallery[currentImgIndex] : (item.image || "/public/placeholder.jpg");

    useEffect(() => {
        if (gallery.length > 1) {
            const interval = setInterval(() => {
                setCurrentImgIndex((prev) => (prev + 1) % gallery.length);
            }, 3000);
            return () => clearInterval(interval);
        }
    }, [gallery.length]);

    return (
        <motion.div
            whileHover={{ y: -10 }}
            className="group bg-white rounded-3xl shadow-lg cursor-pointer h-full flex flex-col"
            onClick={() => navigate(`/product/${item.id}`)}
        >
            <div className="relative h-40 sm:h-48 md:h-56 overflow-hidden rounded-t-2xl sm:rounded-t-3xl bg-gray-50 flex items-center justify-center p-3">
                <AnimatePresence mode="wait">
                    <motion.img
                        key={displayImage}
                        src={displayImage}
                        className="max-w-full max-h-full object-contain transition-all duration-700 group-hover:scale-110"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.5 }}
                    />
                </AnimatePresence>

                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleWishlistClick(item);
                    }}
                    className="absolute top-2 sm:top-4 right-2 sm:right-4 bg-white/80 backdrop-blur-md p-2 rounded-full shadow-md z-10 hover:bg-white transition-all min-w-[36px] min-h-[36px] sm:min-w-[40px] sm:min-h-[40px] flex items-center justify-center"
                >
                    <FaHeart
                        className={isInWishlist(item.name) ? "text-red-500" : "text-gray-400"}
                    />
                </button>
            </div>

            <div className="p-3 sm:p-4 flex flex-col flex-1">
                <div className="flex-1">
                    {/* Product Name */}
                    <h3 className="font-bold text-sm sm:text-base md:text-lg text-gray-900 group-hover:text-orange-400 transition-colors line-clamp-1 leading-tight">
                        {item.name}
                    </h3>

                    {/* Rating Section */}
                    <div className="flex items-center gap-1 sm:gap-2 mt-1.5 sm:mt-2">
                        <div className="flex items-center gap-1 bg-orange-50 px-2 py-0.5 rounded-lg border border-orange-100">
                            <span className="text-[11px] font-black text-orange-400">
                                {Number(item.average_rating || 0).toFixed(1)}
                            </span>
                            <FaStar className="text-[10px] text-yellow-400 mb-0.5" />
                        </div>

                        <div className="flex gap-0.5 ml-1">
                            {[...Array(5)].map((_, i) => (
                                <FaStar
                                    key={i}
                                    className={`text-[10px] ${i < Math.floor(item.average_rating || 0) ? "text-yellow-400" : "text-gray-200"}`}
                                />
                            ))}
                        </div>
                    </div>

                    <p className="text-gray-500 text-[10px] sm:text-xs line-clamp-1 mt-1 sm:mt-1.5 leading-tight">{item.description}</p>

                    {/* Brand Badge - visible below description */}
                    {item.brand && (
                        <div className="mt-3">
                            <span
                                className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-orange-50 text-orange-500 border border-orange-200 cursor-pointer hover:bg-orange-100 transition-colors"
                                onClick={(e) => { e.stopPropagation(); navigate(`/brand/${item.brand}`); }}
                            >
                                <span className="w-2 h-2 rounded-full bg-orange-400 inline-block" />
                                {item.brand}
                            </span>
                        </div>
                    )}
                </div>

                <div className="flex justify-between items-center mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-100">
                    <div className="flex flex-col">
                        <span className="text-[9px] sm:text-xs text-gray-400 font-bold uppercase tracking-wider">Price</span>
                        <span className="font-black text-base sm:text-lg md:text-xl text-gray-900">₹{parseFloat(item.price).toFixed(2)}</span>
                    </div>
                    <div className="flex gap-2">
                        {handleAddToCartClick && (
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleAddToCartClick(item);
                                }}
                                className="bg-gradient-to-r from-orange-400 to-purple-500 text-white p-3 rounded-xl hover:from-orange-600 hover:to-purple-700 transition-all shadow-lg active:scale-95 flex items-center justify-center min-w-[44px]"
                            >
                                <FaShoppingBag />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}