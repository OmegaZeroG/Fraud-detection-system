const axios = require("axios");

const ML_API_URL = "http://127.0.0.1:8000/predict";

const getPrediction = async (features) => {
  try {
    const response = await axios.post(ML_API_URL, {
      features: features,
    });

    return response.data;
  } catch (error) {
    console.error("ML API Error:", error.message);
    throw error;
  }
};

module.exports = { getPrediction };
