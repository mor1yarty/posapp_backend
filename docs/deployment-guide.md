# デプロイガイド

## 概要
POSアプリのクラウドDBハイブリッド構成でのデプロイ手順を説明します。

## アーキテクチャ概要
```
フロントエンド (Next.js)
    ↓
┌─────────────────┬─────────────────┐
│ Edge Functions  │ FastAPI        │
│ (クラウドDB)    │ (クラウドApp   │
│                 │  Service)      │
└─────────────────┴─────────────────┘
    ↓
クラウド PostgreSQL Database
```

## デプロイ対象

### 1. クラウドDB Edge Functions
- `health`: ヘルスチェック機能
- `product-simple`: 商品検索（簡易版）

### 2. FastAPI (クラウドApp Service)
- `GET /products/{code}`: 商品検索（完全版）
- `POST /purchase`: 購入処理
- `GET /health`: ヘルスチェック（FastAPI版）

### 3. クラウドDatabase
- PostgreSQLデータベース
- 3テーブル: prd_master, trd, trd_dtl

## Edge Functions デプロイ

### 前提条件
- クラウドDB CLIのインストール
- クラウドDBプロジェクトへのアクセス権

### デプロイ手順
```bash
# 1. クラウドDB CLIでログイン
cloud-db login

# 2. プロジェクトとリンク
cloud-db link --project-ref [your-project-id]

# 3. Edge Functions デプロイ
cloud-db functions deploy health
cloud-db functions deploy product-simple

# 4. 動作確認
curl https://[your-project-id].example.co/functions/v1/health
curl https://[your-project-id].example.co/functions/v1/product-simple/4901427401234
```

### Edge Functions URL
- Health Check: `https://[your-project-id].example.co/functions/v1/health`
- Product Simple: `https://[your-project-id].example.co/functions/v1/product-simple/{code}`

## FastAPI (クラウドApp Service) デプロイ

### 前提条件
- クラウドCLIのインストール
- クラウドApp Serviceリソース

### 環境変数設定
クラウドApp Serviceで以下の環境変数を設定：

```bash
CLOUD_DB_URL=https://[your-project-id].example.co
CLOUD_DB_KEY=your-api-key
CLOUD_DB_PASSWORD=your-db-password
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### デプロイ手順
```bash
# 1. src/ディレクトリに移動
cd cloud-db/src

# 2. requirements.txt確認
cat requirements.txt

# 3. クラウドApp Serviceにデプロイ
cloud-cli webapp up --name your-app-name --resource-group your-resource-group

# 4. 動作確認
curl https://your-app-name.cloudservice.net/health
curl https://your-app-name.cloudservice.net/products/4901427401234
```

## データベース確認

### クラウドDBコンソールでの確認
1. https://clouddb.example.com/dashboard/project/[your-project-id]
2. Table Editorでテーブル確認
3. SQL Editorでデータ確認

### CLI経由での確認
```sql
-- 商品マスター確認
SELECT * FROM prd_master;

-- 取引データ確認
SELECT * FROM trd ORDER BY datetime DESC LIMIT 5;

-- 取引詳細確認
SELECT * FROM trd_dtl ORDER BY trd_id DESC LIMIT 10;
```

## API動作テスト

### Edge Functions テスト
```bash
# ヘルスチェック
curl https://[your-project-id].example.co/functions/v1/health

# 商品検索（簡易版）
curl https://[your-project-id].example.co/functions/v1/product-simple/4901427401234
```

### FastAPI テスト
```bash
# ヘルスチェック
curl https://your-app-name.cloudservice.net/health

# 商品検索（完全版）
curl https://your-app-name.cloudservice.net/products/4901427401234

# 購入処理
curl -X POST https://your-app-name.cloudservice.net/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "product_code": "4901427401234",
        "product_name": "ペットボトル緑茶",
        "product_price": 150
      }
    ]
  }'
```

## パフォーマンス監視

### Edge Functions
- クラウドDB Dashboardの Function Metrics
- レスポンス時間とエラー率を監視

### FastAPI
- クラウドApp Insightsで監視
- メトリクス: レスポンス時間、エラー率、リクエスト数

### データベース
- クラウドDB Dashboard の Database監視
- 接続数、クエリ実行時間を確認

## トラブルシューティング

### よくある問題

#### Edge Functions
1. **CORS エラー**
   - corsHeaders設定を確認
   - OPTIONSリクエスト処理を確認

2. **データベース接続エラー**
   - CLOUD_DB_URL, CLOUD_DB_KEY環境変数を確認
   - Row Level Securityの設定を確認

#### FastAPI
1. **PostgreSQL接続エラー**
   - DATABASE_URL形式を確認
   - CLOUD_DB_PASSWORD設定を確認

2. **SQLAlchemy エラー**
   - テーブル名、カラム名の大文字小文字を確認
   - PostgreSQL固有の機能との互換性を確認

## セキュリティ考慮事項

### API キー管理
- 本番環境では適切なキー管理
- 環境変数での安全な設定

### CORS設定
- 本番フロントエンドURLの適切な設定
- 不要なオリジンの除外

### データベースセキュリティ
- Row Level Security (RLS) の適用検討
- 適切なユーザー権限設定

## 監視とメンテナンス

### 定期確認項目
- [ ] API レスポンス時間
- [ ] データベース接続状況
- [ ] エラーログ確認
- [ ] セキュリティアップデート

### バックアップ
- クラウドDBの自動バックアップ機能を活用
- 重要データの定期エクスポート