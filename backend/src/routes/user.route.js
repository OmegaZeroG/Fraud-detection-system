const express = require("express");
const router = express.Router();

const protect = require("../middlewares/authMiddleware");
const {
  updateProfileValidation,
  changePasswordValidation,
} = require("../validators/user.validator");

const validate = require("../middlewares/validate");
const {
  getProfile,
  updateProfile,
  changePassword,
} = require("../controllers/user.controller");

router.get("/profile", protect, getProfile);

router.put(
  "/profile",
  protect,
  updateProfileValidation,
  validate,
  updateProfile,
);

router.put(
  "/change-password",
  protect,
  changePasswordValidation,
  validate,
  changePassword,
);

module.exports = router;
