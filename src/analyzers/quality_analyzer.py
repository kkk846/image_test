import cv2
import numpy as np
from typing import Dict, Tuple


class ImageQualityAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.thresholds = config.get('analysis', {})

    def analyze(self, image_path: str) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        results = {
            'brightness': self._calculate_brightness(image),
            'contrast': self._calculate_contrast(image),
            'saturation': self._calculate_saturation(image),
            'histogram': self._calculate_histogram(image),
            'tone_analysis': self._analyze_tone(gray)
        }
        
        results['brightness']['pass'] = self._check_brightness(results['brightness']['value'])
        results['contrast']['pass'] = self._check_contrast(results['contrast']['value'])
        results['saturation']['pass'] = self._check_saturation(results['saturation']['value'])
        results['tone_analysis']['pass'] = len(results['tone_analysis']['issues']) == 0
        
        return results

    def _calculate_brightness(self, image: np.ndarray) -> Dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        return {
            'value': float(mean_brightness),
            'std': float(std_brightness),
            'unit': '0-255 范围',
            'description': '图像平均亮度'
        }
    
    def _calculate_contrast(self, image: np.ndarray) -> Dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        
        return {
            'value': float(contrast),
            'unit': '标准差',
            'description': '图像对比度水平'
        }
    
    def _calculate_saturation(self, image: np.ndarray) -> Dict:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        mean_saturation = np.mean(saturation)
        
        return {
            'value': float(mean_saturation),
            'unit': '0-255 范围',
            'description': '图像平均饱和度'
        }
    
    def _calculate_histogram(self, image: np.ndarray) -> Dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten().tolist()
        
        return {
            'values': hist,
            'bins': 256,
            'description': '灰度直方图分布'
        }

    def _check_brightness(self, value: float) -> bool:
        threshold = self.thresholds.get('brightness_threshold', {})
        min_val = threshold.get('min', 50)
        max_val = threshold.get('max', 200)
        return min_val <= value <= max_val

    def _check_contrast(self, value: float) -> bool:
        threshold = self.thresholds.get('contrast_threshold', {})
        min_val = threshold.get('min', 30)
        max_val = threshold.get('max', 150)
        return min_val <= value <= max_val

    def _check_saturation(self, value: float) -> bool:
        return value > 50
    
    def _analyze_tone(self, gray: np.ndarray) -> Dict:
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        total = gray.size
        highlight_ratio = hist[230:].sum() / total
        shadow_ratio = hist[:25].sum() / total
        
        issues = []
        if highlight_ratio > 0.15:
            issues.append("可能过曝")
        if shadow_ratio > 0.15:
            issues.append("可能欠曝")
        
        return {
            'highlight_ratio': float(highlight_ratio),
            'shadow_ratio': float(shadow_ratio),
            'issues': issues,
            'description': '影调分析'
        }
