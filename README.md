# POSアプリケーション - クラウドDB対応バックエンド (FastAPI)

モバイルPOSシステムのクラウドデータベース対応バックエンドAPI実装です。FastAPIとPostgreSQLを使用した高性能なWebAPIです。

## 技術スタック

- **フレームワーク**: FastAPI 0.104.1
- **ASGI サーバー**: Uvicorn 0.24.0
- **ORM**: SQLAlchemy 2.0.23
- **データベースドライバー**: psycopg2-binary 2.9.9
- **データベース**: PostgreSQL (クラウドホスト)
- **REST APIクライアント**: httpx 0.27.2
- **データ検証**: Pydantic 2.5.0
- **クラウドDBクライアント**: supabase 2.4.1

## 機能

### API エンドポイント

#### 商品マスタ検索
- **エンドポイント**: `GET /products/{code}`
- **機能**: JANコードによる商品情報検索
- **接続方式**: クラウドDB REST API経由（WSL環境対応）
- **レスポンス**: 商品ID、商品名、品名、色、品番、価格

#### 購入処理
- **エンドポイント**: `POST /purchase`
- **機能**: 購入データの保存
- **処理**: 取引データ(trd)と取引明細(trd_dtl)の作成
- **税額計算**: 消費税の自動計算機能（Level 2対応）

#### ヘルスチェック
- **エンドポイント**: `GET /health`
- **機能**: サーバー状態の確認

## データベース設計（Level 2対応）

### prd_master（商品マスタ）
- `prd_id`: SERIAL (主キー)
- `code`: CHAR(13) (JANコード、ユニーク)
- `product_name`: VARCHAR(50) (品名)
- `color`: VARCHAR(30) (色)
- `item_code`: VARCHAR(20) (品番)
- `name`: VARCHAR(100) (商品名)
- `price`: INTEGER (価格)

### trd（取引）Level 2拡張
- `trd_id`: SERIAL (主キー)
- `datetime`: TIMESTAMP (取引日時)
- `emp_cd`: CHAR(10) (従業員コード)
- `store_cd`: CHAR(5) (店舗コード)
- `pos_no`: CHAR(3) (POS番号)
- `total_amt`: INTEGER (合計金額)
- `ttl_amt_ex_tax`: INTEGER (合計金額・税抜) ← **Level 2追加**

### trd_dtl（取引明細）Level 2拡張
- `trd_id`: INTEGER (主キー、外部キー)
- `dtl_id`: INTEGER (主キー)
- `prd_id`: INTEGER (外部キー)
- `prd_code`: CHAR(13) (商品コード)
- `prd_name`: VARCHAR(100) (商品名)
- `prd_price`: INTEGER (商品価格)
- `tax_cd`: CHAR(2) (消費税区分) ← **Level 2追加**

## ディレクトリ構成

```
pos-app-backend-supabase/
├── src/                         # アプリケーションソース
│   ├── main.py                  # メインアプリケーション
│   ├── database.py              # Supabase設定とORMモデル
│   ├── models.py                # Pydanticモデル定義
│   ├── tax_calculator.py        # 税額計算機能
│   ├── requirements.txt         # Python依存関係
│   └── venv/                    # Python仮想環境
├── docs/                        # ドキュメント
│   ├── migration-plan.md        # 移行計画
│   ├── deployment-guide.md      # デプロイガイド
│   └── api-comparison.md        # API比較表
├── supabase/                    # Supabase Edge Functions
│   └── functions/
│       ├── health/              # ヘルスチェック関数
│       └── product-simple/      # 商品検索関数
├── supabase_server_manager.sh   # サーバー管理スクリプト
├── supabase-backend.log         # サーバーログ
└── README.md
```

## 環境設定

### 前提条件
- Python 3.11以上
- クラウドデータベースプロジェクト

### クラウドDB接続情報
- **プロジェクトURL**: https://[project-id].example.co
- **データベース**: PostgreSQL (IPv6対応)
- **認証**: API Key認証

### インストールと起動

```bash
# 1. 仮想環境の作成と有効化
cd src
python3 -m venv venv
source venv/bin/activate

# 2. 依存関係のインストール
pip install -r requirements.txt

# 3. サーバー管理スクリプトで起動
cd ..
./supabase_server_manager.sh start
```

### 環境変数設定

