const express = require("express")
const router = express.Router()
const { predictValidation } = require("../validators/predict.validator");
const validate = require("../middlewares/validate");
const { predict } = require("../controllers/predictController")
const Transaction = require("../models/Transaction")
const ApiResponse = require("../utils/ApiResponse")
const ApiError = require("../utils/ApiError")
const asyncHandler = require("../utils/AsyncHandler")
const protect = require("../middlewares/authMiddleware")

// POST prediction
router.post("/predict", protect, predictValidation, validate, predict);

// NEW: Get all transactions
router.get(
  "/history", protect,
  asyncHandler(async (req, res) => {
    const data = await Transaction.find({ user: req.user.id }).sort({
      createdAt: -1,
    });

    return res.json(new ApiResponse(200, data, "History fetched successfully"));
  }),
);

module.exports = router