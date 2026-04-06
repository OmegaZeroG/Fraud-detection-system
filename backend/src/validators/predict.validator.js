const { body } = require("express-validator");

const predictValidation = [
  body("features").isObject().withMessage("Features must be an object"),

  body("features.hour").isNumeric().withMessage("hour must be a number"),
  body("features.amount_log")
    .isNumeric()
    .withMessage("amount_log must be a number"),
  body("features.new_device_flag")
    .isNumeric()
    .withMessage("new_device_flag must be a number"),
  body("features.failed_attempts_before_success")
    .isNumeric()
    .withMessage("failed_attempts_before_success must be a number"),
];

module.exports = { predictValidation };
