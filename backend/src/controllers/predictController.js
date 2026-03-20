const { getPrediction } = require("../services/mlService");

exports.predict = async (req, res) => {
  try {
    const { features } = req.body;

    const result = await getPrediction(features);

    res.json(result);
  } catch (error) {
    console.error("ERROR:", error.message); // 👈 ADD THIS
    res.status(500).json({ error: "Prediction failed" });
  }
};
