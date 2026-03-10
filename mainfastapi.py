import uvicorn
from fastapi import FastAPI

from routes import admin_router, store_router, booking_router, user_router

# ==========================================
# FastAPI App
# ==========================================

app = FastAPI(
    title="JamorCineplex API",
    description="API สำหรับระบบจัดการโรงภาพยนตร์และระบบการจองที่นั่ง",
    version="1.0.0",
)

# ==========================================
# Register Routers
# ==========================================

app.include_router(admin_router)
app.include_router(store_router)
app.include_router(booking_router)
app.include_router(user_router)

# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
