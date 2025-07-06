from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, PrdMaster, Trd, TrdDtl
from models import ProductResponse, PurchaseRequest, PurchaseResponse
from tax_calculator import TaxCalculator
from typing import Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="POS Application API", version="1.0.0")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000",  # HTTPS対応
        "https://app-step4-67.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "POS Application API"}

@app.get("/products/{code}", response_model=Optional[ProductResponse])
async def get_product(code: str, db: Session = Depends(get_db)):
    """
    商品マスタ検索API
    指定された商品コードに基づいて商品情報を取得する
    """
    try:
        logger.info(f"商品検索開始: コード = {code}")
        
        product = db.query(PrdMaster).filter(PrdMaster.code == code).first()
        
        if product:
            logger.info(f"商品見つかりました: {product.name}")
            return ProductResponse(
                product_id=product.prd_id,
                product_code=product.code,
                product_name=product.product_name,
                product_price=product.price,
                color=product.color,
                item_code=product.item_code,
                full_name=product.name
            )
        else:
            logger.info(f"商品が見つかりませんでした: コード = {code}")
            return None
            
    except Exception as e:
        logger.error(f"商品検索中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="商品検索中にエラーが発生しました")

@app.post("/purchase", response_model=PurchaseResponse)
async def create_purchase(purchase_request: PurchaseRequest, db: Session = Depends(get_db)):
    """
    購入処理API
    購入商品リストを受け取り、取引と取引明細を作成する
    """
    try:
        logger.info("購入処理開始")
        
        # 購入商品が空の場合はエラー
        if not purchase_request.items:
            raise HTTPException(status_code=400, detail="購入商品が指定されていません")
        
        # 取引レコード作成
        new_transaction = Trd(
            emp_cd=purchase_request.register_staff_code or "9999999999",
            store_cd=purchase_request.store_code,
            pos_no=purchase_request.pos_id,
            total_amt=0,  # 初期値
            ttl_amt_ex_tax=0  # 🆕 税抜金額初期値
        )
        
        db.add(new_transaction)
        db.flush()  # TRD_IDを取得するためにflush
        
        transaction_id = new_transaction.trd_id
        logger.info(f"取引ID作成: {transaction_id}")
        
        # 取引明細レコード作成と合計金額計算
        total_amount = 0
        for idx, item in enumerate(purchase_request.items):
            dtl_record = TrdDtl(
                trd_id=transaction_id,
                dtl_id=idx + 1,  # 1から開始
                prd_id=item.product_id,
                prd_code=item.product_code,
                prd_name=item.product_name,
                prd_price=item.product_price,
                tax_cd='10'  # 🆕 消費税区分（固定値：10%）
            )
            db.add(dtl_record)
            total_amount += item.product_price
            
        logger.info(f"取引明細作成完了: {len(purchase_request.items)}件, 合計金額: {total_amount}")
        
        # 🆕 税計算処理
        tax_calculation = TaxCalculator.calculate_tax_exclusive_amount(total_amount, '10')
        total_amount_ex_tax = tax_calculation['tax_exclusive_amount']
        tax_amount = tax_calculation['tax_amount']
        
        logger.info(f"税計算結果: 税込={total_amount}, 税抜={total_amount_ex_tax}, 消費税={tax_amount}")
        
        # 取引テーブルの合計金額を更新
        new_transaction.total_amt = total_amount
        new_transaction.ttl_amt_ex_tax = total_amount_ex_tax  # 🆕 税抜金額
        
        # 全ての変更をコミット
        db.commit()
        
        logger.info("購入処理完了")
        
        return PurchaseResponse(
            success=True,
            total_amount=total_amount,
            total_amount_ex_tax=total_amount_ex_tax,  # 🆕 税抜金額
            tax_amount=tax_amount,                   # 🆕 消費税額
            transaction_id=transaction_id,
            message="購入処理が正常に完了しました"
        )
        
    except Exception as e:
        logger.error(f"購入処理中にエラーが発生しました: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="購入処理中にエラーが発生しました")

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)