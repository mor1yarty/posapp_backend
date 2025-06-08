# POSアプリケーション - バックエンド (FastAPI)

モバイルPOSシステムのバックエンドAPI実装です。FastAPIを使用した高性能なPython WebAPIです。

## 技術スタック

- **フレームワーク**: FastAPI 0.104.1
- **ASGI サーバー**: Uvicorn 0.24.0
- **ORM**: SQLAlchemy 2.0.23
- **データベースドライバー**: PyMySQL 1.1.0
- **データ検証**: Pydantic 2.5.0
- **データベース**: MySQL 8.0

## 機能

### API エンドポイント

#### 商品マスタ検索
- **エンドポイント**: `GET /products/{code}`
- **機能**: JANコードによる商品情報検索
- **レスポンス**: 商品ID、商品名、品名、色、品番、価格

#### 購入処理
- **エンドポイント**: `POST /purchase`
- **機能**: 購入データの保存
- **処理**: 取引データ(TRD)と取引明細(TRD_DTL)の作成
- **税額計算**: 消費税の自動計算機能

#### 税額計算
- **エンドポイント**: `POST /calculate-tax`
- **機能**: 商品価格に基づく税額計算
- **対応税率**: 標準税率10%、軽減税率8%

#### ヘルスチェック
- **エンドポイント**: `GET /health`
- **機能**: サーバー状態の確認

## データベース設計

### PRD_MASTER（商品マスタ）
- `PRD_ID`: INTEGER (主キー)
- `CODE`: CHAR(13) (JANコード、ユニーク)
- `PRODUCT_NAME`: VARCHAR(50) (品名)
- `COLOR`: VARCHAR(30) (色)
- `ITEM_CODE`: VARCHAR(20) (品番)
- `NAME`: VARCHAR(100) (商品名)
- `PRICE`: INTEGER (価格)

### TRD（取引）
- `TRD_ID`: INTEGER (主キー)
- `DATETIME`: TIMESTAMP (取引日時)
- `EMP_CD`: CHAR(10) (従業員コード)
- `STORE_CD`: CHAR(5) (店舗コード)
- `POS_NO`: CHAR(3) (POS番号)
- `TOTAL_AMT`: INTEGER (合計金額)

### TRD_DTL（取引明細）
- `TRD_ID`: INTEGER (主キー、外部キー)
- `DTL_ID`: INTEGER (主キー)
- `PRD_ID`: INTEGER (外部キー)
- `PRD_CODE`: CHAR(13) (商品コード)
- `PRD_NAME`: VARCHAR(100) (商品名)
- `PRD_PRICE`: INTEGER (商品価格)

## ディレクトリ構成

```
pos-app-backend/
├── main.py                     # メインアプリケーション
├── database.py                 # データベース設定とORMモデル
├── models.py                   # Pydanticモデル定義
├── tax_calculator.py           # 税額計算機能
├── DigiCertGlobalRootCA.crt.pem # Azure MySQL SSL証明書
├── requirements.txt            # Python依存関係
├── .env.example               # 環境変数テンプレート
├── Dockerfile                 # Dockerコンテナ設定
├── server.log                 # サーバーログ
└── README.md
```

## 環境設定

### 前提条件
- Python 3.11以上
- MySQL 8.0以上

### インストール

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 環境変数設定

**開発環境**: `.env.example`をコピーして`.env`ファイルを作成し、環境に合わせて設定：

```bash
cp .env.example .env
```

```.env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/pos_app
DEBUG=True
```

**本番環境**: 環境変数を直接設定（`.env`ファイルは使用しません）：
```bash
export ENVIRONMENT=production
export DB_HOST=your-production-host
export DB_USER=your-username
export DB_PASSWORD=your-password
export DB_NAME=your-database
```

### データベースセットアップ

```bash
# MySQLデータベースの作成
mysql -u root -p
CREATE DATABASE pos_app;

# スキーマとサンプルデータの投入
SOURCE ../database/schema.sql;
SOURCE ../database/sample_data.sql;
```

## 開発

### 開発サーバー起動

```bash
# 開発モードでの起動
uvicorn main:app --reload --port 8000

# 本番モードでの起動
uvicorn main:app --host 0.0.0.0 --port 8000
```

サーバーは http://localhost:8000 で利用可能になります。

### API ドキュメント

FastAPIの自動生成ドキュメントが利用できます：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## APIの使用例

### 商品検索

```bash
# 商品検索API
curl -X GET "http://localhost:8000/products/4901681513017"

# レスポンス例
{
  "prd_id": 1,
  "code": "4901681513017",
  "product_name": "サラサクリップ",
  "color": "ブラック",
  "item_code": "JJ15-BK",
  "name": "サラサクリップ ブラック",
  "price": 130
}
```

### 購入処理

```bash
# 購入処理API
curl -X POST "http://localhost:8000/purchase" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "prd_id": 1,
        "prd_code": "4901681513017",
        "prd_name": "サラサクリップ ブラック",
        "prd_price": 130,
        "quantity": 2
      }
    ]
  }'

# レスポンス例
{
  "transaction_id": 1,
  "total_amount": 260,
  "message": "購入が完了しました"
}
```

