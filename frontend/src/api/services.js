import API from "./axios";

// 🔮 Predict
export const predictAPI = (amount) => {
  return API.post("/predict", {
    features: [amount],
  });
};

// 📊 Get history
export const getHistoryAPI = () => {
  return API.get("/history");
};

// 🔐 Auth
export const loginAPI = (data) => {
  return API.post("/auth/login", data);
};

export const registerAPI = (data) => {
  return API.post("/auth/register", data);
};
