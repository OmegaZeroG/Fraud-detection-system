const axios = require("axios");
const ApiError = require("../utils/ApiError");

const ML_API_URL = "http://127.0.0.1:8000/predict";

const getPrediction = async (features) => {
  try {
    const response = await axios.post(ML_API_URL, {
      features,
    });

    return response.data;
  } catch (error) {
    console.error("ML API Error:", error.message);

    // 🔥 Throw structured error
    throw new ApiError(500, "ML service is unavailable or failed to respond");
  }
};

module.exports = { getPrediction };
