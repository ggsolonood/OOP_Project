from fastapi import FastAPI
import uvicorn
from routes import api_router

app = FastAPI(title="JamorCineplex API", version="2.0.0")
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    print("🚀 Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)