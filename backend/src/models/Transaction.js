const mongoose = require("mongoose");

const transactionSchema = new mongoose.Schema({
  amount: Number,
  prediction: Number,
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model("Transaction", transactionSchema);
