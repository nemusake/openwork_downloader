# OpenWorkデータ取得プロジェクト 引継ぎ用SOW

## プロジェクト概要

### プロジェクト名
OpenWork企業データ自動取得システム

### プロジェクト目的
- OpenWorkのウェブサイトから企業の分析データを自動取得
- CSV形式でのデータ保存・管理
- 研究・分析用途での企業情報収集

### 開発期間
- 開発完了済み（2025年8月）
- 実運用開始可能状態

## 技術仕様

### 開発環境
- **言語**: Python 3.6以上
- **ライブラリ**: 標準ライブラリのみ使用（ポータビリティ重視）
- **外部依存**: なし（uvなどのパッケージマネージャ不要）

### システム構成
```
openwork_downloader/
├── openwork.py                     # 単一企業データ取得スクリプト
├── openwork_batch.py              # 一括データ取得スクリプト
├── openwork_list.csv              # 企業リスト（493社分データ）
├── codelist.csv                   # 企業コード一覧
├── data/                          # 出力CSVファイル（493ファイル）
├── claude.md                      # プロジェクト設定
├── openwork_README.md             # システム技術仕様書
├── 使用手順書_openwork.md         # 詳細操作マニュアル
└── sow.md                         # 本書（引継ぎ用SOW）
```

### データ取得項目（11項目）
1. クチコミ総合評価
2. 待遇面の満足度
3. 社員の士気
4. 風通しの良さ
5. 社員の相互尊重
6. 20代成長環境
7. 人材の長期育成
8. 法令順守意識
9. 人事評価の適正感
10. 有給休暇消化率
11. 残業時間(月間)

### 出力仕様
- **ファイル形式**: CSV（UTF-8 BOM付き）
- **命名規則**: `コード_銘柄名_ニューインデックス区分_企業コード.csv`
- **データ形式**: 正規化形式（各年・各指標が1行）
- **データ期間**: 2016年～2025年（10年分）
- **データ量**: 1企業あたり110行（11指標×10年）

## 完成済み機能

### ✅ 実装完了済み
- [x] 単一企業データ取得機能（openwork.py）
- [x] 一括企業データ取得機能（openwork_batch.py）
- [x] 企業リスト管理システム
- [x] CSVデータ出力機能
- [x] エラーハンドリング
- [x] サーバー負荷軽減機能（3秒間隔制御）
- [x] 進捗表示機能
- [x] ログ出力機能
- [x] データ正規化機能

### ✅ データ取得完了済み
- [x] 493社分のデータ取得完了
- [x] 全データファイルCSV形式で保存済み
- [x] データ品質確認済み

## 引継ぎ事項

### 1. Gitリポジトリ管理
```bash
# 現在の状態
cd ~/workspace/openwork_downloader
git status  # 初期化済み（.gitディレクトリ存在）

# 推奨初回コミット手順
git add .
git commit -m "Initial commit: OpenWork data scraping system

- Complete data scraping system for 493 companies
- Standard Python libraries only (no external dependencies)
- CSV output format with normalized data structure
- Error handling and server load management
- 11 metrics × 10 years data collection

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# GitHub上のリモートリポジトリとの連携
git remote add origin https://github.com/your-account/openwork-downloader.git
git push -u origin main
```

### 2. プロジェクト削除計画
**元プロジェクト削除前チェックリスト:**
- [ ] 新プロジェクトでのデータ動作確認完了
- [ ] GitHubへのpush完了確認
- [ ] バックアップ取得完了
- [ ] 関係者への引継ぎ完了通知

```bash
# 元プロジェクトの削除（引継ぎ完了後に実行）
rm -rf /home/jptyf/workspace/openwork
```

### 3. 運用推奨事項

#### 定期実行設定
```bash
# cron設定例（月次実行）
0 2 1 * * cd /home/jptyf/workspace/openwork_downloader && python3 openwork_batch.py >> logs/batch_$(date +\%Y\%m).log 2>&1
```

#### データ管理
```bash
# データサイズ確認
du -sh data/  # 約6.3MB

# ファイル数確認
ls data/ | wc -l  # 493ファイル

# バックアップスクリプト例
tar -czf backup/openwork_data_$(date +%Y%m%d).tar.gz data/
```

### 4. システム拡張ポイント

#### 拡張可能機能
- [ ] 企業リストの自動更新機能
- [ ] データベース連携機能
- [ ] API化対応
- [ ] リアルタイム更新機能
- [ ] データ可視化機能

#### 設定変更箇所
```python
# openwork_batch.py
self.delay_seconds = 3  # リクエスト間隔（秒）

# 取得対象指標の変更
self.target_keys = [
    'score.all.total',      # 必要に応じて追加/削除
    # ...
]
```

### 5. トラブルシューティング

#### よくある問題と解決方法
- **ネットワークエラー**: リクエスト間隔を延長（delay_secondsを増やす）
- **データ取得失敗**: 企業URLの確認、OpenWorkサイトの仕様変更チェック
- **CSVファイルエラー**: 文字エンコーディングの確認（UTF-8 BOM）

#### ログ確認方法
```bash
# 実行時ログ確認
python3 openwork_batch.py 2>&1 | tee logs/execution.log

# エラーログ分析
grep "エラー" logs/execution.log
```

## ドキュメント参照

### 技術仕様
- `openwork_README.md` - システム全体の技術仕様書
- `claude.md` - プロジェクト方針・設定

### 操作マニュアル
- `使用手順書_openwork.md` - 詳細な操作手順とトラブルシューティング

### データファイル
- `openwork_list.csv` - 企業リスト（493社）
- `codelist.csv` - 企業コード一覧
- `data/` - 取得済みデータ（493ファイル）

## 引継ぎ完了チェックリスト

- [ ] システム動作確認完了
- [ ] Gitコミット・push完了
- [ ] ドキュメント確認完了
- [ ] データ整合性確認完了
- [ ] 運用方針決定完了
- [ ] 元プロジェクト削除実行

## 連絡先・サポート

### システム開発者
- **開発者**: Claude (AI Assistant)
- **開発期間**: 2025年8月
- **開発方針**: ポータビリティ重視、標準ライブラリのみ使用

### 引継ぎ日
- **引継ぎ日**: 2025年8月31日
- **プロジェクト状態**: 実運用可能
- **データ取得状況**: 完了（493社分）

---

**注意事項**: 
- このシステムは研究・教育目的での使用を前提としています
- 商用利用時はOpenWorkの利用規約を確認してください
- サーバー負荷軽減のため、適切な間隔での実行をお願いします