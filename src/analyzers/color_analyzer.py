import cv2
import numpy as np
from typing import Dict, List


class ColorAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.thresholds = config.get('analysis', {})

    def analyze(self, image_path: str) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        results = {
            'white_balance': self._analyze_white_balance(image),
            'color_distribution': self._analyze_color_distribution(image),
            'color_temperature': self._estimate_color_temperature(image),
            'color_cast': self._detect_color_cast(image),
            'dominant_colors': self._find_dominant_colors(image)
        }
        
        results['white_balance']['pass'] = results['white_balance']['is_balanced']
        results['color_cast']['pass'] = not results['color_cast']['has_cast']
        
        return results

    def _analyze_white_balance(self, image: np.ndarray) -> Dict:
        h, w = image.shape[:2]
        
        center_crop = image[h//4:3*h//4, w//4:3*w//4]
        
        mean_r = np.mean(center_crop[:, :, 2])
        mean_g = np.mean(center_crop[:, :, 1])
        mean_b = np.mean(center_crop[:, :, 0])
        
        max_channel = max(mean_r, mean_g, mean_b)
        min_channel = min(mean_r, mean_g, mean_b)
        
        balance_ratio = min_channel / max_channel if max_channel > 0 else 0
        is_balanced = balance_ratio > 0.85
        
        return {
            'mean_r': float(mean_r),
            'mean_g': float(mean_g),
            'mean_b': float(mean_b),
            'balance_ratio': float(balance_ratio),
            'is_balanced': is_balanced,
            'description': '白平衡分析 - 各通道平衡时为良好'
        }
    
    def _analyze_color_distribution(self, image: np.ndarray) -> Dict:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
        
        h_hist = h_hist.flatten().tolist()
        s_hist = s_hist.flatten().tolist()
        v_hist = v_hist.flatten().tolist()
        
        dominant_hue = np.argmax(h_hist)
        mean_saturation = np.mean(hsv[:, :, 1])
        mean_value = np.mean(hsv[:, :, 2])
        
        return {
            'hue_histogram': h_hist,
            'saturation_histogram': s_hist,
            'value_histogram': v_hist,
            'dominant_hue': int(dominant_hue),
            'mean_saturation': float(mean_saturation),
            'mean_value': float(mean_value),
            'description': 'HSV色彩空间分布分析'
        }
    
    def _estimate_color_temperature(self, image: np.ndarray) -> Dict:
        h, w = image.shape[:2]
        
        center_crop = image[h//4:3*h//4, w//4:3*w//4]
        
        mean_r = np.mean(center_crop[:, :, 2])
        mean_g = np.mean(center_crop[:, :, 1])
        mean_b = np.mean(center_crop[:, :, 0])
        
        if mean_r + mean_b == 0:
            temperature = 6500
        else:
            ratio = mean_r / (mean_b + 1e-10)
            
            if ratio > 1.5:
                temperature = 3000
            elif ratio > 1.2:
                temperature = 4000
            elif ratio > 1.0:
                temperature = 5000
            elif ratio > 0.8:
                temperature = 6500
            elif ratio > 0.6:
                temperature = 8000
            else:
                temperature = 10000
        
        temp_category = self._categorize_temperature(temperature)
        
        return {
            'temperature': int(temperature),
            'category': temp_category,
            'description': '估计色温 - 单位：开尔文'
        }
    
    def _categorize_temperature(self, temp: int) -> str:
        if temp < 4000:
            return '暖色（黄/橙）'
        elif temp < 5000:
            return '中性暖'
        elif temp < 6500:
            return '中性'
        elif temp < 8000:
            return '中性冷'
        else:
            return '冷色（蓝）'
    
    def _detect_color_cast(self, image: np.ndarray) -> Dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        diff_r = cv2.absdiff(gray, image[:, :, 2])
        diff_g = cv2.absdiff(gray, image[:, :, 1])
        diff_b = cv2.absdiff(gray, image[:, :, 0])
        
        mean_diff_r = np.mean(diff_r)
        mean_diff_g = np.mean(diff_g)
        mean_diff_b = np.mean(diff_b)
        
        diffs = [mean_diff_r, mean_diff_g, mean_diff_b]
        max_diff = max(diffs)
        min_diff = min(diffs)
        
        cast_threshold = 5.0
        has_cast = max_diff > cast_threshold and (max_diff - min_diff) > cast_threshold
        
        cast_type = '无色偏'
        if has_cast:
            if mean_diff_r == max_diff:
                cast_type = '红色偏'
            elif mean_diff_g == max_diff:
                cast_type = '绿色偏'
            else:
                cast_type = '蓝色偏'
        
        return {
            'has_cast': has_cast,
            'cast_type': cast_type,
            'red_diff': float(mean_diff_r),
            'green_diff': float(mean_diff_g),
            'blue_diff': float(mean_diff_b),
            'description': '色偏检测 - 检测图像是否存在颜色倾向'
        }

    def _find_dominant_colors(self, image: np.ndarray, k: int = 5) -> Dict:
        pixels = image.reshape(-1, 3).astype(np.float32)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        
        counts = np.bincount(labels.flatten())
        percentages = (counts / len(labels)) * 100
        
        dominant_colors = []
        for i in range(k):
            color = {
                'bgr': centers[i].tolist(),
                'rgb': centers[i][::-1].tolist(),
                'percentage': float(percentages[i])
            }
            dominant_colors.append(color)
        
        dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
        
        return {
            'colors': dominant_colors,
            'k': k,
            'description': f'前{k}个主色调'
        }
    
    def calculate_color_accuracy(self, image_path: str, reference_colors: List[Dict]) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        h, w = image.shape[:2]
        
        results = []
        for ref_color in reference_colors:
            x = int(ref_color['x'] * w)
            y = int(ref_color['y'] * h)
            radius = int(ref_color.get('radius', 10))
            
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(mask, (x, y), radius, 255, -1)
            
            mean_color = cv2.mean(image, mask=mask)[:3]
            
            ref_bgr = ref_color['bgr']
            ref_rgb = ref_color.get('rgb', ref_bgr[::-1])
            
            delta_e = self._calculate_delta_e(mean_color, ref_bgr)
            
            result = {
                'reference_color': ref_rgb,
                'measured_color': mean_color[::-1],
                'delta_e': float(delta_e),
                'pass': delta_e < 10.0
            }
            results.append(result)
        
        return {
            'colors': results,
            'average_delta_e': float(np.mean([r['delta_e'] for r in results])),
            'pass': all(r['pass'] for r in results),
            'description': '与参考颜色的色彩准确性'
        }

    def _calculate_delta_e(self, color1: np.ndarray, color2: np.ndarray) -> float:
        def rgb_to_lab(rgb):
            rgb = np.array(rgb) / 255.0
            
            mask = rgb > 0.04045
            rgb[mask] = ((rgb[mask] + 0.055) / 1.055) ** 2.4
            rgb[~mask] = rgb[~mask] / 12.92
            
            rgb = rgb * 100
            
            xyz = np.zeros(3)
            xyz[0] = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
            xyz[1] = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
            xyz[2] = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
            
            xyz[0] /= 95.047
            xyz[1] /= 100.000
            xyz[2] /= 108.883
            
            xyz = np.where(xyz > 0.008856, xyz ** (1/3), 7.787 * xyz + 16/116)
            
            lab = np.zeros(3)
            lab[0] = 116 * xyz[1] - 16
            lab[1] = 500 * (xyz[0] - xyz[1])
            lab[2] = 200 * (xyz[1] - xyz[2])
            
            return lab
        
        lab1 = rgb_to_lab(color1)
        lab2 = rgb_to_lab(color2)
        
        delta_e = np.sqrt(np.sum((lab1 - lab2) ** 2))
        
        return delta_e
