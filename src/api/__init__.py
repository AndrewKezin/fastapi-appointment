from fastapi import APIRouter

from src.api.cars import router as car_router
from src.api.users import router as user_router
from src.api.appointments import router as appointment_router

main_router = APIRouter()

main_router.include_router(car_router)
main_router.include_router(user_router)
main_router.include_router(appointment_router)

