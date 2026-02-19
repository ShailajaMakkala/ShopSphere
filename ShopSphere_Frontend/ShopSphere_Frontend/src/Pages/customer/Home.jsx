import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { fetchProducts, AddToCart, AddToWishlist, RemoveFromWishlist } from "../../Store";
import toast from "react-hot-toast";
import ProductCard from "../../components/ProductCard";

const CATEGORIES = [
  { id: "All", label: "All Products" },
  { id: "Electronics", label: "Electronics" },
  { id: "Sports", label: "Sports" },
  { id: "Fashion", label: "Fashion" },
  { id: "Books", label: "Books" },
  { id: "Home & Kitchen", label: "Home & Kitchen" },
  { id: "Grocery", label: "Grocery" },
  { id: "Beauty", label: "Beauty" },
  { id: "Toys", label: "Toys" },
  { id: "Automotive", label: "Automotive" },
  { id: "Services", label: "Services" },
  { id: "Other", label: "Other" },
];

const BANNERS = [
  {
    id: 1,
    title: "The Ultimate Future Collection",
    subtitle: "Season 2024",
    description: "Experience the next generation of premium tech and lifestyle products. Designed for those who dare to lead.",
    image: "/banner1.png",
    cta: "Explore Future",
    color: "from-blue-600 to-indigo-600"
  },
  {
    id: 2,
    title: "Elegance in Every Detail",
    subtitle: "Luxury Minimalist",
    description: "Discover a curated collection of minimalist essentials that redefine modern sophistication and timeless style.",
    image: "/banner2.png",
    cta: "View Collection",
    color: "from-purple-600 to-fuchsia-600"
  },
  {
    id: 3,
    title: "Active Life Redefined",
    subtitle: "High Performance",
    description: "Gear up with our high-performance athletic collection. Engineered for maximum comfort and peak athletic ability.",
    image: "/banner3.png",
    cta: "Get Started",
    color: "from-orange-500 to-red-600"
  }
];

