
cd ml-service
./venv/Scripts/Activate
python -m uvicorn app.main:app --reload


cd backend
npm run dev