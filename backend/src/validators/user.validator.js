const { body } = require("express-validator");

const updateProfileValidation = [
  body("name").notEmpty().withMessage("Name required"),
  body("email").isEmail().withMessage("Valid email required"),
];

const changePasswordValidation = [
  body("oldPassword").notEmpty().withMessage("Old password required"),
  body("newPassword")
    .isLength({ min: 6 })
    .withMessage("New password must be at least 6 characters"),
];

module.exports = {
  updateProfileValidation,
  changePasswordValidation,
};