const Home = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const urlSearchQuery = searchParams.get("search") || "";

  const [activeCategory, setActiveCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState(urlSearchQuery);
  const [currentBanner, setCurrentBanner] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 8;
  const categoryRefs = useRef({});

  // Update local search state when URL changes
  useEffect(() => {
    setSearchQuery(urlSearchQuery);
  }, [urlSearchQuery]);

  const allProducts = useSelector((state) => state.products.all || []);
  const isLoading = useSelector((state) => state.products.isLoading);
  const wishlist = useSelector((state) => state.wishlist);

  const productsByCategory = {
    All: allProducts,
    Electronics: useSelector((state) => state.products.electronics),
    Sports: useSelector((state) => state.products.sports),
    Fashion: useSelector((state) => state.products.fashion),
    Books: useSelector((state) => state.products.books),
    "Home & Kitchen": useSelector((state) => state.products.home_kitchen),
    Grocery: useSelector((state) => state.products.grocery),
    Beauty: useSelector((state) => state.products.beauty_personal_care),
    Toys: useSelector((state) => state.products.toys_games),
    Automotive: useSelector((state) => state.products.automotive),
    Services: useSelector((state) => state.products.services),
    Other: useSelector((state) => state.products.other),
  };

  useEffect(() => {
    dispatch(fetchProducts());
  }, [dispatch]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % BANNERS.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  const filteredProducts = (productsByCategory[activeCategory] || []).filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);
  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = filteredProducts.slice(indexOfFirstProduct, indexOfLastProduct);

  const handleWishlistClick = (item) => {
    const user = localStorage.getItem("accessToken");
    if (!user) {
      toast.error("Please login to manage your wishlist");
      navigate("/login");
      return;
    }
    if (isInWishlist(item.name)) {
      dispatch(RemoveFromWishlist(item));
      toast.success("Removed from wishlist");
    } else {
      dispatch(AddToWishlist(item));
      toast.success("Added to wishlist");
    }
  };

  const handleAddToCartClick = (item) => {
    const user = localStorage.getItem("accessToken");
    if (!user) {
      toast.error("Please login to add items to your cart");
      navigate("/login");
      return;
    }
    dispatch(AddToCart(item));
    toast.success("Added to cart");
  };

  const isInWishlist = (itemName) => {
    return wishlist.some((item) => item.name === itemName);
  };

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    document.getElementById("products-section")?.scrollIntoView({ behavior: "smooth" });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-violet-600 font-bold animate-pulse">Loading amazing products...</p>
        </div>
      </div>
    );
  }

  const banner = BANNERS[currentBanner];

  return (
    <div className="min-h-screen bg-white">
      {/* CATEGORIES SECTION (Placed between Navbar and Banner) */}
      <section id="categories-section" className="bg-white border-b border-gray-100 pt-[10px] pb-3 w-full sticky top-[10px] z-40">
        <div className="w-full px-6 md:px-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <h2 className="text-sm font-black text-gray-900 tracking-[0.2em] whitespace-nowrap">
              BROWSE <span className="text-violet-600">CATEGORIES</span>
            </h2>
            <div className="flex gap-0 overflow-x-auto pb-2 md:pb-0 w-full scrollbar-hide justify-start md:justify-end items-center">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => { setActiveCategory(cat.id); setCurrentPage(1); }}
                  className={`px-6 py-2 rounded-xl font-bold text-[10px] uppercase tracking-wider transition-all duration-300 ${activeCategory === cat.id ? "bg-violet-600 text-white shadow-lg scale-105" : "bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-900"}`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* HERO CAROUSEL (Without Arrows) */}
      <section className="relative w-full h-[400px] md:h-[550px] overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentBanner}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
            className="absolute inset-0"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent z-10" />
            <img src={banner.image} alt={banner.title} className="w-full h-full object-cover" />
            <div className="absolute inset-0 z-20 flex flex-col justify-center px-6 md:px-24 lg:px-32">
              <motion.div
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.8 }}
                className="max-w-3xl"
              >
                <motion.p
                  className="text-violet-400 font-black tracking-[0.3em] uppercase text-xs mb-4"
                >
                  {banner.subtitle}
                </motion.p>
                <motion.h1
                  className="text-4xl md:text-6xl font-black text-white mb-6 leading-tight"
                >
                  {banner.title}
                </motion.h1>
                <motion.p
                  className="text-gray-300 text-base md:text-lg mb-8 max-w-xl leading-relaxed"
                >
                  {banner.description}
                </motion.p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => document.getElementById("products-section")?.scrollIntoView({ behavior: "smooth" })}
                  className={`group w-fit px-10 py-4 bg-gradient-to-r ${banner.color} text-white font-black rounded-2xl flex items-center gap-3 shadow-xl transition-all duration-300`}
                >
                  {banner.cta} <ArrowRight size={20} />
                </motion.button>
              </motion.div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Progress Indicators (Only indicators, no arrows) */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-30 flex gap-3 p-3 bg-black/20 backdrop-blur-xl rounded-full border border-white/10">
          {BANNERS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentBanner(idx)}
              className={`h-1.5 rounded-full transition-all duration-700 ${currentBanner === idx ? "w-10 bg-violet-500 shadow-[0_0_15px_rgba(139,92,246,0.5)]" : "w-1.5 bg-white/40 hover:bg-white/60"}`}
            />
          ))}
        </div>
      </section>

      {/* PRODUCT GRID SECTION */}
      <section id="products-section" className="max-w-[1600px] mx-auto px-6 md:px-12 py-16">
        <div className="flex items-end justify-between mb-12">
          <div className="space-y-2">
            <p className="text-violet-600 font-black tracking-widest text-xs uppercase">Curated Just for You</p>
            <h3 className="text-3xl font-black text-gray-900 tracking-tight">FEATURED PRODUCTS</h3>
          </div>
          <p className="text-gray-400 text-xs font-bold hidden md:block uppercase tracking-widest">
            {filteredProducts.length} Items Available
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {currentProducts.map((item) => (
            <ProductCard
              key={item.id}
              item={item}
              navigate={navigate}
              handleWishlistClick={handleWishlistClick}
              handleAddToCartClick={handleAddToCartClick}
              isInWishlist={isInWishlist}
            />
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-24 bg-gray-50 rounded-[32px] border-2 border-dashed border-gray-200">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="text-gray-300" size={32} />
            </div>
            <h3 className="text-xl font-black text-gray-900 mb-2">No products found</h3>
            <p className="text-gray-500 text-sm">Try adjusting your filters or search terms</p>
          </div>
        )}

        {/* PAGINATION */}
        {totalPages > 1 && (
          <div className="flex justify-center mt-20 gap-3">
            {Array.from({ length: totalPages }).map((_, i) => (
              <button
                key={i}
                onClick={() => paginate(i + 1)}
                className={`w-12 h-12 rounded-xl font-black text-sm transition-all duration-500 ${currentPage === i + 1 ? "bg-black text-white shadow-xl scale-110" : "bg-white text-gray-400 border border-gray-100 hover:border-violet-200 hover:text-violet-600"}`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default Home;