**開発環境（必須）**:
```bash
export CLOUD_DB_PASSWORD="your-db-password"
export ENVIRONMENT="development"
```

**本番環境（クラウドアプリサービス）**:
```bash
CLOUD_DB_PASSWORD=your-db-password
ENVIRONMENT=production
```

**オプション環境変数**（デフォルト値あり）:
```bash
CLOUD_DB_URL=https://[project-id].example.co
CLOUD_DB_KEY=your-api-key...
```

## サーバー管理

### 管理スクリプト使用方法

```bash
# サーバー起動
./supabase_server_manager.sh start

# サーバー停止
./supabase_server_manager.sh stop

# サーバー再起動
./supabase_server_manager.sh restart

# サーバー状態確認
./supabase_server_manager.sh status

# 接続テスト実行
./supabase_server_manager.sh test

# ログ表示
./supabase_server_manager.sh logs

# ポート強制解放
./supabase_server_manager.sh force-kill

# ヘルプ表示
./supabase_server_manager.sh help
```

### 手動起動

```bash
cd src
source venv/bin/activate
CLOUD_DB_PASSWORD=your-db-password ENVIRONMENT=development python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

サーバーは http://localhost:8000 で利用可能になります。

### API ドキュメント

FastAPIの自動生成ドキュメントが利用できます：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## サンプルデータ

### 文房具商品データ（30商品）

データベースには以下の文房具シリーズが登録されています：

#### サラサシリーズ（10商品）
- サラサクリップ: ¥110（ブラック/レッド/ブルー）
- サラサグランド: ¥1,320（マットブラック/ボルドーパープル）
- サラサナノ: ¥220（ブラック/レッド）
- サラサドライ、サラサR、サラサマークオン: ¥110～¥165

#### マッキーシリーズ（10商品）
- ハイマッキー: ¥165（ブラック/レッド/ブルー）
- マッキー極細: ¥132（各色）
- マッキーノック、マッキーケア、マッキー極太: ¥132～¥495

#### マイルドライナーシリーズ（10商品）
- マイルドライナー: ¥110（5色展開）
- マイルドライナーブラッシュ: ¥165（3色）
- マイルドライナーのもと: ¥935（高級タイプ）

## APIの使用例

### 商品検索

```bash
# 文房具商品検索API（サラサクリップ ブラック）
curl -X GET "http://localhost:8000/products/4901681143115"

# レスポンス例
{
  "product_id": 1,
  "product_code": "4901681143115",
  "product_name": "サラサクリップ",
  "product_price": 110,
  "color": "ブラック",
  "item_code": "JJ15-BK",
  "full_name": "サラサクリップ ブラック"
}
```

### 購入処理（Level 2対応）

```bash
# 購入処理API（税抜金額・消費税区分対応）
curl -X POST "http://localhost:8000/purchase" \
  -H "Content-Type: application/json" \
  -d '{
    "register_staff_code": "9999999999",
    "store_code": "30",
    "pos_id": "90",
    "items": [
      {
        "product_id": 1,
        "product_code": "4901681143115",
        "product_name": "サラサクリップ",
        "product_price": 110
      }
    ]
  }'

# レスポンス例
{
  "success": true,
  "total_amount": 110,
  "total_amount_ex_tax": 100,
  "tax_amount": 10,
  "transaction_id": 1,
  "message": "購入処理が正常に完了しました"
}
```

### ヘルスチェック

```bash
# ヘルスチェックAPI
curl -X GET "http://localhost:8000/health"

# レスポンス例
{"status": "healthy"}
```

## アーキテクチャ

### 技術的特徴

1. **ハイブリッド接続方式**
   - 本番環境: PostgreSQL直接接続
   - WSL環境: クラウドDB REST API経由（IPv6問題回避）

2. **Level 2税額計算対応**
   - 税抜金額自動計算
   - 消費税区分管理
   - 標準税率10%・軽減税率8%対応

3. **環境適応設計**
   - クラウドアプリサービス対応
   - WSL開発環境対応
   - 環境変数による設定管理

### レイヤー構造
1. **API層** (`main.py`): FastAPIエンドポイント + REST APIフォールバック
2. **データモデル層** (`models.py`): Pydantic入出力モデル
3. **データアクセス層** (`database.py`): SQLAlchemy ORM + クラウドDB接続

### 主要機能
- **CORS対応**: クラウドアプリサービスからのクロスオリジンリクエスト許可
- **接続フォールバック**: PostgreSQL→REST API自動切り替え
- **エラーハンドリング**: 適切なHTTPステータスコードとエラーメッセージ
- **トランザクション管理**: データベース操作の一貫性保証
- **ログ出力**: サーバーアクティビティの記録
- **環境別設定**: 開発環境と本番環境の自動判別

## 接続テスト

### 自動テスト実行

```bash
# 包括的な接続テスト
./supabase_server_manager.sh test

