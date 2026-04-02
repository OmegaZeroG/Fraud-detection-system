const { body } = require("express-validator");

const predictValidation = [
  body("features")
    .isArray({ min: 1 })
    .withMessage("Features must be a non-empty array"),
];

module.exports = { predictValidation };
