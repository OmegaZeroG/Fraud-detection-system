const asyncHandler = require("../utils/AsyncHandler");
const ApiError = require("../utils/ApiError");
const ApiResponse = require("../utils/ApiResponse");

const { getPrediction } = require("../services/mlService");
const Transaction = require("../models/Transaction");

exports.predict = asyncHandler(async (req, res) => {
  const { features } = req.body;

  if (!features) {
    throw new ApiError(400, "Features are required");
  }

  // 🔥 Call ML service
  const result = await getPrediction(features);

  // 🔥 Save to DB
  const saved = await Transaction.create({
    amount: features[0],
    prediction: result.prediction,
  });

  return res
    .status(200)
    .json(new ApiResponse(200, saved, "Prediction successful"));
});
