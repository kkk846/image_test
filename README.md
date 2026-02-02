# Android 相机图像质量自动化测试系统

一个专业、开源的 Android 相机图像质量（Image Quality, IQ）自动化评估工具，基于 Python + OpenCV + ADB 实现。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

## 功能特性

- **自动拍照**: 通过 ADB 触发相机拍照
- **图像质量分析**: 使用 OpenCV 和 NumPy 进行全面分析
- **专业报告**: 生成详细的 HTML 测试报告
- **模块化设计**: 易于扩展新的分析器

## 支持的指标

### 图像质量（4项）
- **亮度**: 灰度均值，用于曝光评估
- **对比度**: 标准差，衡量动态范围
- **饱和度**: HSV 饱和度通道均值
- **影调分析**: 基于直方图的高光/阴影检测

### 清晰度（4项）
- **拉普拉斯方差**: 边缘锐度测量
- **Sobel 梯度**: 边缘强度评估
- **Tenengrad**: 基于梯度的焦点度量
- **FFT 焦点**: 高频内容比例

### 噪声检测（4项）
- **噪声水平**: 均匀区域标准差
- **峰值信噪比 (PSNR)**: 峰值信噪比
- **结构相似性 (SSIM)**: 结构相似度指数
- **信噪比 (SNR)**: 均匀区域信噪比

### 色彩分析（5项）
- **白平衡**: RGB 通道平衡
- **色彩分布**: HSV 直方图分析
- **色温**: 红蓝比估算
- **色偏检测**: 通道差异分析
- **主色调**: K-means 聚类

## 安装

### 前置条件
- Python 3.8+
- Android SDK Platform Tools (ADB)
- 已开启 USB 调试的 Android 设备

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速开始

#### Windows
```bash
run.bat
```

#### Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

#### 直接运行
```bash
python main.py
```

### 配置说明

编辑 `config.json` 来自定义测试参数：

```json
{
  "adb": {
    "adb_path": "",
    "device_id": "",
    "timeout": 30
  },
  "camera": {
    "capture_delay": 2,
    "image_format": "jpg",
    "quality": 100
  },
  "analysis": {
    "brightness_threshold": {"min": 30, "max": 230},
    "contrast_threshold": {"min": 20, "max": 180},
    "sharpness_threshold": {"min": 50},
    "noise_threshold": {"max": 40}
  },
  "output": {
    "images_dir": "output/images",
    "reports_dir": "reports"
  }
}
```

## 项目结构

```
image_test/
├── main.py                 # 主程序入口
├── config.json            # 配置文件
├── requirements.txt        # 依赖列表
├── run.bat               # Windows 启动脚本
├── run.sh                # Linux/Mac 启动脚本
├── src/                  # 源代码
│   ├── adb_controller.py       # ADB 控制器
│   ├── camera_controller.py    # 相机控制器
│   ├── report_generator.py    # 报告生成器
│   ├── analyzers/            # 分析器
│   │   ├── quality_analyzer.py
│   │   ├── sharpness_analyzer.py
│   │   ├── noise_analyzer.py
│   │   └── color_analyzer.py
│   └── utils/
├── output/               # 输出目录
│   └── images/
└── reports/              # 报告目录
```

## 输出

测试报告保存在 `reports/` 目录：
- 文件名格式：`test_report_YYYYMMDD_HHMMSS.html`
- 用浏览器打开查看详细结果

## 技术细节

### 使用的算法
- **Canny 边缘检测**: 用于均匀区域选择
- **直方图分析**: 用于影调分布
- **拉普拉斯算子**: 用于清晰度测量
- **K-means 聚类**: 用于主色调提取
- **SSIM**: 用于结构相似性

### 测试建议
- 使用标准测试图卡或均匀光照场景
- 确保对焦准确，避免模糊
- 使用三脚架或固定手机位置
- 在充足且均匀的光线下拍摄
- 拍摄 3-5 张照片取平均结果

## 未来计划

- 支持 RAW (DNG) 图像解析
- 添加动态范围估算
- 实现色彩准确性 (ΔE) 分析
- 构建 Web UI (Gradio/Streamlit)
- 支持多设备并行测试
- 添加视频质量测试

## 许可证

MIT License

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 致谢

本项目参考了相机图像质量评估的行业实践：
- **SNR**: ISO 15739 标准中的核心噪声指标
- **影调分析**: 基于人眼对高光/阴影的敏感性
- **色温评估**: 白平衡校准的基础
- **均匀区域选择**: 专业 IQ 测试的标准做法（如 Imatest）
- **SSIM**: 结构相似性的经典指标

## 💡 作者

**刘锦坤**（东莞理工学院 · 计算机科学与技术）
