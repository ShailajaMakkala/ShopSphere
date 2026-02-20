import { useEffect, useState } from "react";
import { getVendorProducts, deleteVendorProduct, updateVendorProduct } from "../../api/vendor_axios";
import toast from "react-hot-toast";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedProduct, setEditedProduct] = useState({});
  const [previews, setPreviews] = useState([]);
  const [sliderIndex, setSliderIndex] = useState({});
  const [viewIndex, setViewIndex] = useState(null); // New state for view modal
  const [viewSliderIndex, setViewSliderIndex] = useState(0); // Image slider in view
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await getVendorProducts();
      setProducts(data);

      const initialIndex = {};
      data.forEach((_, i) => initialIndex[i] = 0);
      setSliderIndex(initialIndex);
    } catch (error) {
      console.error("Error loading products:", error);
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (index) => {
    if (!window.confirm("Delete this product?")) return;
    try {
      const productToDelete = products[index];
      await deleteVendorProduct(productToDelete.id);

      const updated = [...products];
      updated.splice(index, 1);
      setProducts(updated);
      toast.success("Product deleted successfully");
    } catch (error) {
      console.error("Error deleting product:", error);
      toast.error("Failed to delete product");
    }
  };

  const startEdit = (index) => {
    const product = products[index];
    const knownCategories = [
      "electronics",
      "fashion",
      "home_kitchen",
      "grocery",
      "beauty_personal_care",
      "sports_fitness",
      "toys_games",
      "automotive",
      "books",
      "services",
    ];

    const isCustom =
      product.category &&
      !knownCategories.includes(product.category.toLowerCase());

    setEditingIndex(index);
    setEditedProduct({
      ...product,
      stock: product.quantity,
      category: isCustom ? "other" : product.category.toLowerCase(),
      images: [],
    });

    if (isCustom) {
      setCustomCategory(product.category);
    } else {
      setCustomCategory("");
    }

    setPreviews(
      product.images?.map((img) =>
        img.image.startsWith("http") ? img.image : `${API_BASE_URL}${img.image}`
      ) || []
    );
  };

  const [customCategory, setCustomCategory] = useState("");

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditedProduct({ ...editedProduct, [name]: value });

    if (name === "category" && value !== "other") {
      setCustomCategory("");
    }
  };

  const handleImages = (e) => {
    const files = Array.from(e.target.files);
    Promise.all(
      files.map(
        (file) =>
          new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.readAsDataURL(file);
          })
      )
    ).then((newImages) => {
      setEditedProduct((prev) => ({
        ...prev,
        images: [...(prev.images || []), ...files], // Store File objects
      }));
      setPreviews((prev) => [...prev, ...newImages]);
    });
  };

  const removeImage = (index) => {
    setEditedProduct(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const saveEdit = async () => {
    if (
      !editedProduct.name ||
      !editedProduct.price ||
      !editedProduct.description ||
      !editedProduct.stock ||
      !editedProduct.category
    ) {
      toast.error("Please fill all required fields");
      return;
    }

    // If new images are provided, check minimum 4 requirement
    // If not provided, backend preserves old ones
    if (editedProduct.images.length > 0 && editedProduct.images.length < 4) {
      toast.error("Minimum 4 product images are required if updating photos.");
      return;
    }

    try {
      setLoading(true);
      const productToUpdate = {
        ...editedProduct,
        category:
          editedProduct.category === "other"
            ? customCategory.trim()
            : editedProduct.category,
        quantity: editedProduct.stock, // Ensure backend gets 'quantity'
      };

      await updateVendorProduct(editedProduct.id, productToUpdate);

      toast.success("Product updated successfully");
      await loadProducts(); // Refresh list from backend
      setEditingIndex(null);
    } catch (error) {
      console.error("Error saving product:", error);
      const errorMessage =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        "Failed to update product";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const nextSlide = (i) => {
    setSliderIndex(prev => ({
      ...prev,
      [i]: (prev[i] + 1) % (products[i].images?.length || 1)
    }));
  };

  const prevSlide = (i) => {
    setSliderIndex(prev => ({
      ...prev,
      [i]: (prev[i] - 1 + (products[i].images?.length || 1)) % (products[i].images?.length || 1)
    }));
  };

  const nextViewSlide = () => {
    if (!products[viewIndex]?.images) return;
    setViewSliderIndex((viewSliderIndex + 1) % products[viewIndex].images.length);
  };

  const prevViewSlide = () => {
    if (!products[viewIndex]?.images) return;
    setViewSliderIndex((viewSliderIndex - 1 + products[viewIndex].images.length) % products[viewIndex].images.length);
  };

  return (
    <div className="max-w-7xl mx-auto p-8 relative">

      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold">Product Management</h2>
        <span className="bg-gray-100 px-4 py-2 rounded-xl">
          Total: {products.length}
        </span>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <div className="w-12 h-12 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-500 font-medium">Loading your products...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[400px] border-4 border-dashed border-gray-100 rounded-[40px] bg-gray-50/50">
          <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mb-6">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No products added yet</h3>
          <p className="text-gray-500 mb-8 max-w-sm text-center">Ready to start selling? Add your first product and it will appear here.</p>
          <button
            onClick={() => window.location.href = '/vendoraddproduct'}
            className="px-8 py-3 bg-black text-white rounded-2xl font-bold hover:bg-gray-800 transition-all hover:scale-105 active:scale-95"
          >
            Add First Product
          </button>
        </div>
      ) : (
        /* PRODUCT GRID */
        <div className="grid md:grid-cols-3 gap-8">
          {products.map((p, i) => (
            <div key={i} className="bg-white rounded-2xl shadow p-5 relative">

              {/* IMAGE SLIDER */}
              <div className="relative mb-3">
                {p.images?.length > 0 ? (
                  <>
                    <img
                      src={p.images[sliderIndex[i]]?.image?.startsWith('http')
                        ? p.images[sliderIndex[i]].image
                        : `${API_BASE_URL}${p.images[sliderIndex[i]]?.image}`}
                      className="h-44 w-full object-cover rounded-xl"
                      onError={(e) => {
                        e.target.src = "https://images.unsplash.com/photo-1523275335684-37898b6baf30";
                      }}
                    />
                    {p.images.length > 1 && (
                      <>
                        <button
                          onClick={() => prevSlide(i)}
                          className="absolute top-1/2 left-2 bg-white/80 backdrop-blur-sm p-1.5 rounded-full text-gray-800 shadow-md hover:bg-white transition-all transform -translate-y-1/2"
                        >
                          ‹
                        </button>
                        <button
                          onClick={() => nextSlide(i)}
                          className="absolute top-1/2 right-2 bg-white/80 backdrop-blur-sm p-1.5 rounded-full text-gray-800 shadow-md hover:bg-white transition-all transform -translate-y-1/2"
                        >
                          ›
                        </button>
                      </>
                    )}
                  </>
                ) : (
                  <div className="h-44 w-full bg-gray-100 rounded-xl flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                    <span className="text-xs font-bold uppercase tracking-widest">No Photos</span>
                  </div>
                )}
              </div>

              <h3 className="font-bold text-lg">{p.name}</h3>
              <p className="text-emerald-600 font-semibold mt-1">₹ {p.price}</p>
              <p className="text-sm text-gray-500">{p.category}</p>

              <div className="flex gap-4 mt-4">
                <button
                  onClick={() => startEdit(i)}
                  className="flex-1 border rounded-lg py-2 hover:bg-gray-100"
                >
                  Edit
                </button>
                <button
                  onClick={() => {
                    setViewIndex(i);
                    setViewSliderIndex(0);
                  }}
                  className="flex-1 border rounded-lg py-2 hover:bg-gray-100"
                >
                  View
                </button>
                <button
                  onClick={() => deleteProduct(i)}
                  className="flex-1 bg-red-500 text-white rounded-lg py-2 hover:bg-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* EDIT OVERLAY */}
      {editingIndex !== null && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-[32px] p-8 w-full max-w-2xl relative shadow-2xl animate-in fade-in zoom-in duration-300 mx-auto">

            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-black text-gray-900 flex items-center gap-3">
                <span className="p-2.5 bg-orange-100 rounded-2xl">
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </span>
                Edit Product
              </h2>
              <button
                onClick={() => setEditingIndex(null)}
                className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-900 transition-all"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            <div className="space-y-5 max-h-[65vh] overflow-y-auto pr-2 custom-scrollbar">
              <div>
                <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Product Name</label>
                <input
                  name="name"
                  value={editedProduct.name}
                  onChange={handleEditChange}
                  className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-medium text-gray-900"
                  placeholder="Enter product name"
                />
              </div>

              <div>
                <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Description</label>
                <textarea
                  name="description"
                  value={editedProduct.description}
                  onChange={handleEditChange}
                  className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-medium text-gray-900 resize-none"
                  rows={4}
                  placeholder="Tell us about your product..."
                />
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Price (₹)</label>
                  <div className="relative">
                    <span className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 font-bold">₹</span>
                    <input
                      name="price"
                      type="number"
                      value={editedProduct.price}
                      onChange={handleEditChange}
                      className="w-full bg-gray-50 border border-gray-100 rounded-2xl pl-10 pr-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-bold text-gray-900"
                      placeholder="0.00"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Stock</label>
                  <input
                    name="stock"
                    type="number"
                    value={editedProduct.stock}
                    onChange={handleEditChange}
                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-bold text-gray-900"
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Category</label>
                  <select
                    name="category"
                    value={editedProduct.category}
                    onChange={handleEditChange}
                    className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-bold text-gray-900 appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%20fill%3D%22none%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cpath%20d%3D%22M5%207.5L10%2012.5L15%207.5%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%221.67%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22/%3E%3C/svg%3E')] bg-[length:20px_20px] bg-[right_1.25rem_center] bg-no-repeat"
                  >
                    <option value="">Select Category</option>
                    <option value="electronics">Electronics</option>
                    <option value="fashion">Fashion</option>
                    <option value="home_kitchen">Home & Kitchen</option>
                    <option value="grocery">Groceries</option>
                    <option value="beauty_personal_care">Beauty & Personal Care</option>
                    <option value="sports_fitness">Sports & Fitness</option>
                    <option value="toys_games">Toys & Games</option>
                    <option value="automotive">Automotive</option>
                    <option value="books">Books</option>
                    <option value="services">Services</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                {editedProduct.category === "other" && (
                  <div>
                    <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Custom Category</label>
                    <input
                      name="customCategory"
                      value={customCategory}
                      onChange={(e) => setCustomCategory(e.target.value)}
                      placeholder="Enter category name"
                      className="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 outline-none transition-all font-medium text-gray-900"
                    />
                  </div>
                )}
              </div>

              <div>
                <label className="text-[11px] font-black text-gray-400 uppercase tracking-widest mb-1.5 block">Product Photos (Min 4)</label>
                <div className="relative group/upload">
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImages}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className="w-full bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl py-4 px-5 text-center group-hover/upload:border-orange-500/50 group-hover/upload:bg-orange-50/30 transition-all">
                    <span className="text-sm font-bold text-gray-500 group-hover/upload:text-orange-600">Click to upload new images</span>
                  </div>
                </div>
              </div>

              {/* IMAGE PREVIEWS */}
              <div className="flex gap-3 flex-wrap p-4 bg-gray-50/50 rounded-2xl border border-gray-100 shadow-inner">
                {previews.map((img, idx) => (
                  <div key={idx} className="relative group/img">
                    <img src={img} className="w-20 h-20 object-cover rounded-xl shadow-sm border border-white" />
                    <button
                      onClick={() => removeImage(idx)}
                      className="absolute -top-2 -right-2 bg-white text-red-500 rounded-full w-6 h-6 flex items-center justify-center text-sm shadow-xl opacity-0 group-hover/img:opacity-100 transition-all hover:scale-110"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-4 mt-8 pt-6 border-t border-gray-100">
              <button
                onClick={saveEdit}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white py-4 rounded-2xl font-black text-sm uppercase tracking-widest shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 transition-all hover:-translate-y-1 active:scale-95 disabled:opacity-50 disabled:translate-y-0"
              >
                {loading ? "Saving..." : "Save Changes"}
              </button>
              <button
                onClick={() => setEditingIndex(null)}
                className="flex-1 bg-gray-50 text-gray-500 py-4 rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-gray-100 transition-all active:scale-95"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW OVERLAY */}
      {viewIndex !== null && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center p-4 z-50 overflow-y-auto"
          onClick={() => setViewIndex(null)}
        >
          <div
            className="bg-white rounded-[32px] p-8 w-full max-w-3xl relative shadow-2xl animate-in fade-in zoom-in duration-300 pointer-events-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <span className="p-2 bg-violet-100 rounded-lg">
                  <svg className="w-6 h-6 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                </span>
                Product Details
              </h2>
              <button
                onClick={() => setViewIndex(null)}
                className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            <div className="max-h-[75vh] overflow-y-auto pr-2 custom-scrollbar">
              {/* IMAGE SLIDER */}
              <div className="relative mb-8 group">
                {products[viewIndex]?.images?.length > 0 ? (
                  <div className="bg-gray-50 rounded-2xl overflow-hidden border border-gray-100 shadow-inner">
                    <img
                      src={products[viewIndex].images[viewSliderIndex]?.image?.startsWith('http')
                        ? products[viewIndex].images[viewSliderIndex].image
                        : `${API_BASE_URL}${products[viewIndex].images[viewSliderIndex]?.image}`}
                      className="h-[400px] w-full object-contain mx-auto"
                      onError={(e) => {
                        e.target.src = "https://images.unsplash.com/photo-1523275335684-37898b6baf30";
                      }}
                    />
                    {products[viewIndex].images.length > 1 && (
                      <>
                        <button
                          onClick={prevViewSlide}
                          className="absolute top-1/2 left-4 bg-white/90 backdrop-blur-md p-2.5 rounded-full text-gray-800 shadow-xl hover:bg-white transition-all transform -translate-y-1/2 opacity-0 group-hover:opacity-100"
                        >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" /></svg>
                        </button>
                        <button
                          onClick={nextViewSlide}
                          className="absolute top-1/2 right-4 bg-white/90 backdrop-blur-md p-2.5 rounded-full text-gray-800 shadow-xl hover:bg-white transition-all transform -translate-y-1/2 opacity-0 group-hover:opacity-100"
                        >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" /></svg>
                        </button>
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5">
                          {products[viewIndex].images.map((_, dotIdx) => (
                            <div
                              key={dotIdx}
                              className={`w-2 h-2 rounded-full transition-all ${dotIdx === viewSliderIndex ? 'bg-violet-600 w-4' : 'bg-gray-300'}`}
                            />
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="h-64 w-full bg-gray-100 rounded-2xl flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                    <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    <span className="font-bold text-sm uppercase tracking-widest">No Photos Found</span>
                  </div>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Product Name</label>
                    <p className="text-xl font-bold text-gray-900 leading-tight">{products[viewIndex]?.name}</p>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Description</label>
                    <p className="text-gray-600 leading-relaxed text-sm">{products[viewIndex]?.description || "No description provided."}</p>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                  <div className="flex justify-between items-center border-b border-gray-200 pb-3">
                    <span className="text-gray-500 font-medium">Price</span>
                    <span className="text-xl font-bold text-emerald-600">₹ {products[viewIndex]?.price}</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-gray-200 pb-3">
                    <span className="text-gray-500 font-medium">Availability</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${products[viewIndex]?.quantity > 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                      {products[viewIndex]?.quantity > 0 ? `${products[viewIndex]?.quantity} In Stock` : 'Out of Stock'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 font-medium">Category</span>
                    <span className="px-3 py-1 bg-violet-100 text-violet-700 rounded-full text-xs font-bold capitalize">
                      {products[viewIndex]?.category?.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
