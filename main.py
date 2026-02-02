import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.adb_controller import ADBController
from src.camera_controller import CameraController
from src.analyzers.quality_analyzer import ImageQualityAnalyzer
from src.analyzers.sharpness_analyzer import SharpnessAnalyzer
from src.analyzers.noise_analyzer import NoiseAnalyzer
from src.analyzers.color_analyzer import ColorAnalyzer
from src.report_generator import ReportGenerator


class ImageTestAutomation:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.adb = None
        self.camera = None
        self.quality_analyzer = None
        self.sharpness_analyzer = None
        self.noise_analyzer = None
        self.color_analyzer = None
        self.report_generator = None
        self.test_results = {}
        self.test_images = []

    def _load_config(self, config_path: str) -> dict:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def initialize(self):
        print("=" * 50)
        print("图像质量自动化测试工具")
        print("=" * 50)
        
        print("\n1. 初始化ADB连接...")
        adb_config = self.config.get('adb', {})
        self.adb = ADBController(
            adb_path=adb_config.get('adb_path', ''),
            device_id=adb_config.get('device_id', ''),
            timeout=adb_config.get('timeout', 30)
        )
        
        print("2. 连接设备...")
        self.adb.connect()
        
        device_info = self.adb.get_device_info()
        print(f"   设备型号: {device_info.get('model', 'Unknown')}")
        print(f"   制造商: {device_info.get('manufacturer', 'Unknown')}")
        print(f"   Android版本: {device_info.get('android_version', 'Unknown')}")
        
        print("\n3. 初始化相机控制器...")
        self.camera = CameraController(self.adb, self.config)
        
        print("4. 初始化分析器...")
        self.quality_analyzer = ImageQualityAnalyzer(self.config)
        self.sharpness_analyzer = SharpnessAnalyzer(self.config)
        self.noise_analyzer = NoiseAnalyzer(self.config)
        self.color_analyzer = ColorAnalyzer(self.config)
        
        print("5. 初始化报告生成器...")
        self.report_generator = ReportGenerator(self.config)
        
        self.test_results['test_info'] = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'device_model': device_info.get('model', 'Unknown'),
            'android_version': device_info.get('android_version', 'Unknown'),
            'manufacturer': device_info.get('manufacturer', 'Unknown')
        }
        
        print("\n初始化完成！\n")

    def run_test(self, photo_count: int = 3) -> Dict:
        print("=" * 50)
        print("开始测试")
        print("=" * 50)
        
        print(f"\n读取 {photo_count} 张照片进行分析...")
        photos = self.camera.capture_multiple_photos(photo_count)
        
        for i, (path, name) in enumerate(photos, 1):
            print(f"\n分析第 {i} 张照片: {name}")
            self._analyze_image(path, name, i)
        
        self._generate_final_report()
        
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
        
        return self.test_results

    def _analyze_image(self, image_path: str, image_name: str, index: int):
        if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
            print(f"  ⚠ 跳过分析：文件不存在或为空")
            return
        
        self.test_images.append({
            'path': image_path,
            'name': image_name,
            'size': self._get_image_size(image_path)
        })
        
        print(f"  - 图像质量分析...")
        quality_results = self.quality_analyzer.analyze(image_path)
        
        print(f"  - 清晰度测试...")
        sharpness_results = self.sharpness_analyzer.analyze(image_path)
        
        print(f"  - 噪声检测...")
        noise_results = self.noise_analyzer.analyze(image_path)
        
        print(f"  - 色彩分析...")
        color_results = self.color_analyzer.analyze(image_path)
        
        if index == 1:
            self.test_results['quality'] = quality_results
            self.test_results['sharpness'] = sharpness_results
            self.test_results['noise'] = noise_results
            self.test_results['color'] = color_results

    def _get_image_size(self, image_path: str) -> str:
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is not None:
                h, w = img.shape[:2]
                return f"{w}x{h}"
        except:
            pass
        return "Unknown"

    def _generate_final_report(self):
        print("\n生成测试报告...")
        
        images_dir = self.config['output']['images_dir']
        reports_dir = self.config['output']['reports_dir']
        
        processed_images = []
        for img in self.test_images:
            original_path = img['path']
            img_name = img['name']
            
            if os.path.exists(original_path):
                dest_path = os.path.join(reports_dir, img_name)
                import shutil
                try:
                    shutil.copy2(original_path, dest_path)
                    processed_images.append({
                        'path': img_name,
                        'name': img_name,
                        'size': img['size']
                    })
                    print(f"  已复制图片: {img_name}")
                except Exception as e:
                    print(f"  复制图片失败 {img_name}: {e}")
                    processed_images.append({
                        'path': original_path,
                        'name': img_name,
                        'size': img['size']
                    })
            else:
                processed_images.append({
                    'path': original_path,
                    'name': img_name,
                    'size': img['size']
                })
        
        report_data = {
            'test_info': self.test_results['test_info'],
            'test_images': processed_images,
            'quality_tests': self._format_quality_tests(),
            'sharpness_tests': self._format_sharpness_tests(),
            'noise_tests': self._format_noise_tests(),
            'color_tests': self._format_color_tests(),
            'quality_pass_count': self._count_pass_tests('quality'),
            'quality_total_count': self._count_total_tests('quality'),
            'quality_pass_rate': self._calculate_pass_rate('quality'),
            'sharpness_pass_count': self._count_pass_tests('sharpness'),
            'sharpness_total_count': self._count_total_tests('sharpness'),
            'sharpness_pass_rate': self._calculate_pass_rate('sharpness'),
            'noise_pass_count': self._count_pass_tests('noise'),
            'noise_total_count': self._count_total_tests('noise'),
            'noise_pass_rate': self._calculate_pass_rate('noise'),
            'color_pass_count': self._count_pass_tests('color'),
            'color_total_count': self._count_total_tests('color'),
            'color_pass_rate': self._calculate_pass_rate('color'),
            'total_tests': self._count_total_tests_all(),
            'passed_tests': self._count_passed_tests_all(),
            'pass_rate': self._calculate_pass_rate_all(),
            'recommendations': self._generate_recommendations()
        }
        
        report_path = self.report_generator.generate_report(report_data)
        print(f"报告已保存: {report_path}")

    def _format_quality_tests(self) -> List[Dict]:
        quality = self.test_results.get('quality', {})
        tests = []
        
        metric_names = {
            'brightness': '亮度',
            'contrast': '对比度',
            'saturation': '饱和度',
            'tone_analysis': '影调分析'
        }
        
        for metric, data in quality.items():
            if isinstance(data, dict) and 'pass' in data:
                test = {
                    'name': metric_names.get(metric, metric),
                    'pass': data['pass'],
                    'description': data.get('description', ''),
                    'details': []
                }
                
                if metric == 'tone_analysis':
                    test['details'].append({
                        'label': '高光占比',
                        'value': f"{data.get('highlight_ratio', 0):.2%}"
                    })
                    test['details'].append({
                        'label': '阴影占比',
                        'value': f"{data.get('shadow_ratio', 0):.2%}"
                    })
                    if data.get('issues'):
                        test['details'].append({
                            'label': '问题',
                            'value': ', '.join(data.get('issues', []))
                        })
                else:
                    test['details'].append({
                        'label': '数值',
                        'value': f"{data.get('value', 0):.2f}"
                    })
                    test['details'].append({
                        'label': '单位',
                        'value': data.get('unit', '')
                    })
                
                tests.append(test)
        
        return tests

    def _format_sharpness_tests(self) -> List[Dict]:
        sharpness = self.test_results.get('sharpness', {})
        tests = []
        
        metric_names = {
            'laplacian': '拉普拉斯方差',
            'sobel': 'Sobel梯度',
            'tenengrad': 'Tenengrad指标',
            'fft_focus': 'FFT焦点'
        }
        
        for metric, data in sharpness.items():
            if isinstance(data, dict) and 'pass' in data:
                tests.append({
                    'name': metric_names.get(metric, metric),
                    'pass': data['pass'],
                    'description': data.get('description', ''),
                    'details': [
                        {'label': '数值', 'value': f"{data.get('value', 0):.2f}"},
                        {'label': '单位', 'value': data.get('unit', '')},
                        {'label': '说明', 'value': data.get('description', '')}
                    ]
                })
        
        return tests

    def _format_noise_tests(self) -> List[Dict]:
        noise = self.test_results.get('noise', {})
        tests = []
        
        metric_names = {
            'noise_level': '噪声水平',
            'psnr': '峰值信噪比',
            'ssim': '结构相似性',
            'snr': '信噪比'
        }
        
        for metric, data in noise.items():
            if isinstance(data, dict) and 'pass' in data:
                tests.append({
                    'name': metric_names.get(metric, metric),
                    'pass': data['pass'],
                    'description': data.get('description', ''),
                    'details': [
                        {'label': '数值', 'value': f"{data.get('value', 0):.2f}"},
                        {'label': '单位', 'value': data.get('unit', '')},
                        {'label': '说明', 'value': data.get('description', '')}
                    ]
                })
        
        return tests

    def _format_color_tests(self) -> List[Dict]:
        color = self.test_results.get('color', {})
        tests = []
        
        metric_names = {
            'white_balance': '白平衡',
            'color_distribution': '色彩分布',
            'color_temperature': '色温',
            'color_cast': '色偏检测',
            'dominant_colors': '主色调'
        }
        
        for metric, data in color.items():
            if isinstance(data, dict) and 'pass' in data:
                test = {
                    'name': metric_names.get(metric, metric),
                    'pass': data['pass'],
                    'description': data.get('description', ''),
                    'details': []
                }
                
                if metric == 'color_temperature':
                    test['details'].append({
                        'label': '色温',
                        'value': f"{data.get('temperature', 0)}K"
                    })
                    test['details'].append({
                        'label': '类别',
                        'value': data.get('category', '未知')
                    })
                elif metric == 'color_cast':
                    test['details'].append({
                        'label': '色偏类型',
                        'value': data.get('cast_type', '无')
                    })
                    test['details'].append({
                        'label': '是否存在',
                        'value': '是' if data.get('has_cast', False) else '否'
                    })
                elif metric == 'dominant_colors':
                    test['details'].append({
                        'label': '主色调数量',
                        'value': str(data.get('k', 0))
                    })
                else:
                    test['details'].append({
                        'label': '数值',
                        'value': f"{data.get('value', 0):.2f}"
                    })
                    test['details'].append({
                        'label': '单位',
                        'value': data.get('unit', '')
                    })
                
                tests.append(test)
        
        return tests

    def _count_pass_tests(self, category: str) -> int:
        category_data = self.test_results.get(category, {})
        count = 0
        for data in category_data.values():
            if isinstance(data, dict) and data.get('pass', False):
                count += 1
        return count

    def _count_total_tests(self, category: str) -> int:
        category_data = self.test_results.get(category, {})
        count = 0
        for data in category_data.values():
            if isinstance(data, dict) and 'pass' in data:
                count += 1
        return count

    def _calculate_pass_rate(self, category: str) -> float:
        total = self._count_total_tests(category)
        passed = self._count_pass_tests(category)
        if total == 0:
            return 0.0
        return (passed / total) * 100

    def _count_total_tests_all(self) -> int:
        return sum([self._count_total_tests(cat) for cat in ['quality', 'sharpness', 'noise', 'color']])

    def _count_passed_tests_all(self) -> int:
        return sum([self._count_pass_tests(cat) for cat in ['quality', 'sharpness', 'noise', 'color']])

    def _calculate_pass_rate_all(self) -> float:
        total = self._count_total_tests_all()
        passed = self._count_passed_tests_all()
        if total == 0:
            return 0.0
        return (passed / total) * 100

    def _generate_recommendations(self) -> List[str]:
        analysis = self.test_results
        recommendations = []
        
        quality = analysis.get('quality', {})
        brightness = quality.get('brightness', {})
        if not brightness.get('pass', True):
            value = brightness.get('value', 0)
            if value < 50:
                recommendations.append("建议：图像偏暗，可以增加曝光补偿")
            elif value > 200:
                recommendations.append("建议：图像偏亮，可以降低曝光补偿")
        
        tone = quality.get('tone_analysis', {})
        if tone.get('issues'):
            recommendations.append(f"建议：{', '.join(tone.get('issues', []))}")
        
        noise = analysis.get('noise', {})
        noise_level = noise.get('noise_level', {})
        if not noise_level.get('pass', True):
            recommendations.append("建议：噪声较高，建议使用更好的光线条件或降低ISO")
        
        sharpness = analysis.get('sharpness', {})
        laplacian = sharpness.get('laplacian', {})
        if not laplacian.get('pass', True):
            recommendations.append("建议：清晰度不足，请确保对焦准确")
        
        color = analysis.get('color', {})
        color_cast = color.get('color_cast', {})
        if color_cast.get('has_cast', False):
            recommendations.append(f"建议：检测到{color_cast.get('cast_type', '')}，请检查白平衡设置")
        
        return recommendations


def main():
    try:
        automation = ImageTestAutomation()
        automation.initialize()
        automation.run_test(photo_count=3)
        
        print("\n" + "=" * 50)
        print("照片读取完成！共读取 {} 张照片".format(len(automation.test_images)))
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
