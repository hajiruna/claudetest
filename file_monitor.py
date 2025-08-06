#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル監視システム - メインモジュール
指定されたディレクトリの変更を監視し、定時（6時、10時、14時、17時）にレポートを表示します。
"""

import os
import sys
import time
import datetime
import threading
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


@dataclass
class ChangeRecord:
    """変更記録を格納するデータクラス"""
    timestamp: datetime.datetime
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    path: str
    is_directory: bool
    old_path: str = None  # 移動/リネーム時の旧パス


class FileMonitorHandler(FileSystemEventHandler):
    """ファイルシステムイベントハンドラー"""
    
    def __init__(self):
        super().__init__()
        self.changes = defaultdict(list)
        self.lock = threading.Lock()
    
    def on_created(self, event: FileSystemEvent):
        """ファイル・ディレクトリ作成時"""
        self._record_change('created', event.src_path, event.is_directory)
    
    def on_modified(self, event: FileSystemEvent):
        """ファイル・ディレクトリ変更時"""
        if not event.is_directory:  # ディレクトリの変更は除外（頻繁すぎるため）
            self._record_change('modified', event.src_path, event.is_directory)
    
    def on_deleted(self, event: FileSystemEvent):
        """ファイル・ディレクトリ削除時"""
        self._record_change('deleted', event.src_path, event.is_directory)
    
    def on_moved(self, event: FileSystemEvent):
        """ファイル・ディレクトリ移動/リネーム時"""
        self._record_change('moved', event.dest_path, event.is_directory, event.src_path)
    
    def _record_change(self, event_type: str, path: str, is_directory: bool, old_path: str = None):
        """変更を記録"""
        with self.lock:
            change = ChangeRecord(
                timestamp=datetime.datetime.now(),
                event_type=event_type,
                path=path,
                is_directory=is_directory,
                old_path=old_path
            )
            # 日付キーで分類
            date_key = change.timestamp.strftime('%Y-%m-%d')
            self.changes[date_key].append(change)
    
    def get_changes_since_last_report(self, last_report_time: datetime.datetime) -> List[ChangeRecord]:
        """前回のレポート以降の変更を取得"""
        with self.lock:
            all_changes = []
            for date_changes in self.changes.values():
                for change in date_changes:
                    if change.timestamp > last_report_time:
                        all_changes.append(change)
            return sorted(all_changes, key=lambda x: x.timestamp)
    
    def clear_old_changes(self, days_to_keep: int = 7):
        """古い変更記録を削除（メモリ節約）"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        with self.lock:
            dates_to_remove = []
            for date_str in self.changes:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                if date_obj < cutoff_date:
                    dates_to_remove.append(date_str)
            
            for date_str in dates_to_remove:
                del self.changes[date_str]


