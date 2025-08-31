#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWork企業データ取得スクリプト
Python3標準ライブラリのみを使用
"""

import urllib.request
import urllib.parse
import re
import json
import csv
import sys
from typing import Dict, List, Optional, Any


class OpenWorkScraper:
    """OpenWorkからデータを取得するクラス"""
    
    def __init__(self):
        self.base_url = "https://www.openwork.jp"
    
    def fetch_company_data(self, company_code: str) -> Optional[Dict[str, Any]]:
        """
        企業コードから企業データを取得
        
        Args:
            company_code: 企業コード（例: a0910000000Fqdi）
            
        Returns:
            取得したデータ辞書、失敗時はNone
        """
        url = f"{self.base_url}/{company_code}/analysis/"
        
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
                data['company_code'] = company_code
                
            return data
            
        except Exception as e:
            print(f"エラー: {company_code}のデータ取得に失敗しました - {e}")
            return None
    
    def _extract_getdata_json(self, html_content: str) -> Optional[Dict[str, Any]]:
        """HTMLからgetData()関数のJSONデータを抽出"""
        try:
            # getData()関数の戻り値を正規表現で抽出
            pattern = r'function getData\(\)\s*\{\s*return\s*({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                print("getData()関数が見つかりませんでした")
                return None
                
            json_str = match.group(1)
            # JavaScriptのコメントを除去
            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
            
            # JSONパース
            data = json.loads(json_str)
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return None
        except Exception as e:
            print(f"データ抽出エラー: {e}")
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
    
    def convert_to_csv_rows(self, data: Dict[str, Any]) -> List[List[str]]:
        """
        取得データをCSV行形式に変換（残業時間までの項目のみ）
        
        Returns:
            CSV行のリスト（ヘッダー行含む）
        """
        if not data or 'xAxis' not in data or 'yAxis' not in data:
            return []
        
        # 残業時間までの項目のみを対象とする
        target_keys = [
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
        
        # ヘッダー行を作成
        years = data['xAxis']
        headers = ['企業名', '企業コード', '指標名', '単位'] + [str(year) for year in years]
        
        rows = [headers]
        
        # 指定した項目のデータを順番に行として追加
        for key in target_keys:
            if key in data['yAxis']:
                metric_data = data['yAxis'][key]
                row = [
                    data.get('company_name', '不明'),
                    data.get('company_code', '不明'),
                    metric_data.get('name', key),
                    metric_data.get('unit', '')
                ]
                
                # 各年のデータを追加
                metric_values = metric_data.get('data', [])
                for i, year in enumerate(years):
                    if i < len(metric_values):
                        value = metric_values[i]
                        row.append(str(value) if value is not None else '')
                    else:
                        row.append('')
                
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
            
            print(f"CSVファイルを保存しました: {filename}")
            return True
            
        except Exception as e:
            print(f"CSV保存エラー: {e}")
            return False


def main():
    """メイン処理"""
    if len(sys.argv) != 2:
        print("使用方法: python openwork_scraper.py <企業コード>")
        print("例: python openwork_scraper.py a0910000000Fqdi")
        sys.exit(1)
    
    company_code = sys.argv[1]
    
    # データ取得
    scraper = OpenWorkScraper()
    print(f"企業データを取得中: {company_code}")
    
    data = scraper.fetch_company_data(company_code)
    if not data:
        print("データ取得に失敗しました")
        sys.exit(1)
    
    # CSV変換
    rows = scraper.convert_to_csv_rows(data)
    if not rows:
        print("CSV変換に失敗しました")
        sys.exit(1)
    
    # CSV保存
    output_filename = f"openwork_{company_code}.csv"
    success = scraper.save_to_csv(rows, output_filename)
    
    if success:
        print(f"取得完了: {len(rows)-1}件の指標データを保存しました")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()