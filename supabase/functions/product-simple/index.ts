import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req: Request) => {
  // CORS設定
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  };

  // OPTIONSリクエスト (CORS preflight) の処理
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Supabaseクライアント初期化
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // URLから商品コードを取得
    const url = new URL(req.url);
    const pathParts = url.pathname.split('/');
    const code = pathParts[pathParts.length - 1];

    if (!code) {
      return new Response(
        JSON.stringify({ error: "商品コードが指定されていません" }),
        { 
          status: 400,
          headers: { 
            "Content-Type": "application/json",
            ...corsHeaders
          }
        }
      );
    }

    console.log(`商品検索開始: コード = ${code}`);

    // データベースから商品を検索
    const { data: product, error } = await supabase
      .from('prd_master')
      .select('prd_id, code, product_name, color, item_code, name, price')
      .eq('code', code)
      .single();

    if (error) {
      console.log(`商品が見つかりませんでした: コード = ${code}`, error);
      return new Response(
        JSON.stringify({ error: "商品がマスタ未登録です" }),
        { 
          status: 404,
          headers: { 
            "Content-Type": "application/json",
            ...corsHeaders
          }
        }
      );
    }

    if (product) {
      console.log(`商品見つかりました: ${product.name}`);
      
      // FastAPIのProductResponseフォーマットに合わせる
      const responseData = {
        product_id: product.prd_id,
        product_code: product.code,
        product_name: product.product_name,
        product_price: product.price,
        color: product.color,
        item_code: product.item_code,
        full_name: product.name
      };

      return new Response(
        JSON.stringify(responseData),
        { 
          headers: { 
            "Content-Type": "application/json",
            ...corsHeaders
          }
        }
      );
    } else {
      console.log(`商品が見つかりませんでした: コード = ${code}`);
      return new Response(
        JSON.stringify(null),
        { 
          headers: { 
            "Content-Type": "application/json",
            ...corsHeaders
          }
        }
      );
    }

  } catch (error) {
    console.error('商品検索中にエラーが発生しました:', error);
    
    return new Response(
      JSON.stringify({ 
        error: "商品検索中にエラーが発生しました",
        details: error.message 
      }),
      { 
        status: 500,
        headers: { 
          "Content-Type": "application/json",
          ...corsHeaders
        }
      }
    );
  }
});