"""v1 API 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import auth, users, departments, positions, resumes, analysis

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(departments.router, prefix="/departments", tags=["部门"])
api_router.include_router(positions.router, prefix="/positions", tags=["岗位"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["简历"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["AI 分析"])