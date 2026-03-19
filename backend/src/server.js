const express = require("express");

const app = express();
const port = 8000;

app.use(express.json());

app.get("/", (req,res)=>{
    res.send("Fraud Detection API is Running");
});

app.listen(port,()=>{
    console.log(`Server is Running on port ${port}`)
})
