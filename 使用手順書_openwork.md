# OpenWork データ取得ツール 使用手順書

## 1. 事前準備

### 1.1 動作環境の確認
```bash
python3 --version
```
Python 3.6以上が必要です。

### 1.2 プロジェクトディレクトリの確認
```bash
ls -la
```
以下のファイルが存在することを確認してください：
- `openwork.py` - 単一企業取得スクリプト
- `openwork_batch.py` - 一括取得スクリプト
- `openwork_list.csv` - 企業リスト

### 1.3 dataフォルダの確認・作成
```bash
mkdir -p data
```

## 2. 企業リストファイルの準備

### 2.1 openwork_list.csvの形式
以下の列が必要です：
```csv
date,銘柄名,コード,業種,TOPIXに占める個別銘柄のウエイト,ニューインデックス区分,URL
```

### 2.2 サンプルデータ
```csv
date,銘柄名,コード,業種,TOPIXに占める個別銘柄のウエイト,ニューインデックス区分,URL
2025/6/30,極洋,1301,水産・農林業,0.000067,TOPIX Small 2,https://www.openwork.jp/a0910000000Fqdi/analysis/
2025/6/30,ニッスイ,1332,水産・農林業,0.000304,TOPIX Mid400,https://www.openwork.jp/a0910000000Fqdk/analysis/
```

### 2.3 重要な注意点
- **URL列**: OpenWorkのanalysisページのURLを正確に記載
- **文字エンコーディング**: UTF-8で保存
- **日付形式**: `YYYY/M/D`形式（例: `2025/6/30`）
- **ニューインデックス区分**: TOPIX分類（TOPIX Small 2、TOPIX Mid400等）を正確に記載

## 3. 単一企業データ取得（openwork.py）

### 3.1 基本的な使用方法
```bash
python3 openwork.py <企業コード>
```

### 3.2 実行例
```bash
# 極洋のデータを取得
python3 openwork.py a0910000000Fqdi
```

### 3.3 出力結果
```
企業データを取得中: a0910000000Fqdi
CSVファイルを保存しました: openwork_a0910000000Fqdi.csv
取得完了: 11件の指標データを保存しました
```

### 3.4 エラーの場合
```
エラー: a0910000000Fqdiのデータ取得に失敗しました - HTTP Error 404: Not Found
データ取得に失敗しました
```

## 4. 一括データ取得（openwork_batch.py）

### 4.1 基本的な使用方法
```bash
python3 openwork_batch.py
```

### 4.2 実行例と出力
```bash
$ python3 openwork_batch.py
OpenWork企業データ一括取得を開始します...
企業リストを読み込みました: 4社

[1/4] 処理中: 極洋
  成功: data/1301_極洋_Small2_a0910000000Fqdi.csv (110行のデータ)

[2/4] 処理中: ニッスイ
  成功: data/1332_ニッスイ_Mid400_a0910000000Fqdk.csv (110行のデータ)

[3/4] 処理中: マルハニチロ
  成功: data/1333_マルハニチロ_Mid400_a0910000000Fqdl.csv (110行のデータ)

[4/4] 処理中: ユキグニファクトリー
  成功: data/1375_ユキグニファクトリー_Small2_a0910000000Fqdp.csv (110行のデータ)

=== 処理完了 ===
成功: 4社
失敗: 0社
合計: 4社
```

### 4.3 処理時間の目安
- **1社あたり**: 約4秒（3秒待機 + 1秒処理）
- **10社**: 約40秒
- **100社**: 約7分

## 5. 出力ファイルの確認

### 5.1 ファイル一覧の確認
```bash
ls -la data/
```

### 5.2 ファイル名の形式
`コード_銘柄名_ニューインデックス区分_企業コード.csv`

例：
- `1301_極洋_Small2_a0910000000Fqdi.csv`
- `1332_ニッスイ_Mid400_a0910000000Fqdk.csv`
- `2914_日本たばこ産業_Core30_a0910000000FqqJ.csv`

**ニューインデックス区分の処理:**
- TOPIXプレフィックスを除去: `TOPIX Small 2` → `Small 2`
- 空白を除去: `Small 2` → `Small2`

### 5.3 CSVファイルの内容確認
```bash
head -5 data/1301_極洋_Small2_a0910000000Fqdi.csv
```

出力例：
```csv
date,銘柄名,コード,ニューインデックス区分,企業コード,年,指標名,スコア
2025/6/30,極洋,1301,TOPIX Small 2,a0910000000Fqdi,2016,クチコミ総合評価,2.85
2025/6/30,極洋,1301,TOPIX Small 2,a0910000000Fqdi,2017,クチコミ総合評価,2.84
2025/6/30,極洋,1301,TOPIX Small 2,a0910000000Fqdi,2018,クチコミ総合評価,2.83
2025/6/30,極洋,1301,TOPIX Small 2,a0910000000Fqdi,2019,クチコミ総合評価,2.8
```

### 5.4 データ行数の確認
```bash
wc -l data/*.csv
```

正常な場合、各ファイルは111行（ヘッダー1行 + データ110行）になります。

## 6. トラブルシューティング

### 6.1 よくあるエラーと対処法

#### エラー1: `openwork_list.csvが見つかりません`
```bash
# 現在のディレクトリを確認
pwd
ls -la openwork_list.csv

# ファイルが存在しない場合は作成
touch openwork_list.csv
```

#### エラー2: `HTTP Error 404: Not Found`
- URLが正しいか確認
- 企業コードが存在するか確認
- OpenWorkサイトでページが表示されるか手動確認

#### エラー3: `CSV変換エラー`
- 企業にデータが存在しない可能性
- 手動でOpenWorkページを確認

#### エラー4: `Permission denied`
```bash
# dataフォルダの権限確認
ls -la data/
chmod 755 data/
```

### 6.2 実行権限の設定
```bash
chmod +x openwork.py
chmod +x openwork_batch.py
```

### 6.3 デバッグ用コマンド
```bash
# Python3が正しくインストールされているか確認
which python3

# スクリプトの構文エラーチェック
python3 -m py_compile openwork.py
python3 -m py_compile openwork_batch.py
```

## 7. 運用上の注意事項

### 7.1 サーバー負荷軽減
- 大量データ取得時は時間に余裕を持って実行
- 同時実行は避ける
- エラーが続く場合は間隔を延ばす

### 7.2 データ品質
- 最新年度のデータが`null`の場合があります
- 社員クチコミが少ない企業では一部データが不足する場合があります

### 7.3 定期実行
```bash
# cronで定期実行する場合の例
# 毎日午前2時に実行
0 2 * * * cd /path/to/openwork && python3 openwork_batch.py
```

### 7.4 ファイル管理
```bash
# 古いファイルの削除（30日より古いファイル）
find data/ -name "*.csv" -mtime +30 -delete

# ファイル数の確認
ls data/ | wc -l
```

## 8. 設定変更

### 8.1 待機時間の変更
`openwork_batch.py`の24行目を編集：
```python
self.delay_seconds = 3  # 秒数を変更
```

### 8.2 取得項目の変更
`openwork_batch.py`の27-37行目の`target_keys`を編集：
```python
self.target_keys = [
    'score.all.total',      # クチコミ総合評価
    # 必要な項目のみ残す
]
```

## 9. サポート情報

### 9.1 ログの確認
標準出力に詳細な実行ログが表示されます。問題の特定にご活用ください。

### 9.2 データの確認
出力されたCSVファイルはExcelやデータベースで読み込み可能です。

### 9.3 バックアップ推奨
取得したデータは定期的にバックアップすることを推奨します。