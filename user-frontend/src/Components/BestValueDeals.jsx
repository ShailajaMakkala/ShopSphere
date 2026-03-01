import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { fetchDealOfTheDay } from "../Store";

const BestValueDeals = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const deals = useSelector((state) => state.products.dealOfTheDay || []);
    const scrollRef = useRef(null);

    useEffect(() => {
        dispatch(fetchDealOfTheDay());
    }, [dispatch]);

    const handleViewAllDeals = () => {
        navigate("/offer-zone");
    };

    const handleProductClick = (productId) => {
        navigate(`/product/${productId}`);
    };

    if (deals.length === 0) return null;

    return (
        <section className="max-w-[1600px] mx-auto px-3 sm:px-6 md:px-12 py-4 sm:py-8">
            <div className="bg-gradient-to-br from-[#e0f1ff] via-[#f0f9ff] to-[#e4f2ff] rounded-[24px] sm:rounded-[32px] md:rounded-[40px] p-4 sm:p-6 md:p-10 shadow-xl border border-blue-100/50 relative overflow-hidden">
                {/* Decorative elements */}
                <div className="absolute top-0 right-0 w-48 h-48 bg-blue-400/10 rounded-full blur-[60px] -mr-24 -mt-24" />
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-indigo-400/10 rounded-full blur-[60px] -ml-24 -mb-24" />

                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 mb-5 sm:mb-8">
                    <div className="space-y-0.5">
                        <p className="text-blue-500 font-bold tracking-widest text-[9px] uppercase">Flash Sale</p>
                        <h2 className="text-xl sm:text-2xl md:text-3xl font-black text-slate-900 tracking-tight">
                            Deal of the Day
                        </h2>
                    </div>

                    <div className="flex items-center gap-3">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={handleViewAllDeals}
                            className="w-11 h-11 sm:w-12 sm:h-12 bg-slate-900 text-white rounded-xl flex items-center justify-center hover:bg-blue-600 transition-colors shadow-lg active:scale-95 group min-w-[44px] min-h-[44px]"
                        >
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </motion.button>
                    </div>
                </div>

                <div
                    ref={scrollRef}
                    className="relative z-10 flex gap-3 sm:gap-4 overflow-x-auto pb-4 sm:pb-6 scrollbar-hide snap-x"
                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                >
                    {deals.map((deal) => (
                        <motion.div
                            key={deal.id}
                            whileHover={{ y: -6 }}
                            onClick={() => handleProductClick(deal.id)}
                            className="flex-shrink-0 w-[170px] sm:w-[220px] md:w-[260px] bg-white rounded-[20px] sm:rounded-[28px] overflow-hidden shadow-lg shadow-blue-900/5 group border border-white hover:border-blue-200 transition-all duration-300 cursor-pointer flex flex-col snap-start"
                        >
                            <div className="relative h-32 sm:h-40 bg-white overflow-hidden flex items-center justify-center p-3">
                                <img
                                    src={deal.image}
                                    alt={deal.name}
                                    className="max-h-full max-w-full object-contain transition-all duration-700 group-hover:scale-110 drop-shadow-md"
                                />
                                <div className="absolute top-3 left-3 z-20">
                                    <span className="bg-blue-600/90 backdrop-blur-sm text-white text-[8px] font-black px-1.5 py-0.5 rounded-md uppercase tracking-wider shadow-sm">
                                        {deal.category_display || deal.category || "Deal"}
                                    </span>
                                </div>
                                <div className="absolute inset-0 bg-gradient-to-t from-blue-500/0 via-transparent to-transparent group-hover:from-blue-500/5 transition-colors duration-500" />
                            </div>
                            <div className="p-3 sm:p-5 space-y-1 sm:space-y-1.5 flex-grow flex flex-col">
                                <p className="text-blue-500 font-bold text-[9px] uppercase tracking-tight">{deal.vendor_name || "Premium Store"}</p>
                                <h3 className="text-slate-800 font-bold text-xs tracking-tight leading-tight group-hover:text-blue-600 transition-colors line-clamp-1 h-4 mt-1">
                                    {deal.name}
                                </h3>
                                <div className="mt-auto pt-3 flex items-center justify-between">
                                    <div className="flex flex-col">
                                        <p className="text-gray-400 line-through text-[10px]">₹{deal.price + 500}</p>
                                        <p className="text-slate-900 font-black text-lg">
                                            ₹{deal.price}
                                        </p>
                                    </div>
                                    <div className="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center text-blue-500 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
                                        <ArrowRight size={12} />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default BestValueDeals;
