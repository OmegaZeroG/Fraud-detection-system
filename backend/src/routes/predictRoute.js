const express = require("express")
const router = express.Router()

const { predict } = require("../controllers/predictController")
const Transaction = require("../models/Transaction")

// POST prediction
//router.post("/predict", predict)

// 👉 NEW: Get all transactions
router.get("/history", async (req, res) => {
  try {
    const data = await Transaction.find().sort({ createdAt: -1 })
    res.json(data)
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch history" })
  }
})

module.exports = router