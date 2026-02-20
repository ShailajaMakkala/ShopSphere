import axios from "axios";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";



// vendor register
export const vendorRegister = async (signupData) => {
    const token = localStorage.getItem("accessToken");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    console.log(signupData);
    const response = await axios.post(
        `${API_BASE_URL}/vendor/register/`,
        signupData,
        { headers }
    );
    return response.data;
};

// Get vendor approval status
export const getVendorStatus = async () => {
    const token = localStorage.getItem("accessToken");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await axios.get(
        `${API_BASE_URL}/api/vendor/approval-status/`,
        { headers }
    );
    return response.data;
};

// LOGOUT
export const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
};


export const add_Product = async (productData) => {
    const token = localStorage.getItem("accessToken");
    const headers = {
        "Content-Type": "multipart/form-data",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const formData = new FormData();
    Object.keys(productData).forEach((key) => {
        if (key === "images") {
            productData.images.forEach((image) => {
                formData.append("images", image);
            });
        } else if (key === "stock") {
            // Map 'stock' from frontend to 'quantity' for backend
            formData.append("quantity", productData[key]);
        } else {
            formData.append(key, productData[key]);
        }
    });

    const response = await axios.post(
        `${API_BASE_URL}/api/vendor/products/`,
        formData,
        { headers }
    );

    return response.data;
};

// Get vendor products
export const getVendorProducts = async () => {
    const token = localStorage.getItem("accessToken");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await axios.get(
        `${API_BASE_URL}/api/vendor/products/`,
        { headers }
    );
    return response.data;
};

// Delete vendor product
export const deleteVendorProduct = async (productId) => {
    const token = localStorage.getItem("accessToken");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await axios.delete(
        `${API_BASE_URL}/api/vendor/products/${productId}/`,
        { headers }
    );
    return response.data;
};
// Update vendor product
export const updateVendorProduct = async (productId, productData) => {
    const token = localStorage.getItem("accessToken");
    const headers = {
        "Content-Type": "multipart/form-data",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const formData = new FormData();
    Object.keys(productData).forEach((key) => {
        if (key === "images") {
            // Only append new images if any are provided
            if (Array.isArray(productData.images)) {
                productData.images.forEach((image) => {
                    if (image instanceof File) {
                        formData.append("images", image);
                    }
                });
            }
        } else if (key === "quantity" || key === "stock") {
            formData.append("quantity", productData[key]);
        } else {
            formData.append(key, productData[key]);
        }
    });

    const response = await axios.put(
        `${API_BASE_URL}/api/vendor/products/${productId}/`,
        formData,
        { headers }
    );
    return response.data;
};
