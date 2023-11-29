from fastapi import APIRouter

from app.routers.api_v1 import (
    auth,
    login,
    user,
    stadium,
    stadium_court,
    team_member,
    team,
    order
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stadium.router, prefix="/stadium", tags=["stadium"])
api_router.include_router(stadium_court.router, prefix="/stadium-court", tags=["stadium-court"])
api_router.include_router(team_member.router, prefix="/team-member", tags=["team-member"])
api_router.include_router(team.router, prefix="/team", tags=["team"])
api_router.include_router(order.router, prefix="/order", tags=["order"])
# api_router.mount("/google-auth", auth.auth_app)