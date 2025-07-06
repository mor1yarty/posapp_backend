# POSアプリ クラウドDB ハイブリッド移行プロジェクト

## プロジェクト概要
pos-app-backendをクラウドDBハイブリッド構成に移行。git worktreeを使用してmainブランチとcloud-migrationブランチを並行管理し、Edge Functions + FastAPI の分担構成を実現する。

## アーキテクチャ設計

### 移行後の構成
```
フロントエンド (Next.js)
    ↓
┌─────────────────────────────────────┐
│ API レイヤー                        │
├─────────────────┬───────────────────┤
│ Edge Functions  │ FastAPI          │
│ - GET /health   │ - GET /products  │
│ - 軽量・高速    │ - POST /purchase │
│                 │ - 複雑ロジック   │
└─────────────────┴───────────────────┘
    ↓
クラウド PostgreSQL
```

## リポジトリ構成

### git worktree構成
```
pos-app-backend/
├── main/                          # mainブランチ (MySQL版)
│   ├── main.py
│   ├── database.py               # MySQL版
│   ├── models.py
│   ├── tax_calculator.py
│   └── requirements.txt
└── cloud-db/                  # cloud-migrationブランチ
    ├── src/                      # FastAPI クラウドDB版
    │   ├── main.py
    │   ├── database.py           # PostgreSQL版
    │   ├── models.py
    │   └── tax_calculator.py
    ├── functions/                # Edge Functions
    │   └── functions/
    │       ├── health/
    │       │   └── index.ts
    │       └── product-simple/
    │           └── index.ts
    └── docs/                     # プロジェクトドキュメント
        ├── migration-plan.md
        ├── implementation-checklist.md
        ├── api-comparison.md
        └── deployment-guide.md
```

## エンドポイント分担

### Edge Functions担当
| エンドポイント | 理由 | 実装難易度 |
|---------------|------|-----------|
| GET /health | 最もシンプル | ★☆☆☆☆ |
| GET /products/{code} (基本版) | 単純なDB検索 | ★★☆☆☆ |

### FastAPI担当
| エンドポイント | 理由 | 重要度 |
|---------------|------|--------|
| POST /purchase | 複雑なトランザクション処理 | ★★★★★ |
| GET /products/{code} (完全版) | 複雑なレスポンス構築 | ★★★☆☆ |

## データベーススキーマ

### MySQL → PostgreSQL 変換

#### PRD_MASTER (商品マスター)
```sql
-- PostgreSQL版
CREATE TABLE prd_master (
    prd_id SERIAL PRIMARY KEY,
    code CHAR(13) UNIQUE NOT NULL,
    product_name VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL
);
```

#### TRD (取引)
```sql
-- PostgreSQL版
CREATE TABLE trd (
    trd_id SERIAL PRIMARY KEY,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    emp_cd CHAR(10) NOT NULL,
    store_cd CHAR(5) NOT NULL DEFAULT '30',
    pos_no CHAR(3) NOT NULL DEFAULT '90',
    total_amt INTEGER NOT NULL DEFAULT 0,
    ttl_amt_ex_tax INTEGER
);
```

#### TRD_DTL (取引明細)
```sql
-- PostgreSQL版
CREATE TABLE trd_dtl (
    trd_id INTEGER NOT NULL,
    dtl_id INTEGER NOT NULL,
    prd_id INTEGER NOT NULL,
    prd_code CHAR(13) NOT NULL,
    prd_name VARCHAR(100) NOT NULL,
    prd_price INTEGER NOT NULL,
    tax_cd CHAR(2) DEFAULT '10',
    PRIMARY KEY (trd_id, dtl_id),
    FOREIGN KEY (trd_id) REFERENCES trd(trd_id)
);
```

## 実装スケジュール

- **Phase 1**: git worktree環境構築 (0.5日) ✅
- **Phase 2**: データベース移行 (2日)
- **Phase 3**: Edge Functions実装 (1.5日)
- **Phase 4**: FastAPI クラウドDB対応 (2.5日)
- **Phase 5**: デプロイと検証 (1.5日)

**合計**: 約8日間

## 技術的メリット

- **並行開発**: 既存版と新版を同時参照・比較可能
- **安全性**: main/ で既存版を完全保護
- **パフォーマンス**: Edge Functions による高速レスポンス
- **コスト最適化**: 用途別の最適なホスティング
- **学習機会**: モダンなサーバーレス技術の習得