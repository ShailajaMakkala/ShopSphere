import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ShoppingBag,
    Filter,
    LayoutGrid,
    List,
    Search,
    X,
    Tag,
    DollarSign,
    Store as StoreIcon,
    ChevronDown,
    ChevronUp,
    Heart,
    ShoppingCart,
    Zap
} from 'lucide-react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchProducts, AddToCart, AddToWishlist, RemoveFromWishlist } from '../../Store';
import toast from 'react-hot-toast';
import ProductCard from '../../Components/ProductCard';

const CATEGORIES = [
    { id: "all", label: "All Products" },
    { id: "electronics", label: "Electronics" },
    { id: "sports_fitness", label: "Sports & Fitness" },
    { id: "fashion", label: "Fashion" },
    { id: "books", label: "Books" },
    { id: "home_kitchen", label: "Home & Kitchen" },
    { id: "grocery", label: "Groceries" },
    { id: "beauty_personal_care", label: "Beauty & Care" },
    { id: "toys_games", label: "Toys & Games" },
    { id: "automotive", label: "Automotive" },
    { id: "services", label: "Services" },
    { id: "other", label: "Other" },
];

const PRICE_RANGES = [
    { id: "all", label: "Any Price" },
    { id: "0-500", label: "Under ₹500", min: 0, max: 500 },
    { id: "500-2000", label: "₹500 – ₹2,000", min: 500, max: 2000 },
    { id: "2000-5000", label: "₹2,000 – ₹5,000", min: 2000, max: 5000 },
    { id: "5000-15000", label: "₹5,000 – ₹15,000", min: 5000, max: 15000 },
    { id: "15000+", label: "Above ₹15,000", min: 15000, max: Infinity },
];

const Shop = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedPriceRange, setSelectedPriceRange] = useState('all');
    const [viewMode, setViewMode] = useState('grid');
    const [isFilterOpen, setIsFilterOpen] = useState(false);

    const allProducts = useSelector((state) => state.products.all || []);
    const isLoading = useSelector((state) => state.products.isLoading);
    const wishlist = useSelector((state) => state.wishlist);

    useEffect(() => {
        dispatch(fetchProducts());
    }, [dispatch]);

    const filteredProducts = useMemo(() => {
        const priceRange = PRICE_RANGES.find(p => p.id === selectedPriceRange);
        return allProducts.filter((item) => {
            const matchCat = selectedCategory === 'all' || item.category?.toLowerCase() === selectedCategory;
            const matchPrice = !priceRange || priceRange.id === 'all'
                ? true
                : item.price >= priceRange.min && item.price <= priceRange.max;
            const matchSearch = !searchQuery
                ? true
                : item.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.description?.toLowerCase().includes(searchQuery.toLowerCase());
            return matchCat && matchPrice && matchSearch;
        });
    }, [allProducts, selectedCategory, selectedPriceRange, searchQuery]);

    const handleWishlistClick = (item) => {
        if (!localStorage.getItem("accessToken")) {
            toast.error("Please login to manage your wishlist");
            navigate("/login"); return;
        }
        if (wishlist.some(w => w.name === item.name)) {
            dispatch(RemoveFromWishlist(item));
            toast.success("Removed from wishlist");
        } else {
            dispatch(AddToWishlist(item));
            toast.success("Added to wishlist");
        }
    };

    const handleAddToCartClick = (item) => {
        if (!localStorage.getItem("accessToken")) {
            toast.error("Please login to add items to your cart");
            navigate("/login"); return;
        }
        dispatch(AddToCart(item));
        toast.success("Added to cart");
    };

    const handleBuyNow = (item) => {
        if (!localStorage.getItem("accessToken")) {
            toast.error("Please login to purchase");
            navigate("/login"); return;
        }
        dispatch(AddToCart(item));
        navigate("/checkout");
    };

    const isInWishlist = (itemName) => wishlist.some(w => w.name === itemName);

    if (isLoading && allProducts.length === 0) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-6">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 dark:text-white mb-2">Shop All Products</h1>
                        <p className="text-gray-500 font-medium">Explore our entire collection of {allProducts.length} premium products.</p>
                    </div>

                    <div className="flex flex-wrap items-center gap-4">
                        {/* Search Bar */}
                        <div className="relative group">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-600 transition-colors" size={18} />
                            <input
                                type="text"
                                placeholder="Search products..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-12 pr-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-sm font-semibold outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all w-full md:w-72"
                            />
                        </div>

                        <button
                            onClick={() => setIsFilterOpen(!isFilterOpen)}
                            className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-700 dark:text-gray-300 font-bold hover:bg-gray-50 dark:hover:bg-gray-700 transition-all shadow-sm"
                        >
                            <Filter className="w-4 h-4" />
                            Filters
                        </button>

                        <div className="flex bg-gray-200 dark:bg-gray-700 rounded-2xl p-1">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-2 rounded-xl transition-all ${viewMode === 'grid' ? 'bg-white dark:bg-gray-800 shadow-sm text-blue-600' : 'text-gray-500'}`}
                            >
                                <LayoutGrid className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-2 rounded-xl transition-all ${viewMode === 'list' ? 'bg-white dark:bg-gray-800 shadow-sm text-blue-600' : 'text-gray-500'}`}
                            >
                                <List className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Filters Collapse */}
                <AnimatePresence>
                    {isFilterOpen && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="bg-white dark:bg-gray-800 rounded-3xl p-6 mb-8 shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                                <div>
                                    <h3 className="text-xs font-black uppercase tracking-widest text-gray-400 mb-4">Categories</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {CATEGORIES.map(cat => (
                                            <button
                                                key={cat.id}
                                                onClick={() => setSelectedCategory(cat.id)}
                                                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${selectedCategory === cat.id ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'}`}
                                            >
                                                {cat.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-xs font-black uppercase tracking-widest text-gray-400 mb-4">Price Range</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {PRICE_RANGES.map(range => (
                                            <button
                                                key={range.id}
                                                onClick={() => setSelectedPriceRange(range.id)}
                                                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${selectedPriceRange === range.id ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'}`}
                                            >
                                                {range.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Product Grid */}
                {filteredProducts.length > 0 ? (
                    <div className={viewMode === 'grid'
                        ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"
                        : "flex flex-col gap-6"
                    }>
                        {filteredProducts.map((item) => (
                            <ProductCard
                                key={item.id}
                                item={item}
                                navigate={navigate}
                                handleWishlistClick={handleWishlistClick}
                                handleAddToCartClick={handleAddToCartClick}
                                handleBuyNow={handleBuyNow}
                                isInWishlist={isInWishlist}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 bg-white dark:bg-gray-800 rounded-[3rem] border border-dashed border-gray-200 dark:border-gray-700">
                        <ShoppingBag className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No products found</h3>
                        <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                            We couldn't find any products matching your current filters. Try adjusting them to see more!
                        </p>
                        <button
                            onClick={() => { setSelectedCategory('all'); setSelectedPriceRange('all'); setSearchQuery(''); }}
                            className="mt-6 px-8 py-3 bg-blue-600 text-white rounded-2xl font-bold hover:bg-blue-700 transition-all"
                        >
                            Reset All Filters
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Shop;
