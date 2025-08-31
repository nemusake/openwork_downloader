#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWork企業データ一括取得スクリプト
openwork_list.csvから複数企業のデータを取得して個別CSVファイルに保存

実行コマンド
python3 openwork_batch.py
"""

import urllib.request
import urllib.parse
import re
import json
import csv
import sys
import os
import time
from typing import Dict, List, Optional, Any, Tuple


class OpenWorkBatchScraper:
    """OpenWorkから複数企業のデータを一括取得するクラス"""
    
    def __init__(self):
        self.base_url = "https://www.openwork.jp"
        self.delay_seconds = 3  # リクエスト間隔（秒）
        
        # 残業時間までの項目のみを対象とする
        self.target_keys = [
            'score.all.total',      # クチコミ総合評価
            'score.all.satisfy',    # 待遇面の満足度
            'score.all.spirit',     # 社員の士気
            'score.all.airy',       # 風通しの良さ
            'score.all.team',       # 社員の相互尊重
            'score.all.junior',     # 20代成長環境
            'score.all.senior',     # 人材の長期育成
            'score.all.law',        # 法令順守意識
            'score.all.assess',     # 人事評価の適正感
            'score.all.withpay',    # 有給休暇消化率
            'score.all.overtime'    # 残業時間(月間)
        ]
    
    def load_company_list(self, csv_filename: str) -> List[Dict[str, str]]:
        """
        企業リストCSVファイルを読み込み
        
        Args:
            csv_filename: CSVファイル名
            
        Returns:
            企業情報の辞書リスト
        """
        companies = []
        
        try:
            with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('URL'):  # URLが存在する行のみ
                        companies.append(row)
            
            print(f"企業リストを読み込みました: {len(companies)}社")
            return companies
            
        except Exception as e:
            print(f"企業リスト読み込みエラー: {e}")
            return []
    
    def extract_company_code_from_url(self, url: str) -> Optional[str]:
        """
        URLから企業コードを抽出
        
        Args:
            url: OpenWorkのURL
            
        Returns:
            企業コード（例: a0910000000Fqdi）
        """
        try:
            # URLから企業コードを抽出（/で区切られた部分）
            pattern = r'/([a-zA-Z0-9]+)/analysis/?'
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None
            
        except Exception:
            return None
    
    def fetch_company_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        企業URLから企業データを取得
        
        Args:
            url: 企業ページのURL
            
        Returns:
            取得したデータ辞書、失敗時はNone
        """
        try:
            # HTTPリクエスト送信
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                html_content = response.read().decode('utf-8')
                
            # getData()関数からJSONデータを抽出
            data = self._extract_getdata_json(html_content)
            if data:
                # 企業名も抽出
                company_name = self._extract_company_name(html_content)
                data['company_name'] = company_name
                
            return data
            
        except Exception as e:
            print(f"エラー: {url}のデータ取得に失敗しました - {e}")
            return None
    
    def _extract_getdata_json(self, html_content: str) -> Optional[Dict[str, Any]]:
        """HTMLからgetData()関数のJSONデータを抽出"""
        try:
            # getData()関数の戻り値を正規表現で抽出
            pattern = r'function getData\(\)\s*\{\s*return\s*({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                return None
                
            json_str = match.group(1)
            # JavaScriptのコメントを除去
            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
            
            # JSONパース
            data = json.loads(json_str)
            return data
            
        except Exception:
            return None
    
    def _extract_company_name(self, html_content: str) -> str:
        """HTMLから企業名を抽出"""
        try:
            # titleタグから企業名を抽出
            title_match = re.search(r'<title>([^「]+)', html_content)
            if title_match:
                return title_match.group(1).strip()
            
            # h2タグから企業名を抽出（フォールバック）
            h2_match = re.search(r'<h2[^>]*>.*?href="[^"]*">([^<]+)</a>', html_content)
            if h2_match:
                return h2_match.group(1).strip()
                
            return "不明"
            
        except Exception:
            return "不明"
    
    def convert_to_normalized_csv_rows(self, data: Dict[str, Any], 
                                      company_info: Dict[str, str]) -> List[List[str]]:
        """
        取得データを正規化されたCSV行形式に変換
        
        Args:
            data: 取得したOpenWorkデータ
            company_info: 企業情報（date, 銘柄名, コード等）
            
        Returns:
            CSV行のリスト（ヘッダー行含む）
        """
        if not data or 'xAxis' not in data or 'yAxis' not in data:
            return []
        
        # ヘッダー行
        headers = ['date', '銘柄名', 'コード', 'ニューインデックス区分', '企業コード', '年', '指標名', 'スコア']
        rows = [headers]
        
        # 企業コードをURLから抽出
        company_code = self.extract_company_code_from_url(company_info.get('URL', ''))
        
        years = data['xAxis']
        
        # 指定した項目のデータを正規化して行として追加
        for key in self.target_keys:
            if key in data['yAxis']:
                metric_data = data['yAxis'][key]
                metric_values = metric_data.get('data', [])
                metric_name = metric_data.get('name', key)
                
                # 各年のデータを個別の行として追加
                for i, year in enumerate(years):
                    if i < len(metric_values) and metric_values[i] is not None:
                        row = [
                            company_info.get('date', ''),
                            company_info.get('銘柄名', ''),
                            company_info.get('コード', ''),
                            company_info.get('ニューインデックス区分', ''),
                            company_code or '',
                            str(year),
                            metric_name,
                            str(metric_values[i])
                        ]
                        rows.append(row)
        
        return rows
    
    def save_to_csv(self, rows: List[List[str]], filename: str) -> bool:
        """
        データをUTF-8 BOM付きCSVファイルに保存
        
        Args:
            rows: CSV行データ
            filename: 出力ファイル名
            
        Returns:
            保存成功時True
        """
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            return True
            
        except Exception as e:
            print(f"CSV保存エラー ({filename}): {e}")
            return False
    
    def generate_output_filename(self, company_info: Dict[str, str]) -> str:
        """
        出力ファイル名を生成
        
        Args:
            company_info: 企業情報
            
        Returns:
            ファイル名（コード_銘柄名_ニューインデックス区分_企業コード.csv）
        """
        meigara_name = company_info.get('銘柄名', 'unknown')
        stock_code = company_info.get('コード', 'unknown')
        company_code = self.extract_company_code_from_url(company_info.get('URL', ''))
        new_index = company_info.get('ニューインデックス区分', 'unknown')
        
        # ファイル名に使えない文字を置換
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', meigara_name)
        
        # ニューインデックス区分からTOPIXを除去し、空白を除去
        if new_index and new_index != 'unknown':
            # TOPIXを除去
            clean_index = re.sub(r'^TOPIX\s*', '', new_index)
            # 空白を除去
            clean_index = re.sub(r'\s+', '', clean_index)
            # ファイル名に使えない文字を置換
            clean_index = re.sub(r'[<>:"/\\|?*]', '_', clean_index)
        else:
            clean_index = 'unknown'
        
        filename = f"{stock_code}_{safe_name}_{clean_index}_{company_code or 'unknown'}.csv"
        return os.path.join('data', filename)
    
    def process_all_companies(self, csv_filename: str) -> Tuple[int, int]:
        """
        すべての企業のデータを取得して保存
        
        Args:
            csv_filename: 企業リストCSVファイル名
            
        Returns:
            (成功件数, 失敗件数)
        """
        companies = self.load_company_list(csv_filename)
        if not companies:
            return 0, 0
        
        success_count = 0
        fail_count = 0
        
        for i, company_info in enumerate(companies, 1):
            print(f"\n[{i}/{len(companies)}] 処理中: {company_info.get('銘柄名', 'Unknown')}")
            
            url = company_info.get('URL', '')
            if not url:
                print(f"  スキップ: URLが空です")
                fail_count += 1
                continue
            
            # データ取得
            data = self.fetch_company_data(url)
            if not data:
                print(f"  失敗: データ取得エラー")
                fail_count += 1
                time.sleep(self.delay_seconds)
                continue
            
            # CSV変換
            rows = self.convert_to_normalized_csv_rows(data, company_info)
            if not rows or len(rows) <= 1:
                print(f"  失敗: CSV変換エラー")
                fail_count += 1
                time.sleep(self.delay_seconds)
                continue
            
            # ファイル保存
            output_filename = self.generate_output_filename(company_info)
            if self.save_to_csv(rows, output_filename):
                print(f"  成功: {output_filename} ({len(rows)-1}行のデータ)")
                success_count += 1
            else:
                print(f"  失敗: ファイル保存エラー")
                fail_count += 1
            
            # リクエスト間隔を空ける
            if i < len(companies):
                time.sleep(self.delay_seconds)
        
        return success_count, fail_count


def main():
    """メイン処理"""
    csv_filename = "openwork_list.csv"
    
    if not os.path.exists(csv_filename):
        print(f"エラー: {csv_filename}が見つかりません")
        sys.exit(1)
    
    # データフォルダが存在しない場合は作成
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 一括取得実行
    scraper = OpenWorkBatchScraper()
    print("OpenWork企業データ一括取得を開始します...")
    
    success_count, fail_count = scraper.process_all_companies(csv_filename)
    
    print(f"\n=== 処理完了 ===")
    print(f"成功: {success_count}社")
    print(f"失敗: {fail_count}社")
    print(f"合計: {success_count + fail_count}社")


if __name__ == "__main__":
    main()