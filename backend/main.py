"""
FastAPI主应用
前后端分离架构 - 提供API服务和静态文件服务
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from core.config import settings, validate_settings
from core.logging_config import setup_logging, get_logger
from core.database import Base, engine
from api import api_router

# 初始化日志系统
logger = setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    max_bytes=settings.log_max_bytes,
    backup_count=settings.log_backup_count
)

# 验证配置
config_errors = validate_settings()
if config_errors:
    for error in config_errors:
        logger.warning(error)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MQTT IoT管理系统 - RESTful API",
    debug=settings.debug
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body if settings.debug else None
        }
    )

# 注册API路由
app.include_router(api_router, prefix=settings.api_prefix)

# 静态文件服务（用于部署版本）
static_dir = Path(__file__).parent / "static"
if static_dir.exists() and static_dir.is_dir():
    # 如果有静态文件目录，挂载静态文件
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # 提供前端页面
    @app.get("/")
    async def serve_index():
        """提供前端首页"""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {
            "message": "MQTT IoT管理系统 API",
            "version": settings.app_version,
            "docs": "/docs",
            "api_prefix": settings.api_prefix
        }
    
    # 处理前端路由（SPA应用）
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """处理前端路由，所有非API路径返回index.html"""
        # 排除API路径和静态文件路径
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        
        # 如果是静态资源，尝试返回
        static_file = static_dir / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # 其他路径返回index.html（SPA路由）
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        return JSONResponse(status_code=404, content={"detail": "Not found"})
else:
    # 如果没有静态文件目录，使用API根路径
    @app.get("/")
    async def root():
        """API根路径"""
        return {
            "message": "MQTT IoT管理系统 API",
            "version": settings.app_version,
            "docs": "/docs",
            "api_prefix": settings.api_prefix
        }

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.app_version}

# 启动时启动MQTT服务
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"启动应用: {settings.app_name} v{settings.app_version}")
    logger.info(f"API前缀: {settings.api_prefix}")
    
    try:
        from services.mqtt_service import start_mqtt_service
        if start_mqtt_service():
            logger.info("MQTT服务启动成功")
        else:
            logger.warning("MQTT服务启动失败（可能没有激活的配置）")
    except Exception as e:
        logger.error(f"启动MQTT服务失败: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("正在关闭应用...")
    try:
        from services.mqtt_service import stop_mqtt_service
        stop_mqtt_service()
        logger.info("MQTT服务已停止")
    except Exception as e:
        logger.error(f"停止MQTT服务失败: {e}", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"监听地址: {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )