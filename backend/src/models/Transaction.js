const mongoose = require("mongoose");

const transactionSchema = new mongoose.Schema(
  {
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    // ATO Login Features
    hour: { type: Number },
    new_device_flag: { type: Number },
    new_country_flag: { type: Number },
    new_payee_flag: { type: Number },
    failed_attempts_before_success: { type: Number },
    time_to_transfer_seconds: { type: Number },
    is_odd_hour: { type: Number },
    suspicious_sequence: { type: Number },
    country_encoded: { type: Number },

    // ML Results
    fraud_probability: { type: Number, required: true },
    risk_level: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH"],
      required: true,
    },
    is_fraud: { type: Boolean, required: true },
    shap_factors: { type: Array, default: [] },

    // Amount
    amount: { type: Number },
  },
  { timestamps: true },
);

module.exports = mongoose.model("Transaction", transactionSchema);
