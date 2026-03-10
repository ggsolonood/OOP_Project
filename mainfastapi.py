from fastapi import FastAPI
from routes import admin_router, store_router, booking_router, user_router, movie_router
import uvicorn

app = FastAPI(
    title="JamorCineplex API",
    description="API สำหรับระบบจัดการโรงภาพยนตร์และระบบการจองที่นั่ง",
    version="1.0.0",
)

app.include_router(movie_router)
app.include_router(admin_router)
app.include_router(store_router)
app.include_router(booking_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
