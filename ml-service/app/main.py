from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


# ✅ Define proper request schema
class Transaction(BaseModel):
    features: List[float]

@app.get("/health")
def health():
    return {"status": "ok", "service": "ml-service"}


def dummy_model(data):
    if data[-1] > 1000:
        return 1
    return 0


@app.get("/")
def home():
    return {"message": "Fraud Detection API Running"}


@app.post("/predict")
def predict(transaction: Transaction):
    
    features = transaction.features

    prediction = dummy_model(features)

    return {
        "prediction": int(prediction)
    }