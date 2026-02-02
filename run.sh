#!/bin/bash

echo "===================================="
echo "Android 相机图像质量自动化测试系统"
echo "===================================="
echo ""

echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

python3 --version

echo ""
echo "[2/4] 检查ADB环境..."
if ! command -v adb &> /dev/null; then
    echo "[警告] 未找到ADB，请确保已安装Android SDK Platform Tools"
    echo "        并将ADB添加到系统PATH"
    echo "        或在config.json中配置adb_path"
    exit 1
fi

adb version

echo ""
echo "[3/4] 检查设备连接..."
adb devices
echo ""
echo "如果上面没有显示设备，请："
echo "1. 确保手机已通过USB连接到电脑"
echo "2. 手机已开启USB调试"
echo "3. 手机已授权电脑调试"
echo ""

echo "[4/4] 开始运行测试..."
echo ""
python3 main.py

echo ""
echo "===================================="
echo "测试完成！"
echo "报告已保存到 reports/ 目录"
echo "===================================="
