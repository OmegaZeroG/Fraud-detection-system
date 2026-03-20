const express = require("express");
const cors = require("cors");

const app = express();
const   port = process.env.PORT || 5000;

app.use(cors()); 
app.use(express.json());

app.use("/api", require("./routes/predictRoute"));
app.listen(port, () => {
    console.log(`Server running on port http://localhost:${port}`);
});


module.exports = app;
