from fastapi import FastAPI
import uvicorn

from routes import (
    movie_router,
    admin_router,
    store_router,
    booking_router,
    user_router,
)

app = FastAPI(
    title="JamorCineplex API",
    description="API สำหรับระบบจองตั๋วโรงภาพยนต์และระบบสมาชิก",
    version="1.0.0",
)

app.include_router(movie_router)
app.include_router(admin_router)
app.include_router(store_router)
app.include_router(booking_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
