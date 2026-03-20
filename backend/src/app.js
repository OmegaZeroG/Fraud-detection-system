const express = require("express");
const app = express();

const predictRoutes = require("./routes/predictRoute");

app.use(express.json());
app.use(cors());
app.use("/api", predictRoutes);

module.exports = app;
