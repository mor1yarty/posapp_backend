# API実装比較: Edge Functions vs FastAPI

## 概要
POSアプリケーションのAPIエンドポイントを Edge Functions と FastAPI で分担実装する際の比較検討資料。

## エンドポイント分担戦略

### Edge Functions 担当
軽量で高頻度アクセスが想定されるエンドポイント

### FastAPI 担当  
複雑なビジネスロジックやトランザクション処理が必要なエンドポイント

## 詳細比較

### 1. GET /health

#### Edge Functions実装
```typescript
// cloud-db/functions/health/index.ts
export default async function handler(req: Request) {
  return new Response(JSON.stringify({
    status: "healthy",
    service: "pos-edge-functions",
    timestamp: new Date().toISOString(),
    version: "1.0.0"
  }), {
    headers: { "Content-Type": "application/json" }
  });
}
```

**特徴**:
- シンプルな実装
- データベースアクセス不要
- 超高速レスポンス（<50ms想定）
- グローバル配信対応

#### FastAPI実装 (比較用)
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**比較結果**: Edge Functions 採用 ✅
- レスポンス速度: Edge Functions > FastAPI
- 実装コスト: 同等
- 運用コスト: Edge Functions < FastAPI

### 2. GET /products/{code}

#### Edge Functions実装 (簡易版)
```typescript
// cloud-db/functions/product-simple/index.ts
export default async function handler(req: Request) {
  const url = new URL(req.url);
  const code = url.pathname.split('/').pop();
  
  const { data: product, error } = await cloudDB
    .from('prd_master')
    .select('prd_id, code, name, price')
    .eq('code', code)
    .single();
    
  if (error) {
    return new Response(JSON.stringify({ error: "商品がマスタ未登録です" }), {
      status: 404,
      headers: { "Content-Type": "application/json" }
    });
  }
  
  return new Response(JSON.stringify(product), {
    headers: { "Content-Type": "application/json" }
  });
}
```

**特徴**:
- 基本的な商品情報のみ
- シンプルなデータベースクエリ
- 高速レスポンス
- 制限: 複雑なレスポンス構築不可

#### FastAPI実装 (完全版)
```python
@app.get("/products/{code}", response_model=Optional[ProductResponse])
async def get_product(code: str, db: Session = Depends(get_db)):
    product = db.query(PrdMaster).filter(PrdMaster.code == code).first()
    
    if product:
        return ProductResponse(
            product_id=product.prd_id,
            product_code=product.code,
            product_name=product.product_name,
            product_price=product.price,
            color=product.color,
            item_code=product.item_code,
            full_name=product.name
        )
    return None
```

**特徴**:
- 完全な商品情報
- 複雑なレスポンス構築
- SQLAlchemy ORM使用
- エラーハンドリング充実

**比較結果**: 両方実装 ✅
- 用途分離: 簡易版(Edge) + 完全版(FastAPI)
- パフォーマンス最適化
- 段階的移行可能

### 3. POST /purchase

#### Edge Functions実装 (検討のみ)
```typescript
// 実装検討中 - 複雑すぎる可能性
export default async function handler(req: Request) {
  // 複雑なトランザクション処理
  // 税計算ロジック
  // エラーハンドリング
  // → 実装困難と判断
}
```

**課題**:
- トランザクション処理の複雑さ
- 税計算ロジックの移植コスト
- エラーハンドリングの複雑さ
- PostgreSQL関数が必要

#### FastAPI実装 (継続)
```python
@app.post("/purchase", response_model=PurchaseResponse)
async def create_purchase(purchase_request: PurchaseRequest, db: Session = Depends(get_db)):
    # 既存の複雑なビジネスロジックをそのまま使用
    # トランザクション処理
    # 税計算
    # エラーハンドリング
```

**比較結果**: FastAPI継続 ✅
- 既存ロジック保護
- 複雑性に対する最適解
- 段階的移行への含み

## パフォーマンス予測

### レスポンス時間 (想定)
| エンドポイント | Edge Functions | FastAPI | 改善率 |
|----------------|----------------|---------|--------|
| GET /health | 30ms | 150ms | 80%向上 |
| GET /products (簡易) | 100ms | 200ms | 50%向上 |
| GET /products (完全) | - | 200ms | - |
| POST /purchase | - | 500ms | - |

### 運用コスト
| 項目 | Edge Functions | FastAPI |
|------|----------------|---------|
| 基本料金 | 使用量ベース | 固定月額 |
| スケーリング | 自動 | 手動設定必要 |
| 保守性 | 高 | 中 |

## 実装戦略

### Phase 1: 軽量エンドポイント
1. GET /health → Edge Functions
2. GET /products (簡易版) → Edge Functions

### Phase 2: 既存ロジック保護
1. POST /purchase → FastAPI (クラウドDB)
2. GET /products (完全版) → FastAPI (クラウドDB)

### Phase 3: 段階的移行
1. ユーザーフィードバック収集
2. 必要に応じて追加移行検討

## 結論

**ハイブリッド構成の採用** ✅
- 軽量処理: Edge Functions で高速化
- 複雑処理: FastAPI で安定性確保
- 段階的移行: リスク最小化
- 学習効果: モダン技術の習得