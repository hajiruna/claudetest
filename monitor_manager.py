#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル監視システム - プロセス管理モジュール
監視プロセスの開始、停止、状態確認を管理します。
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import Optional

import psutil


class MonitorManager:
    """監視プロセス管理クラス"""
    
    PID_FILE = "file_monitor.pid"
    SCRIPT_NAME = "file_monitor.py"
    
    def __init__(self):
        self.script_path = Path(__file__).parent / self.SCRIPT_NAME
        self.pid_file = Path(__file__).parent / self.PID_FILE
    
    def start_monitor(self) -> bool:
        """監視プロセスを開始"""
        # 既存プロセス確認
        existing_pid = self._get_running_pid()
        if existing_pid:
            if self._is_process_running(existing_pid):
                print(f"監視プロセスは既に実行中です (PID: {existing_pid})")
                return False
            else:
                # PIDファイルはあるがプロセスが存在しない場合
                print("古いPIDファイルを削除します。")
                self._remove_pid_file()
        
        # スクリプト存在確認
        if not self.script_path.exists():
            print(f"エラー: 監視スクリプトが見つかりません: {self.script_path}")
            return False
        
        try:
            # Python環境でスクリプトを実行
            # uvの仮想環境を使用
            uv_cmd = ["uv", "run", "python", str(self.script_path)]
            
            print("ファイル監視プロセスを開始しています...")
            
            # バックグラウンドで実行
            if os.name == 'nt':  # Windows
                # Windowsの場合、新しいコンソールウィンドウで実行
                process = subprocess.Popen(
                    uv_cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=Path(__file__).parent
                )
            else:  # Unix/Linux
                process = subprocess.Popen(
                    uv_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=Path(__file__).parent
                )
            
            # PIDファイル作成
            self._write_pid_file(process.pid)
            
            # プロセス起動確認
            time.sleep(2)
            if self._is_process_running(process.pid):
                print(f"ファイル監視を開始しました (PID: {process.pid})")
                print("停止するには stop_monitor.bat を実行してください。")
                return True
            else:
                print("エラー: プロセスの起動に失敗しました。")
                self._remove_pid_file()
                return False
                
        except Exception as e:
            print(f"エラー: プロセス起動に失敗しました: {e}")
            self._remove_pid_file()
            return False
    
    def stop_monitor(self) -> bool:
        """監視プロセスを停止"""
        pid = self._get_running_pid()
        if not pid:
            print("監視プロセスは実行されていません。")
            return False
        
        if not self._is_process_running(pid):
            print("監視プロセスは既に停止しています。")
            self._remove_pid_file()
            return False
        
        try:
            # プロセス終了
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], 
                             capture_output=True, check=False)
            else:  # Unix/Linux
                os.kill(pid, signal.SIGTERM)
            
            # 終了確認（最大10秒待機）
            for _ in range(10):
                time.sleep(1)
                if not self._is_process_running(pid):
                    break
            else:
                # 強制終了
                if os.name == 'nt':
                    subprocess.run(["taskkill", "/PID", str(pid), "/F"], 
                                 capture_output=True, check=False)
                else:
                    os.kill(pid, signal.SIGKILL)
            
            self._remove_pid_file()
            print(f"ファイル監視を停止しました (PID: {pid})")
            return True
            
        except Exception as e:
            print(f"エラー: プロセス停止に失敗しました: {e}")
            return False
    
    def check_status(self) -> None:
        """監視プロセスの状態を確認"""
        print("=" * 50)
        print("ファイル監視システム 状態確認")
        print("=" * 50)
        
        pid = self._get_running_pid()
        if not pid:
            print("ステータス: 停止中")
            print("PIDファイル: なし")
            return
        
        if self._is_process_running(pid):
            try:
                process = psutil.Process(pid)
                print(f"ステータス: 実行中")
                print(f"PID: {pid}")
                print(f"開始時刻: {process.create_time()}")
                print(f"CPU使用率: {process.cpu_percent():.1f}%")
                print(f"メモリ使用量: {process.memory_info().rss / 1024 / 1024:.1f} MB")
                
                # 監視対象パスの存在確認
                watch_path = r"M:\北日本カンパニー\間接部門\セントラルオフィス・物流部\セントラルオフィス課\100_システムチーム\03_UserLocal"
                if os.path.exists(watch_path):
                    print(f"監視対象パス: 接続中")
                else:
                    print(f"監視対象パス: 接続切断")
                
            except psutil.NoSuchProcess:
                print("ステータス: プロセス情報取得失敗")
                self._remove_pid_file()
        else:
            print("ステータス: 停止中（PIDファイルのみ残存）")
            self._remove_pid_file()
        
        print("=" * 50)
    
    def _get_running_pid(self) -> Optional[int]:
        """実行中のプロセスPIDを取得"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r', encoding='utf-8') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return None
    
    def _write_pid_file(self, pid: int) -> None:
        """PIDファイルを作成"""
        try:
            with open(self.pid_file, 'w', encoding='utf-8') as f:
                f.write(str(pid))
        except IOError as e:
            print(f"警告: PIDファイルの作成に失敗しました: {e}")
    
    def _remove_pid_file(self) -> None:
        """PIDファイルを削除"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except IOError:
            pass
    
    def _is_process_running(self, pid: int) -> bool:
        """プロセスが実行中かチェック"""
        try:
            return psutil.pid_exists(pid)
        except:
            return False


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用法: python monitor_manager.py [start|stop|status]")
        return
    
    command = sys.argv[1].lower()
    manager = MonitorManager()
    
    if command == "start":
        manager.start_monitor()
    elif command == "stop":
        manager.stop_monitor()
    elif command == "status":
        manager.check_status()
    else:
        print("無効なコマンドです。start, stop, status のいずれかを指定してください。")


if __name__ == "__main__":
    main()