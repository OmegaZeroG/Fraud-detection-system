const express = require("express");
const router = express.Router();
const mongoose = require("mongoose");
const axios = require("axios");

router.get("/health", async (req, res) => {
    const health = {
    status: "ok",
    timestamp: new Date().toISOString(),
    services: {
        server: "up",
        mongodb: "unknown",
        ml_service: "unknown",
        },
    };

    // Check MongoDB connection
    try {
        const dbState = mongoose.connection.readyState;
        // 0 = disconnected, 1 = connected, 2 = connecting, 3 = disconnecting
        const stateMap = {
            0: "disconnected",
            1: "connected",
            2: "connecting",
            3: "disconnecting",
        };
        health.services.mongodb = stateMap[dbState] || "unknown";
    } catch (err) {
        health.services.mongodb = "error";
        health.status = "degraded";
    }

    // Check ML service (adjust URL to your ML service)
    try {
        const mlResponse = await axios.get(`${process.env.ML_SERVER_URL}/health`, {
        timeout: 3000,
        });
        health.services.ml_service = mlResponse.status === 200 ? "up" : "down";
    } catch (err) {
        health.services.ml_service = "down";
        health.services.ml_service_error = err.message;
        health.status = "degraded";
    }

    // If any critical service is down, mark overall status
    if (health.services.mongodb !== "connected") {
        health.status = "degraded";
    }

    const httpStatus = health.status === "ok" ? 200 : 207;
    res.status(httpStatus).json(health);
});

module.exports = router;
