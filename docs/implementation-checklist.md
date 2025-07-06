# 実装チェックリスト

## Phase 1: git worktree環境構築 ✅

- [x] main/ディレクトリ作成と既存ファイル移動
- [x] supabase-migrationブランチ作成
- [x] supabase/worktree設定
- [x] ディレクトリ構造作成（src, docs, supabase/functions）
- [x] プロジェクトドキュメント作成開始

## Phase 2: データベース移行

### Supabaseスキーマ作成
- [ ] PRD_MASTER テーブル作成
- [ ] TRD テーブル作成
- [ ] TRD_DTL テーブル作成
- [ ] インデックス設定
- [ ] 外部キー制約設定

### サンプルデータ移行
- [ ] 既存MySQLデータの確認
- [ ] PostgreSQL用データ変換
- [ ] Supabaseへのデータインサート
- [ ] データ整合性確認

## Phase 3: Edge Functions実装

### GET /health
- [ ] supabase/functions/health/index.ts 作成
- [ ] 基本レスポンス実装
- [ ] タイムスタンプ追加
- [ ] Supabaseへのデプロイ
- [ ] 動作確認

### GET /products/{code} (簡易版)
- [ ] supabase/functions/product-simple/index.ts 作成
- [ ] URL パラメータ解析
- [ ] Supabaseクライアント設定
- [ ] データベース検索実装
- [ ] レスポンス形成
- [ ] エラーハンドリング
- [ ] デプロイと動作確認

## Phase 4: FastAPI Supabase対応

### 環境設定
- [ ] src/requirements.txt にsupabase-py追加
- [ ] src/requirements.txt にpsycopg2追加
- [ ] 環境変数設定（SUPABASE_URL, SUPABASE_KEY）

### database.py修正
- [ ] PostgreSQL接続文字列変更
- [ ] Supabase認証情報設定
- [ ] SQLAlchemy設定調整
- [ ] 接続テスト

### API実装
- [ ] GET /products/{code} (完全版) 移植
- [ ] POST /purchase 移植
- [ ] 税計算ロジック確認
- [ ] エラーハンドリング確認
- [ ] ログ設定調整

### 動作確認
- [ ] ローカル環境での動作テスト
- [ ] 商品検索機能テスト
- [ ] 購入処理テスト
- [ ] エラーケースのテスト

## Phase 5: デプロイと検証

### Edge Functions
- [ ] Supabase CLIを使用したデプロイ
- [ ] 本番環境での動作確認
- [ ] パフォーマンステスト

### FastAPI
- [ ] Azure App Service設定更新
- [ ] 環境変数設定
- [ ] デプロイと動作確認
- [ ] 既存フロントエンドとの連携確認

### 総合テスト
- [ ] 全エンドポイントの動作確認
- [ ] レスポンス時間測定
- [ ] エラー処理の確認
- [ ] 負荷テスト（軽量）

## Phase 6: ドキュメント完成

- [ ] api-comparison.md 作成
- [ ] deployment-guide.md 作成
- [ ] worktree-guide.md 作成
- [ ] migration-report.md 作成

## 検証項目

### 機能検証
- [ ] 商品マスター検索の正確性
- [ ] 購入処理のトランザクション整合性
- [ ] 税計算の精度確認
- [ ] エラーレスポンスの一貫性

### パフォーマンス検証
- [ ] Edge Functions vs FastAPI レスポンス時間比較
- [ ] MySQL vs PostgreSQL パフォーマンス比較
- [ ] 同時接続数テスト

### セキュリティ検証
- [ ] Supabase認証の確認
- [ ] データベースアクセス権限の確認
- [ ] API エンドポイントのセキュリティ

## トラブルシューティング

### よくある問題
- [ ] PostgreSQL接続エラーの対処法記録
- [ ] Edge Functions デプロイエラーの対処法記録
- [ ] 型変換エラーの対処法記録

### 備考
- 各フェーズ完了時にgitコミットを実行
- 問題発生時は即座にチェックリストに記録
- 完了項目は ✅ マークで明示