import subprocess
import json
import os
from typing import Optional, List
import time


class ADBController:
    def __init__(self, adb_path: str = "", device_id: str = "", timeout: int = 30):
        self.adb_path = adb_path
        self.device_id = device_id
        self.timeout = timeout
        self._check_adb_available()

    def _get_adb_command(self) -> str:
        if self.adb_path and os.path.exists(self.adb_path):
            return self.adb_path
        return 'adb'

    def _check_adb_available(self):
        try:
            adb_cmd = self._get_adb_command()
            result = subprocess.run([adb_cmd, 'version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode != 0:
                raise RuntimeError("ADB is not installed or not in PATH")
        except FileNotFoundError:
            raise RuntimeError(f"ADB is not installed or not in PATH. Please set adb_path in config.json or install ADB.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("ADB command timed out")

    def _run_command(self, command: List[str]) -> tuple[bool, str]:
        try:
            adb_cmd = self._get_adb_command()
            if self.device_id:
                command = [adb_cmd, '-s', self.device_id] + command
            else:
                command = [adb_cmd] + command
            
            result = subprocess.run(command, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=self.timeout)
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timed out: {' '.join(command)}"
        except Exception as e:
            return False, str(e)

    def get_devices(self) -> List[str]:
        success, output = self._run_command(['devices'])
        if not success:
            raise RuntimeError(f"Failed to get devices: {output}")
        
        devices = []
        lines = output.strip().split('\n')[1:]
        for line in lines:
            if '\tdevice' in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        return devices

    def connect(self) -> bool:
        if not self.device_id:
            devices = self.get_devices()
            if len(devices) == 0:
                raise RuntimeError("No devices found")
            elif len(devices) == 1:
                self.device_id = devices[0]
            else:
                raise RuntimeError(f"Multiple devices found: {devices}. Please specify device_id")
        
        success, output = self._run_command(['get-state'])
        if success and 'device' in output:
            print(f"Connected to device: {self.device_id}")
            return True
        else:
            raise RuntimeError(f"Failed to connect to device {self.device_id}: {output}")

    def get_device_info(self) -> dict:
        info = {}
        
        success, output = self._run_command(['shell', 'getprop', 'ro.product.model'])
        if success:
            info['model'] = output.strip()
        
        success, output = self._run_command(['shell', 'getprop', 'ro.build.version.release'])
        if success:
            info['android_version'] = output.strip()
        
        success, output = self._run_command(['shell', 'getprop', 'ro.product.manufacturer'])
        if success:
            info['manufacturer'] = output.strip()
        
        return info

    def take_photo(self, save_path: str = "/sdcard/test_photo.jpg") -> str:
        print("提示：启动相机应用，请手动拍照或按返回键退出")
        success, output = self._run_command(['shell', 'am', 'start', '-a', 
                                            'android.media.action.IMAGE_CAPTURE'])
        if not success:
            raise RuntimeError(f"Failed to start camera: {output}")
        
        print("等待拍照... (10秒后自动继续)")
        time.sleep(10)
        
        return save_path

    def take_photo_auto(self, save_path: str = "/sdcard/test_photo.jpg") -> str:
        success, output = self._run_command(['shell', 'am', 'start', '-a', 
                                            'android.media.action.IMAGE_CAPTURE'])
        if not success:
            raise RuntimeError(f"Failed to start camera: {output}")
        
        time.sleep(3)
        
        return save_path

    def pull_file(self, remote_path: str, local_path: str) -> bool:
        success, output = self._run_command(['pull', remote_path, local_path])
        if not success:
            raise RuntimeError(f"Failed to pull file: {output}")
        return True

    def push_file(self, local_path: str, remote_path: str) -> bool:
        success, output = self._run_command(['push', local_path, remote_path])
        if not success:
            raise RuntimeError(f"Failed to push file: {output}")
        return True

    def list_files(self, path: str = "/sdcard/DCIM/Camera/") -> List[str]:
        success, output = self._run_command(['shell', 'ls', '-lt', path])
        if not success:
            return []
        
        files = []
        for line in output.strip().split('\n'):
            if line and not line.startswith('.'):
                parts = line.split()
                if len(parts) >= 9:
                    filename = parts[8]
                    full_path = os.path.join(path, filename)
                    files.append(full_path)
        
        return files

    def list_files_with_time(self, path: str = "/sdcard/DCIM/Camera/") -> List[dict]:
        print(f"\n尝试获取文件列表，路径: {path}")
        
        success, output = self._run_command(['shell', 'ls', '-l', path])
        if not success:
            print(f"警告：无法列出文件: {output}")
            return []
        
        print(f"ADB输出:\n{output}")
        
        files = []
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('total') or line.startswith('.'):
                continue
            
            parts = line.split()
            if len(parts) < 1:
                continue
            
            filename = parts[-1]
            
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"  跳过非图片文件: {filename}")
                continue
            
            full_path = os.path.join(path, filename)
            
            timestamp = 'Unknown'
            if len(parts) >= 8:
                try:
                    date_str = f"{parts[5]}-{parts[6]}-{parts[7]}"
                    timestamp = f"{date_str} {parts[3]}:{parts[4]}"
                except:
                    pass
            
            files.append({
                'path': full_path,
                'name': filename,
                'timestamp': timestamp
            })
            print(f"  添加文件: {filename} (时间: {timestamp})")
        
        if files:
            print(f"\n  找到 {len(files)} 个图片文件")
        else:
            print(f"\n  路径 {path} 中没有找到图片文件")
        
        return sorted(files, key=lambda x: x['timestamp'], reverse=True)

    def get_latest_photo(self, path: str = "/sdcard/DCIM/Camera/") -> Optional[str]:
        files = self.list_files(path)
        if files:
            return files[0]
        return None

    def delete_file(self, remote_path: str) -> bool:
        success, output = self._run_command(['shell', 'rm', remote_path])
        return success

    def screen_capture(self, local_path: str) -> bool:
        temp_path = "/sdcard/screenshot.png"
        success, output = self._run_command(['shell', 'screencap', '-p', temp_path])
        if not success:
            raise RuntimeError(f"Failed to capture screen: {output}")
        
        return self.pull_file(temp_path, local_path)
