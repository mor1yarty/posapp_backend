from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# リクエスト/レスポンス用のPydanticモデル

class ProductResponse(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    product_price: int
    color: str
    item_code: str
    full_name: str

class PurchaseItem(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    product_price: int

class PurchaseRequest(BaseModel):
    register_staff_code: Optional[str] = "9999999999"
    store_code: str = "30"
    pos_id: str = "90"
    items: List[PurchaseItem]

class PurchaseResponse(BaseModel):
    success: bool
    total_amount: int
    total_amount_ex_tax: Optional[int] = None  # 🆕 税抜金額
    tax_amount: Optional[int] = None          # 🆕 消費税額
    transaction_id: Optional[int] = None
    message: Optional[str] = None