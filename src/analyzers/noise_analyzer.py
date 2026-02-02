import cv2
import numpy as np
from typing import Dict, Tuple


class NoiseAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.thresholds = config.get('analysis', {})

    def analyze(self, image_path: str) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        results = {
            'noise_level': self._estimate_noise_level(gray),
            'psnr': self._calculate_psnr(gray),
            'ssim': self._calculate_ssim(gray),
            'snr': self._calculate_snr(gray)
        }
        
        threshold = self.thresholds.get('noise_threshold', {})
        max_noise = threshold.get('max', 20)
        
        results['noise_level']['pass'] = results['noise_level']['value'] <= max_noise
        results['psnr']['pass'] = results['psnr']['value'] >= 30
        results['snr']['pass'] = results['snr']['value'] >= 10
        
        return results

    def _estimate_noise_level(self, gray: np.ndarray) -> Dict:
        h, w = gray.shape
        
        if h < 2 or w < 2:
            return {'value': 0.0, 'unit': 'Standard deviation', 'description': 'Noise level'}
        
        noise_map = np.zeros_like(gray, dtype=np.float32)
        
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                neighbors = gray[i-1:i+2, j-1:j+2]
                local_mean = np.mean(neighbors)
                noise_map[i, j] = np.abs(gray[i, j] - local_mean)
        
        noise_level = np.std(noise_map)
        
        return {
            'value': float(noise_level),
            'unit': '标准差',
            'description': '估计噪声水平'
        }
    
    def _calculate_psnr(self, gray: np.ndarray) -> Dict:
        h, w = gray.shape
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        mse = np.mean((gray.astype(np.float64) - blurred.astype(np.float64)) ** 2)
        
        if mse == 0:
            psnr = float('inf')
        else:
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        return {
            'value': float(psnr),
            'unit': '分贝',
            'description': '峰值信噪比 - 越高越好'
        }
    
    def _calculate_ssim(self, gray: np.ndarray) -> Dict:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        mu1 = cv2.GaussianBlur(gray.astype(np.float64), (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(blurred.astype(np.float64), (11, 11), 1.5)
        
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.GaussianBlur(gray.astype(np.float64) ** 2, (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(blurred.astype(np.float64) ** 2, (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(gray.astype(np.float64) * blurred.astype(np.float64), (11, 11), 1.5) - mu1_mu2
        
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        
        ssim = np.mean(ssim_map)
        
        return {
            'value': float(ssim),
            'unit': '0-1 范围',
            'description': '结构相似性 - 越高越好'
        }
    
    def _calculate_snr(self, gray: np.ndarray) -> Dict:
        edges = cv2.Canny(gray, threshold1=50, threshold2=150)
        uniform_mask = ~edges.astype(bool)
        
        if np.sum(uniform_mask) < gray.size * 0.1:
            uniform_mask = np.ones_like(gray, dtype=bool)
        
        signal = np.mean(gray[uniform_mask])
        noise = np.std(gray[uniform_mask])
        snr = signal / (noise + 1e-6)
        
        return {
            'value': float(snr),
            'unit': '比值',
            'description': '信噪比 - 越高越好'
        }
