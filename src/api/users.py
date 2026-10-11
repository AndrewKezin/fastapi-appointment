from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# @router.get("/")


# @router.delete("/users/{user_id}")
# async def delete_user(user_id: int, admin: User = Depends(require_role(UserRole.ADMIN))):
#     ...


# @router.post("/register")

# @router.post("/login")