from fastapi import APIRouter

from gamenet.server.api import auth, credit, customer_auth, customers, devices, games, health, packages, pricing, sales, sessions, vip, websocket

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(credit.router)
api_router.include_router(sessions.router)
api_router.include_router(sales.router)
api_router.include_router(pricing.router)
api_router.include_router(devices.router)
api_router.include_router(customer_auth.router)
api_router.include_router(packages.router)
api_router.include_router(vip.router)
api_router.include_router(websocket.router)
api_router.include_router(games.router)
