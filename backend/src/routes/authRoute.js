const express = require("express");
const router = express.Router();
const {
    registerValidation,
    loginValidation,
} = require("../validators/auth.validator");

const validate = require("../middlewares/validate");

const { register, login } = require("../controllers/authController");

router.post("/register", registerValidation, validate, register);
router.post("/login", loginValidation, validate, login);

module.exports = router;
