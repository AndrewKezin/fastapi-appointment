from fastapi import Depends, HTTPException, status

from src.models.users import UserRole

def require_role(*roles: UserRole):
    # def checker(user: User = Depends(get_current_user)) -> User:
    #     if user.role not in roles:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Недостаточно прав"
    #         )
    #     return user
    # return checker
    pass