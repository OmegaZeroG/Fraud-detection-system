const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// ✅ Test route
app.get("/", (req, res) => {
    res.send("API Running 🚀");
});

// ✅ Routes
app.use("/api", require("./routes/predictRoute"));

const ApiError = require("./utils/ApiError");

//auth routes
app.use("/api/auth", require("./routes/authRoute"));


app.use((err, req, res, next) => {
    const statusCode = err.statusCode || 500;

    res.status(statusCode).json({
        success: false,
        message: err.message || "Internal Server Error",
    });
});


module.exports = app;
