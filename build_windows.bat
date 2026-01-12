@echo off
REM Windows 10 部署构建脚本
REM 用于生成 Windows 部署版本

echo ========================================
echo MQTT IoT 管理系统 - Windows 部署构建
echo ========================================
echo.

REM 检查 Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 构建前端生产版本...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)

call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 前端构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo [完成] 前端构建成功
echo.

echo [2/4] 准备后端文件...
if not exist "deploy\backend" mkdir deploy\backend
xcopy /E /I /Y backend\api deploy\backend\api
xcopy /E /I /Y backend\core deploy\backend\core
xcopy /E /I /Y backend\models deploy\backend\models
xcopy /E /I /Y backend\schemas deploy\backend\schemas
xcopy /E /I /Y backend\services deploy\backend\services
copy /Y backend\main.py deploy\backend\
copy /Y backend\requirements.txt deploy\backend\
copy /Y backend\env.example deploy\backend\env.example
echo [完成] 后端文件准备完成
echo.

echo [3/4] 复制前端构建文件...
if not exist "deploy\backend\static" mkdir deploy\backend\static
if not exist "frontend\dist" (
    echo [错误] 前端构建目录不存在，请先运行前端构建
    cd ..
    pause
    exit /b 1
)
xcopy /E /I /Y frontend\dist\* deploy\backend\static\
echo [完成] 前端文件复制完成
echo.

echo [4/4] 复制启动脚本和配置文件...
REM 如果 deploy 目录下已有 start.bat，直接复制；否则创建一个简单的版本
if exist "deploy\start.bat" (
    echo [信息] 使用已存在的 start.bat 文件
) else (
    echo [信息] 创建 start.bat 启动脚本...
    REM 直接复制已有的 start.bat（如果在源目录存在）
    if exist "start.bat" (
        copy /Y start.bat deploy\start.bat >nul
    ) else (
        REM 创建一个基本的启动脚本
        (
        echo @echo off
        echo chcp 65001 ^>nul
        echo cd /d "%%~dp0"
        echo cd backend
        echo if not exist "venv" python -m venv venv
        echo call venv\Scripts\activate.bat
        echo pip install -q -r requirements.txt
        echo if not exist ".env" copy /Y env.example .env ^>nul
        echo if not exist "logs" mkdir logs
        echo python main.py
        echo pause
        ) > deploy\start.bat
    )
)

REM 复制 stop.bat（如果存在）
if exist "deploy\stop.bat" (
    echo [信息] 使用已存在的 stop.bat 文件
) else (
    echo [信息] 创建 stop.bat 停止脚本...
    (
    echo @echo off
    echo echo 正在停止服务...
    echo for /f "tokens=2" %%%%a in ^('tasklist /FI "IMAGENAME eq python.exe" /FO LIST 2^>nul ^| findstr /C:"PID:"'^) do ^(
    echo     for /f "tokens=*" %%%%b in ^('wmic process where "ProcessId=%%%%a" get CommandLine /format:list 2^>nul ^| findstr /C:"CommandLine"'^) do ^(
    echo         echo %%%%b ^| findstr /C:"main.py" ^>nul
    echo         if !errorlevel! equ 0 ^(
    echo             taskkill /F /PID %%%%a ^>nul 2^>^&1
    echo         ^)
    echo     ^)
    echo ^)
    echo echo 服务已停止
    echo timeout /t 2 ^>nul
    ) > deploy\stop.bat
)

REM 创建 README
(
echo # MQTT IoT 管理系统 - Windows 部署包
echo.
echo ## 系统要求
echo.
echo - Windows 10 或更高版本
echo - Python 3.8 或更高版本
echo - 网络连接（用于安装依赖）
echo.
echo ## 安装步骤
echo.
echo 1. 解压部署包到目标目录
echo 2. 双击运行 `start.bat` 启动服务
echo 3. 首次运行会自动创建虚拟环境和安装依赖（可能需要几分钟）
echo 4. 浏览器访问 http://localhost:8000 查看前端界面
echo 5. 访问 http://localhost:8000/docs 查看 API 文档
echo.
echo ## 配置文件
echo.
echo 首次运行后，会在 `backend` 目录下创建 `.env` 文件，请根据实际情况修改配置：
echo.
echo - `SECRET_KEY`: JWT 签名密钥（生产环境必须修改）
echo - `HOST`: 服务器监听地址（默认: 0.0.0.0）
echo - `PORT`: 服务器端口（默认: 8000）
echo - `CORS_ORIGINS`: 允许的前端源地址（逗号分隔）
echo - `DATABASE_URL`: 数据库连接 URL（默认: sqlite:///./mqtt_iot.db）
echo.
echo ## 使用说明
echo.
echo - 启动服务: 双击 `start.bat`
echo - 停止服务: 双击 `stop.bat` 或直接关闭命令行窗口
echo - 日志文件: `backend\logs\app.log`
echo - 数据库文件: `backend\mqtt_iot.db`
echo.
echo ## 注意事项
echo.
echo 1. 首次启动会创建数据库和必要的目录
echo 2. 确保防火墙允许端口 8000 的访问
echo 3. 如果修改了端口号，请相应修改前端访问地址
echo 4. 生产环境务必修改 SECRET_KEY 配置
echo.
echo ## 故障排除
echo.
echo ### 端口被占用
echo 如果提示端口被占用，请修改 `backend\.env` 文件中的 `PORT` 配置
echo.
echo ### 依赖安装失败
echo 检查网络连接，或使用国内镜像源：
echo ```bash
echo pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
echo ```
echo.
echo ### 无法访问前端
echo 检查后端服务是否正常启动，访问 http://localhost:8000/docs 查看 API 文档
echo.
) > deploy\README_Windows.txt

echo [完成] 部署包准备完成
echo.

echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 部署文件位置: deploy 目录
echo.
echo 下一步:
echo 1. 检查 deploy 目录下的文件
echo 2. 打包 deploy 目录为 zip 文件
echo 3. 在 Windows 10 系统上解压并运行 start.bat
echo.
pause
