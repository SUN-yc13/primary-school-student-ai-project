@echo off
chcp 65001 >nul
echo ========================================
echo   学习效率助手 - 打包脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/4] 安装依赖包...
python -m pip install pyinstaller psutil -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 清理旧的打包文件
echo.
echo [2/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 使用PyInstaller打包
echo.
echo [3/4] 开始打包...
python -m PyInstaller --noconfirm --windowed --onefile ^
    --name "学习效率助手" ^
    --icon=NONE ^
    --add-data "data_manager.py;." ^
    --add-data "pomodoro.py;." ^
    --add-data "app_blocker.py;." ^
    --add-data "sticky_note.py;." ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

:: 完成
echo.
echo [4/4] 打包完成！
echo.
echo 可执行文件位置: dist\学习效率助手.exe
echo.
echo 如需制作安装包，请运行 build_installer.bat
echo.
pause