# 期待される結果
✓ ヘルスチェック: 成功
✓ 商品検索API: 成功 (クラウドデータベース接続確認済み)
```

### 個別テスト

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 商品検索（存在する商品）
curl http://localhost:8000/products/4901681143115

# 商品検索（存在しない商品）
curl http://localhost:8000/products/0000000000000
```

## デプロイ

### クラウドアプリサービス

このアプリケーションはクラウドアプリサービス (Python)でのデプロイを前提として設計されています。

**デプロイ先URL**: https://your-app-name.cloudservice.net

#### 必須環境変数（クラウドアプリサービス）
```bash
CLOUD_DB_PASSWORD=your-db-password
ENVIRONMENT=production
```

#### デプロイコマンド例
```bash
# クラウドCLIでのデプロイ
cloud-cli webapp up --name your-app-name --resource-group your-resource-group --runtime PYTHON:3.11
```

詳細なデプロイ手順については、`docs/deployment-guide.md` を参照してください。

## パフォーマンス最適化

- **データベース接続プール**: SQLAlchemyの接続プール機能
- **非同期処理**: FastAPIの非同期エンドポイント
- **REST APIキャッシュ**: httpxクライアントの効率的な接続管理
- **インデックス最適化**: PostgreSQLデータベースクエリの高速化

## セキュリティ

- **CORS設定**: クラウドアプリサービス等の適切なオリジン制限
- **入力検証**: Pydanticによる型安全性
- **SQLインジェクション対策**: SQLAlchemy ORMの使用
- **クラウドDB認証**: API Key認証による安全なアクセス
- **SSL/TLS対応**: クラウドPostgreSQLのSSL接続
- **環境変数管理**: 機密情報の安全な管理

## ログ管理

サーバーアクティビティは `cloud-backend.log` に記録されます：
- リクエスト/レスポンス情報
- クラウドDB REST API通信ログ
- エラー情報とスタックトレース
- データベース操作ログ

## トラブルシューティング

### よくある問題

1. **クラウドDB接続エラー**
   - 環境変数 `CLOUD_DB_PASSWORD` が設定されているか確認
   - ネットワーク接続を確認
   - REST APIフォールバックが動作するか確認

2. **IPv6接続エラー（WSL環境）**
   - 自動的にREST API経由にフォールバック
   - ログで "REST API経由での商品検索" メッセージを確認

3. **依存関係エラー**
   - `pip install -r requirements.txt` で再インストール
   - Pythonバージョンを確認（3.11以上推奨）
   - httpx==0.27.2 が正しくインストールされているか確認

4. **ポート競合**
   - `./supabase_server_manager.sh force-kill` でポート解放
   - 別のポートで起動: `--port 8001`

5. **環境変数エラー**
   - 開発環境: `CLOUD_DB_PASSWORD` と `ENVIRONMENT=development` 確認
   - 本番環境: クラウドアプリサービスの環境変数設定確認

### デバッグ方法

```bash
# ログをリアルタイム監視
./supabase_server_manager.sh logs

# サーバー状態確認
./supabase_server_manager.sh status

# 接続テスト実行
./supabase_server_manager.sh test
```

## 開発ガイドライン

- PEP 8準拠のコーディングスタイル
- 型ヒントの適切な使用
- ドキュメント文字列の記述
- エラーハンドリングの適切な実装
- クラウドDBベストプラクティスの遵守
- 環境対応設計の維持

## 関連ドキュメント

- [移行計画書](docs/migration-plan.md) - MySQL→クラウドDB移行の詳細
- [デプロイガイド](docs/deployment-guide.md) - クラウドアプリサービス展開手順
- [API比較表](docs/api-comparison.md) - FastAPI vs Edge Functions比較

## ライセンス

このプロジェクトは教育目的で作成されています。