### 税額計算

```bash
# 税額計算API
curl -X POST "http://localhost:8000/calculate-tax" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "サラサクリップ ブラック",
        "price": 130,
        "quantity": 2,
        "tax_rate": 0.10
      }
    ]
  }'

# レスポンス例
{
  "subtotal": 260,
  "tax_amount": 26,
  "total_amount": 286,
  "items": [
    {
      "name": "サラサクリップ ブラック",
      "price": 130,
      "quantity": 2,
      "tax_rate": 0.10,
      "item_total": 260,
      "item_tax": 26
    }
  ]
}
```

## アーキテクチャ

### レイヤー構造
1. **API層** (`main.py`): FastAPIエンドポイント定義
2. **データモデル層** (`models.py`): Pydantic入出力モデル
3. **データアクセス層** (`database.py`): SQLAlchemy ORM

### 主要機能
- **CORS対応**: フロントエンドからのクロスオリジンリクエスト許可
- **エラーハンドリング**: 適切なHTTPステータスコードとエラーメッセージ
- **トランザクション管理**: データベース操作の一貫性保証
- **ログ出力**: サーバーアクティビティの記録
- **環境別設定**: 開発環境と本番環境の自動判別

## Docker対応

```bash
# イメージのビルド
docker build -t pos-backend .

# コンテナの実行
docker run -p 8000:8000 pos-backend
```

## テスト

### 手動テスト

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 商品検索テスト
curl http://localhost:8000/products/4901681513017

# 購入処理テスト
curl -X POST http://localhost:8000/purchase \
  -H "Content-Type: application/json" \
  -d '{"items":[{"prd_id":1,"prd_code":"4901681513017","prd_name":"サラサクリップ ブラック","prd_price":130,"quantity":1}]}'

# 税額計算テスト
curl -X POST http://localhost:8000/calculate-tax \
  -H "Content-Type: application/json" \
  -d '{"items":[{"name":"テスト商品","price":100,"quantity":1,"tax_rate":0.10}]}'
```

## デプロイ

### Azure Web App
このアプリケーションはAzure Web App (Python)でのデプロイを前提として設計されています。

詳細なデプロイ手順については、プロジェクトルートの `azure-deployment.md` を参照してください。

### 環境変数（本番）
```bash
# 必須環境変数
ENVIRONMENT=production
DB_HOST=your-production-host.mysql.database.azure.com
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database
DB_PORT=3306

# オプション
DEBUG=False
```

**重要**: 本番環境では`ENVIRONMENT=production`を設定することで、`.env`ファイルの読み込みをスキップし、環境変数を直接使用します。

### SSL接続設定
本番環境（Azure MySQL）では自動的にSSL接続が有効になります：
- Azure MySQLホスト（*.azure.com）を自動検出
- DigiCertGlobalRootCA.crt.pem証明書を使用したセキュア接続
- 開発環境では通常のMySQL接続を使用

## パフォーマンス最適化

- **データベース接続プール**: SQLAlchemyの接続プール機能
- **非同期処理**: FastAPIの非同期エンドポイント
- **インデックス最適化**: データベースクエリの高速化

## セキュリティ

- **CORS設定**: 適切なオリジン制限
- **入力検証**: Pydanticによる型安全性
- **SQLインジェクション対策**: SQLAlchemy ORMの使用
- **エラー情報の適切な隠蔽**: 本番環境での詳細エラー非表示
- **SSL/TLS対応**: Azure MySQL本番環境でのSSL接続
- **証明書管理**: DigiCertGlobalRootCA.crt.pemによる安全な接続

## ログ管理

サーバーアクティビティは `server.log` に記録されます：
- リクエスト/レスポンス情報
- エラー情報
- データベース操作ログ

## トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   - MySQL サーバーが起動していることを確認
   - `.env`ファイルのDATABASE_URLが正しいことを確認
   - データベースが存在することを確認

2. **依存関係エラー**
   - `pip install -r requirements.txt` で再インストール
   - Pythonバージョンを確認（3.11以上推奨）

3. **ポート競合**
   - ポート8000が他のプロセスで使用されていないことを確認
   - 別のポートで起動: `uvicorn main:app --port 8001`

4. **SSL接続エラー（本番環境）**
   - DigiCertGlobalRootCA.crt.pemファイルが存在することを確認
   - Azure MySQLのSSL設定が有効になっていることを確認
   - ENVIRONMENT=productionが設定されていることを確認

5. **環境変数エラー**
   - 開発環境: `.env`ファイルが正しく設定されているか確認
   - 本番環境: 必要な環境変数がすべて設定されているか確認
   - `ENVIRONMENT=production`が本番環境で設定されているか確認

## 開発ガイドライン

- PEP 8準拠のコーディングスタイル
- 型ヒントの適切な使用
- ドキュメント文字列の記述
- エラーハンドリングの適切な実装
- セキュリティベストプラクティスの遵守

## ライセンス

このプロジェクトは教育目的で作成されています。