class FileMonitor:
    """ファイル監視メインクラス"""
    
    # 監視対象パス
    WATCH_PATH = r"M:\北日本カンパニー\間接部門\セントラルオフィス・物流部\セントラルオフィス課\100_システムチーム\03_UserLocal"
    
    # レポート時刻
    REPORT_HOURS = [6, 10, 14, 17]
    
    def __init__(self):
        self.observer = None
        self.handler = FileMonitorHandler()
        self.last_report_time = datetime.datetime.now()
        self.running = False
        self.report_thread = None
        
    def start(self):
        """監視開始"""
        # 監視パスの存在確認
        if not os.path.exists(self.WATCH_PATH):
            print(f"エラー: 監視対象パスが存在しません: {self.WATCH_PATH}")
            return False
        
        # 既に実行中の場合
        if self.running:
            print("監視は既に実行中です。")
            return False
        
        try:
            # Observer設定
            self.observer = Observer()
            self.observer.schedule(self.handler, self.WATCH_PATH, recursive=True)
            
            # 監視開始
            self.observer.start()
            self.running = True
            
            print(f"ファイル監視を開始しました: {self.WATCH_PATH}")
            print(f"レポート時刻: {', '.join([f'{h}:00' for h in self.REPORT_HOURS])}")
            print("停止するには stop_monitor.bat を実行してください。")
            
            # レポートスレッド開始
            self.report_thread = threading.Thread(target=self._report_scheduler, daemon=True)
            self.report_thread.start()
            
            # メインループ
            self._main_loop()
            
        except KeyboardInterrupt:
            print("\nキーボード割り込みにより監視を停止します。")
        except Exception as e:
            print(f"エラー: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """監視停止"""
        if not self.running:
            return
        
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        print("ファイル監視を停止しました。")
    
    def _main_loop(self):
        """メインループ"""
        while self.running:
            # ネットワークドライブ接続確認（5分毎）
            if not os.path.exists(self.WATCH_PATH):
                print(f"警告: 監視対象パスへの接続が切れています: {self.WATCH_PATH}")
                print("接続復旧を待機中...")
                
                # 接続復旧を待つ
                while self.running and not os.path.exists(self.WATCH_PATH):
                    time.sleep(30)  # 30秒毎に確認
                
                if self.running:
                    print("接続が復旧しました。監視を継続します。")
            
            # 古い変更記録を削除（メモリ節約）
            self.handler.clear_old_changes()
            
            time.sleep(300)  # 5分毎にチェック
    
    def _report_scheduler(self):
        """定時レポートスケジューラー"""
        while self.running:
            now = datetime.datetime.now()
            
            # 次のレポート時刻を計算
            next_report = self._get_next_report_time(now)
            
            # 次のレポート時刻まで待機
            wait_seconds = (next_report - now).total_seconds()
            if wait_seconds > 0:
                time.sleep(min(wait_seconds, 60))  # 最大1分で再チェック
                continue
            
            # レポート実行
            self._generate_report()
            
            # 次の分まで待機（重複実行防止）
            time.sleep(61)
    
    def _get_next_report_time(self, current_time: datetime.datetime) -> datetime.datetime:
        """次のレポート時刻を取得"""
        current_date = current_time.date()
        current_hour = current_time.hour
        
        # 今日の残りのレポート時刻をチェック
        for hour in self.REPORT_HOURS:
            if hour > current_hour:
                return datetime.datetime.combine(current_date, datetime.time(hour, 0))
        
        # 今日のレポート時刻がすべて過ぎている場合、明日の最初のレポート時刻
        tomorrow = current_date + datetime.timedelta(days=1)
        return datetime.datetime.combine(tomorrow, datetime.time(self.REPORT_HOURS[0], 0))
    
    def _generate_report(self):
        """定時レポート生成・表示"""
        current_time = datetime.datetime.now()
        changes = self.handler.get_changes_since_last_report(self.last_report_time)
        
        print("\n" + "="*70)
        print(f"【定時レポート】 {current_time.strftime('%Y年%m月%d日 %H:%M')}")
        print("="*70)
        
        if not changes:
            print("変化なし")
        else:
            print(f"検出された変更: {len(changes)}件")
            print("-" * 50)
            
            # 変更タイプ別に分類
            by_type = defaultdict(list)
            for change in changes:
                by_type[change.event_type].append(change)
            
            # 各タイプの変更を表示
            type_names = {
                'created': '新規作成',
                'modified': '更新',
                'deleted': '削除',
                'moved': '移動・リネーム'
            }
            
            for event_type, type_changes in by_type.items():
                print(f"\n■ {type_names.get(event_type, event_type)} ({len(type_changes)}件)")
                for change in type_changes:
                    time_str = change.timestamp.strftime('%m/%d %H:%M')
                    type_str = "フォルダ" if change.is_directory else "ファイル"
                    
                    if change.event_type == 'moved':
                        print(f"  {time_str} [{type_str}] {change.old_path} → {change.path}")
                    else:
                        print(f"  {time_str} [{type_str}] {change.path}")
        
        print("="*70)
        
        # 前回レポート時刻を更新
        self.last_report_time = current_time


def main():
    """メイン関数"""
    monitor = FileMonitor()
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n監視を停止しています...")
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()