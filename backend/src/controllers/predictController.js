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

  // Call ML service
  const result = await getPrediction(features);

  // Save full result to DB
  const saved = await Transaction.create({
    user: req.user.id,
    amount: features.amount_log || 0,

    // ATO features
    hour: features.hour,
    new_device_flag: features.new_device_flag,
    new_country_flag: features.new_country_flag,
    new_payee_flag: features.new_payee_flag,
    failed_attempts_before_success: features.failed_attempts_before_success,
    time_to_transfer_seconds: features.time_to_transfer_seconds,
    is_odd_hour: features.is_odd_hour,
    suspicious_sequence: features.suspicious_sequence,
    country_encoded: features.country_encoded,

    // ML results
    fraud_probability: result.fraud_probability,
    risk_level: result.risk_level,
    is_fraud: result.is_fraud,
    shap_factors: result.shap_factors,
  });

  return res.status(200).json(
    new ApiResponse(
      200,
      {
        transaction: saved,
        prediction: {
          fraud_probability: result.fraud_probability,
          iso_anomaly_score: result.iso_anomaly_score,
          risk_level: result.risk_level,
          is_fraud: result.is_fraud,
          shap_factors: result.shap_factors,
        },
      },
      "Prediction successful",
    ),
  );
});
