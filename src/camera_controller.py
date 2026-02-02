import os
import time
import traceback
from datetime import datetime
from typing import Optional, Tuple
from .adb_controller import ADBController


class CameraController:
    def __init__(self, adb_controller: ADBController, config: dict):
        self.adb = adb_controller
        self.config = config
        self.output_dir = config['output']['images_dir']
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def capture_photo(self, name: Optional[str] = None) -> Tuple[str, str]:
        local_path = None
        
        try:
            print(f"\n准备读取照片...")
            print("=" * 50)
            print("操作说明：")
            print("1. 请手动打开手机相机应用")
            print("2. 对焦并拍照")
            print("3. 确保照片已保存到相册")
            print("4. 按任意键继续")
            print("=" * 50)
            
            input("\n按Enter键继续...")
            
            photos = self.adb.list_files_with_time()
            
            if photos:
                latest_photo = photos[0]
                print(f"\n✓ 检测到相册最新照片: {latest_photo['name']}")
                print(f"  时间: {latest_photo['timestamp']}")
                print(f"  路径: {latest_photo['path']}")
                
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"photo_{timestamp_str}.jpg"
                local_path = os.path.join(self.output_dir, name)
                
                self.adb.pull_file(latest_photo['path'], local_path)
                
                if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    print(f"\n✓ 照片已保存到: {local_path}")
                    print(f"  文件大小: {os.path.getsize(local_path)} 字节")
                    return local_path, name
                else:
                    print(f"\n⚠ 警告：文件传输失败或文件为空")
                    print(f"  本地路径: {local_path}")
                    return local_path, name
            else:
                print("\n⚠ 警告：相册中没有照片")
                print("\n建议：")
                print("- 请先手动拍摄一些照片到相册")
                print("- 确认照片保存路径正确")
                print("- 检查手机存储权限")
                print("\n程序将创建空文件以继续，但无法进行分析")
                
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"photo_{timestamp_str}.jpg"
                local_path = os.path.join(self.output_dir, name)
                
                return local_path, name
                
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to capture photo: {e}")

    def capture_screenshot(self, name: Optional[str] = None) -> Tuple[str, str]:
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}.png"
        
        local_path = os.path.join(self.output_dir, name)
        
        try:
            self.adb.screen_capture(local_path)
            print(f"Screenshot captured and saved to: {local_path}")
            return local_path, name
        except Exception as e:
            raise RuntimeError(f"Failed to capture screenshot: {e}")

    def capture_multiple_photos(self, count: int, delay: float = 2.0) -> list:
        photos = []
        print(f"\n将读取 {count} 张照片进行分析")
        print("请确保相册中有足够的照片")
        print("-" * 50)
        
        for i in range(count):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"photo_{timestamp}_{i+1}.jpg"
            try:
                path, filename = self.capture_photo(name)
                photos.append((path, filename))
                if i < count - 1:
                    print(f"\n准备读取下一张照片...")
            except Exception as e:
                print(f"Failed to capture photo {i+1}: {e}")
        
        print("\n" + "=" * 50)
        print(f"照片读取完成！共读取 {len(photos)} 张照片")
        print("=" * 50 + "\n")
        
        return photos

    def get_camera_info(self) -> dict:
        info = {}
        
        try:
            success, output = self.adb._run_command(['shell', 'dumpsys', 'media.camera'])
            if success:
                info['camera_service'] = 'Available'
        except:
            info['camera_service'] = 'Unknown'
        
        try:
            success, output = self.adb._run_command(['shell', 'pm', 'list', 'packages', 'camera'])
            if success:
                info['camera_apps'] = [line.split(':')[-1] for line in output.strip().split('\n') if line]
        except:
            info['camera_apps'] = []
        
        return info
