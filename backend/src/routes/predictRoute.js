const router = require("express").Router();
const { predict } = require("../controllers/predictController");

router.post("/predict", predict);

module.exports = router;
