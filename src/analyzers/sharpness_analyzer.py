import cv2
import numpy as np
from typing import Dict


class SharpnessAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.thresholds = config.get('analysis', {})

    def analyze(self, image_path: str) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        results = {
            'laplacian': self._laplacian_variance(gray),
            'sobel': self._sobel_gradient(gray),
            'tenengrad': self._tenengrad(gray),
            'fft_focus': self._fft_focus(gray)
        }
        
        threshold = self.thresholds.get('sharpness_threshold', {})
        min_sharpness = threshold.get('min', 100)
        
        for metric in results:
            results[metric]['pass'] = results[metric]['value'] >= min_sharpness
        
        return results

    def _laplacian_variance(self, gray: np.ndarray) -> Dict:
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        return {
            'value': float(variance),
            'unit': '方差',
            'description': '拉普拉斯方差 - 值越高表示图像越清晰'
        }
    
    def _sobel_gradient(self, gray: np.ndarray) -> Dict:
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        mean_gradient = np.mean(gradient_magnitude)
        
        return {
            'value': float(mean_gradient),
            'unit': '梯度均值',
            'description': 'Sobel梯度 - 边缘检测清晰度'
        }
    
    def _tenengrad(self, gray: np.ndarray) -> Dict:
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = np.mean(gx**2 + gy**2)
        
        return {
            'value': float(tenengrad),
            'unit': '评分',
            'description': 'Tenengrad指标 - 基于梯度的清晰度'
        }
    
    def _fft_focus(self, gray: np.ndarray) -> Dict:
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        
        mask = np.zeros((rows, cols), np.uint8)
        r = min(rows, cols) // 4
        cv2.circle(mask, (ccol, crow), r, 1, -1)
        
        high_freq = np.sum(magnitude_spectrum * mask)
        total_freq = np.sum(magnitude_spectrum)
        
        focus_score = high_freq / (total_freq + 1e-10) * 1000
        
        return {
            'value': float(focus_score),
            'unit': '高频比例',
            'description': 'FFT焦点 - 高频内容比例，越高越清晰'
        }

    def detect_blur_regions(self, image_path: str, block_size: int = 64) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        blur_map = np.zeros((h // block_size, w // block_size))
        
        for i in range(0, h, block_size):
            for j in range(0, w, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                if block.shape[0] == block_size and block.shape[1] == block_size:
                    laplacian = cv2.Laplacian(block, cv2.CV_64F)
                    blur_map[i//block_size, j//block_size] = laplacian.var()
        
        threshold = self.thresholds.get('sharpness_threshold', {}).get('min', 100)
        blurry_blocks = np.sum(blur_map < threshold)
        total_blocks = blur_map.size
        
        return {
            'blur_map': blur_map.tolist(),
            'blurry_blocks': int(blurry_blocks),
            'total_blocks': int(total_blocks),
            'blurry_ratio': float(blurry_blocks / total_blocks),
            'pass': blurry_blocks / total_blocks < 0.3
        }
