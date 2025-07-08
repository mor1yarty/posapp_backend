from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, PrdMaster, Trd, TrdDtl, SUPABASE_URL, SUPABASE_KEY
from models import ProductResponse, PurchaseRequest, PurchaseResponse
from tax_calculator import TaxCalculator
from typing import Optional
import logging
import httpx
import os

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="POS Application API", version="1.0.0")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000",  # 開発環境
        "http://localhost:3000",   # 開発環境HTTP
        "https://tech0-step4-posapp.azurewebsites.net",  # 本番Azure App Service
        "https://posapp-frontend.vercel.app/",  # フロントエンド
        "http://localhost:*",      # Flutter Web開発用
        "*"  # 開発時のみ全てのオリジンを許可
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "POS Application API"}

async def get_product_via_rest_api(code: str):
    """
    Supabase REST API経由で商品情報を取得
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/prd_master?code=eq.{code}&select=*",
                headers=headers
            )
            
            if response.status_code == 200:
                products = response.json()
                if products:
                    product = products[0]
                    return ProductResponse(
                        product_id=product["prd_id"],
                        product_code=product["code"],
                        product_name=product["product_name"],
                        product_price=product["price"],
                        color=product["color"],
                        item_code=product["item_code"],
                        full_name=product["name"]
                    )
                return None
            else:
                logger.error(f"Supabase API エラー: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"REST API経由での商品検索エラー: {e}")
        return None

@app.get("/products/{code}", response_model=Optional[ProductResponse])
async def get_product(code: str):
    """
    商品マスタ検索API
    指定された商品コードに基づいて商品情報を取得する
    """
    try:
        logger.info(f"商品検索開始: コード = {code}")
        
        # まずREST API経由で試行
        product = await get_product_via_rest_api(code)
        
        if product:
            logger.info(f"商品見つかりました: {product.full_name}")
            return product
        else:
            logger.info(f"商品が見つかりませんでした: コード = {code}")
            return None
            
    except Exception as e:
        logger.error(f"商品検索中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="商品検索中にエラーが発生しました")

async def create_purchase_via_rest_api(purchase_request: PurchaseRequest):
    """
    Supabase REST API経由で購入処理を実行
    """
    try:
        logger.info("購入処理開始 (REST API経由)")
        
        # 購入商品が空の場合はエラー
        if not purchase_request.items:
            raise HTTPException(status_code=400, detail="購入商品が指定されていません")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # 取引レコード作成
            trd_data = {
                "emp_cd": purchase_request.register_staff_code or "9999999999",
                "store_cd": purchase_request.store_code or "30",
                "pos_no": purchase_request.pos_id or "90",
                "total_amt": 0,
                "ttl_amt_ex_tax": 0
            }
            
            # 取引テーブルにインサート
            trd_response = await client.post(
                f"{SUPABASE_URL}/rest/v1/trd",
                headers=headers,
                json=trd_data
            )
            
            if trd_response.status_code != 201:
                logger.error(f"取引作成エラー: {trd_response.status_code} - {trd_response.text}")
                raise HTTPException(status_code=500, detail="取引作成に失敗しました")
            
            transaction = trd_response.json()[0]
            transaction_id = transaction["trd_id"]
            logger.info(f"取引ID作成: {transaction_id}")
            
            # 取引明細レコード作成と合計金額計算
            total_amount = 0
            dtl_records = []
            
            for idx, item in enumerate(purchase_request.items):
                dtl_record = {
                    "trd_id": transaction_id,
                    "dtl_id": idx + 1,
                    "prd_id": item.product_id,
                    "prd_code": item.product_code,
                    "prd_name": item.product_name,
                    "prd_price": item.product_price,
                    "tax_cd": "10"
                }
                dtl_records.append(dtl_record)
                total_amount += item.product_price
            
            # 取引明細テーブルにバッチインサート
            dtl_response = await client.post(
                f"{SUPABASE_URL}/rest/v1/trd_dtl",
                headers=headers,
                json=dtl_records
            )
            
            if dtl_response.status_code != 201:
                logger.error(f"取引明細作成エラー: {dtl_response.status_code} - {dtl_response.text}")
                raise HTTPException(status_code=500, detail="取引明細作成に失敗しました")
            
            logger.info(f"取引明細作成完了: {len(purchase_request.items)}件, 合計金額: {total_amount}")
            
            # 税計算処理
            tax_calculation = TaxCalculator.calculate_tax_exclusive_amount(total_amount, '10')
            total_amount_ex_tax = tax_calculation['tax_exclusive_amount']
            tax_amount = tax_calculation['tax_amount']
            
            logger.info(f"税計算結果: 税込={total_amount}, 税抜={total_amount_ex_tax}, 消費税={tax_amount}")
            
            # 取引テーブルの合計金額を更新
            update_data = {
                "total_amt": total_amount,
                "ttl_amt_ex_tax": total_amount_ex_tax
            }
            
            update_response = await client.patch(
                f"{SUPABASE_URL}/rest/v1/trd?trd_id=eq.{transaction_id}",
                headers=headers,
                json=update_data
            )
            
            if update_response.status_code not in [200, 204]:
                logger.error(f"取引更新エラー: {update_response.status_code} - {update_response.text}")
                raise HTTPException(status_code=500, detail="取引更新に失敗しました")
            
            logger.info("購入処理完了 (REST API経由)")
            
            return PurchaseResponse(
                success=True,
                total_amount=total_amount,
                total_amount_ex_tax=total_amount_ex_tax,
                tax_amount=tax_amount,
                transaction_id=transaction_id,
                message="購入処理が正常に完了しました (REST API経由)"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"購入処理中にエラーが発生しました (REST API): {e}")
        logger.error(f"詳細エラー: {error_details}")
        raise HTTPException(status_code=500, detail=f"購入処理中にエラーが発生しました: {str(e)}")

@app.post("/purchase", response_model=PurchaseResponse)
async def create_purchase(purchase_request: PurchaseRequest):
    """
    購入処理API
    購入商品リストを受け取り、取引と取引明細を作成する
    """
    try:
        # まずREST API経由で試行
        return await create_purchase_via_rest_api(purchase_request)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"REST API経由の購入処理に失敗: {e}")
        logger.error(f"詳細エラー: {error_details}")
        raise HTTPException(status_code=500, detail=f"購入処理中にエラーが発生しました: {str(e)}")

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)