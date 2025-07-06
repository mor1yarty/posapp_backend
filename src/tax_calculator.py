"""
税計算モジュール
消費税の計算処理を行う
"""

from decimal import Decimal, ROUND_DOWN
from typing import Dict


class TaxCalculator:
    """消費税計算クラス"""
    
    # 消費税率の定義
    TAX_RATES = {
        '08': Decimal('0.08'),  # 軽減税率 8%
        '10': Decimal('0.10'),  # 標準税率 10%
    }
    
    @classmethod
    def calculate_tax_exclusive_amount(
        cls, 
        tax_inclusive_amount: int, 
        tax_code: str = '10'
    ) -> Dict[str, int]:
        """
        税込金額から税抜金額と消費税額を計算する
        
        Args:
            tax_inclusive_amount (int): 税込金額
            tax_code (str): 消費税区分 ('08' or '10')
            
        Returns:
            Dict[str, int]: {
                'tax_exclusive_amount': 税抜金額,
                'tax_amount': 消費税額,
                'tax_inclusive_amount': 税込金額（確認用）
            }
        """
        if tax_code not in cls.TAX_RATES:
            raise ValueError(f"無効な消費税区分: {tax_code}")
        
        tax_rate = cls.TAX_RATES[tax_code]
        
        # 税抜金額の計算（端数切り捨て）
        # 税抜金額 = 税込金額 ÷ (1 + 税率)
        tax_exclusive_decimal = Decimal(tax_inclusive_amount) / (Decimal('1') + tax_rate)
        tax_exclusive_amount = int(tax_exclusive_decimal.quantize(Decimal('1'), rounding=ROUND_DOWN))
        
        # 消費税額の計算
        tax_amount = tax_inclusive_amount - tax_exclusive_amount
        
        return {
            'tax_exclusive_amount': tax_exclusive_amount,
            'tax_amount': tax_amount,
            'tax_inclusive_amount': tax_inclusive_amount
        }
    
    @classmethod
    def calculate_tax_inclusive_amount(
        cls, 
        tax_exclusive_amount: int, 
        tax_code: str = '10'
    ) -> Dict[str, int]:
        """
        税抜金額から税込金額と消費税額を計算する
        
        Args:
            tax_exclusive_amount (int): 税抜金額
            tax_code (str): 消費税区分 ('08' or '10')
            
        Returns:
            Dict[str, int]: {
                'tax_exclusive_amount': 税抜金額（確認用）,
                'tax_amount': 消費税額,
                'tax_inclusive_amount': 税込金額
            }
        """
        if tax_code not in cls.TAX_RATES:
            raise ValueError(f"無効な消費税区分: {tax_code}")
        
        tax_rate = cls.TAX_RATES[tax_code]
        
        # 消費税額の計算（端数切り捨て）
        # 消費税額 = 税抜金額 × 税率
        tax_amount_decimal = Decimal(tax_exclusive_amount) * tax_rate
        tax_amount = int(tax_amount_decimal.quantize(Decimal('1'), rounding=ROUND_DOWN))
        
        # 税込金額の計算
        tax_inclusive_amount = tax_exclusive_amount + tax_amount
        
        return {
            'tax_exclusive_amount': tax_exclusive_amount,
            'tax_amount': tax_amount,
            'tax_inclusive_amount': tax_inclusive_amount
        }
    
    @classmethod
    def get_tax_rate(cls, tax_code: str) -> Decimal:
        """
        消費税区分から税率を取得する
        
        Args:
            tax_code (str): 消費税区分
            
        Returns:
            Decimal: 税率
        """
        if tax_code not in cls.TAX_RATES:
            raise ValueError(f"無効な消費税区分: {tax_code}")
        
        return cls.TAX_RATES[tax_code]