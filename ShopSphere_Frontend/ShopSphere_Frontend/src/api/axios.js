// import axios from "axios";

// const API_BASE_URL =
//   import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// // LOGIN

// export const loginUser = async (loginData) => {
//   const response = await axios.post(
//     `${API_BASE_URL}/user_login`,
//     loginData
//   );
//   console.log(response.data);

//   // Save tokens immediately after login
//   if (response.data?.access) {
//     localStorage.setItem("accessToken", response.data.access);
//     localStorage.setItem("refreshToken", response.data.refresh);
//   }

//   return response.data;
// };

// // SIGNUP
// export const signupUser = async (signupData) => {
//   const response = await axios.post(
//     `${API_BASE_URL}/register`,
//     signupData
//   );
//   return response.data;
// };


// // LOGOUT
// export const logout = () => {
//   localStorage.removeItem("accessToken");
//   localStorage.removeItem("refreshToken");
// };

// // GET MY ORDERS (Protected)

// export const getMyOrders = async () => {
//   const token = localStorage.getItem("accessToken");

//   if (!token) {
//     throw new Error("No access token found");
//   }

//   const response = await axios.get(
//     `${API_BASE_URL}/my_orders`,
//     {
//       headers: {
//         Authorization: `Bearer ${token}`,
//         "Content-Type": "application/json",
//       },
//     }
//   );

//   return response.data;
// };

// // PROCESS PAYMENT (Protected)
// export const processPayment = async (paymentData) => {
//   const token = localStorage.getItem("accessToken");

//   if (!token) {
//     throw new Error("No access token found. Please login first.");
//   }

//   const response = await axios.post(
//     `${API_BASE_URL}/process_payment`,
//     paymentData,
//     {
//       headers: {
//         Authorization: `Bearer ${token}`,
//         "Content-Type": "application/json",
//       },
//     }
//   );

//   return response.data;
// };

// // ADDRESS MANAGEMENT (Protected)

// export const getAddresses = async () => {
//   const token = localStorage.getItem("accessToken");
//   if (!token) throw new Error("No access token found");

//   const response = await axios.get(`${API_BASE_URL}/address`, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });
//   return response.data;
// };

// export const addAddress = async (addressData) => {
//   const token = localStorage.getItem("accessToken");
//   if (!token) throw new Error("No access token found");

//   const response = await axios.post(`${API_BASE_URL}/address`, addressData, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//       "Content-Type": "application/json",
//     },
//   });
//   return response.data;
// };

// export const deleteAddress = async (id) => {
//   const token = localStorage.getItem("accessToken");
//   if (!token) throw new Error("No access token found");

//   const response = await axios.post(`${API_BASE_URL}/delete-address/${id}`, {}, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });
//   return response.data;
// };

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// LOGIN

export const loginUser = async (loginData) => {
  const response = await axios.post(
    `${API_BASE_URL}/user_login`,
    loginData
  );
  console.log(response.data);

  // Save tokens immediately after login
  if (response.data?.access) {
    localStorage.setItem("accessToken", response.data.access);
    localStorage.setItem("refreshToken", response.data.refresh);
  }

  return response.data;
};

// GOOGLE LOGIN
export const googleLogin = async (googleData) => {
  const response = await axios.post(
    `${API_BASE_URL}/google_login`,
    googleData
  );

  if (response.data?.access) {
    localStorage.setItem("accessToken", response.data.access);
    localStorage.setItem("refreshToken", response.data.refresh);
  }

  return response.data;
};

// SIGNUP
export const signupUser = async (signupData) => {
  const response = await axios.post(
    `${API_BASE_URL}/register`,
    signupData
  );
  return response.data;
};
// FORGOT PASSWORD (Public)
export const forgotPassword = async (email) => {
  const response = await axios.post(
    `${API_BASE_URL}/auth/?page=forgot`,
    { email },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};

// RESET PASSWORD (Public)
export const resetPassword = async (token, password1, password2) => {
  const response = await axios.post(
    `${API_BASE_URL}/auth/?page=reset&token=${token}`,
    { password1, password2 },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};

// PRODUCTS (Public)
export const getProducts = async () => {
  const response = await axios.get(`${API_BASE_URL}/products`);
  return response.data;
};

// LOGOUT
export const logout = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
};

// GET MY ORDERS (Protected)

export const getMyOrders = async () => {
  const token = localStorage.getItem("accessToken");

  if (!token) {
    throw new Error("No access token found");
  }

  const response = await axios.get(
    `${API_BASE_URL}/my_orders`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};

// PROCESS PAYMENT (Protected)
export const processPayment = async (paymentData) => {
  const token = localStorage.getItem("accessToken");

  if (!token) {
    throw new Error("No access token found. Please login first.");
  }

  const response = await axios.post(
    `${API_BASE_URL}/process_payment`,
    paymentData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};

// ADDRESS MANAGEMENT (Protected)

export const getAddresses = async () => {
  const token = localStorage.getItem("accessToken");
  if (!token) throw new Error("No access token found");

  const response = await axios.get(`${API_BASE_URL}/address`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const addAddress = async (addressData) => {
  const token = localStorage.getItem("accessToken");
  if (!token) throw new Error("No access token found");

  const response = await axios.post(`${API_BASE_URL}/address`, addressData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const deleteAddress = async (id) => {
  const token = localStorage.getItem("accessToken");
  if (!token) throw new Error("No access token found");

  const response = await axios.post(`${API_BASE_URL}/delete-address/${id}`, {}, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const updateAddress = async (id, addressData) => {
  const token = localStorage.getItem("accessToken");
  if (!token) throw new Error("No access token found");

  const response = await axios.put(`${API_BASE_URL}/update-address/${id}`, addressData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const getProductDetail = async (productId) => {
  const token = localStorage.getItem("accessToken");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await axios.get(`${API_BASE_URL}/product/${productId}`, {
    headers,
    params: { format: 'json' }
  });
  return response.data;
};

export const submitReview = async (productId, reviewData) => {
  const token = localStorage.getItem("accessToken");
  if (!token) throw new Error("Please login to submit a review");

  const response = await axios.post(`${API_BASE_URL}/submit_review/${productId}`, reviewData, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
