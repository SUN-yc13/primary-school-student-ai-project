@echo off
chcp 65001 >nul
:: 输出当前文件夹目录结构到文本文件
tree /f > 文件夹结构清单.txt
echo 目录结构已保存到【文件夹结构清单.txt】
pause