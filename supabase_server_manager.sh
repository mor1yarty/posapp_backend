#!/bin/bash

# Supabase対応POSアプリ サーバーマネジメントスクリプト
# Supabase対応FastAPIの開始・停止・再起動・確認を管理

set -e

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ディレクトリパス
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/src"

# PIDファイルパス
BACKEND_PID_FILE="$SCRIPT_DIR/.supabase-backend.pid"

# ログファイルパス
BACKEND_LOG_FILE="$SCRIPT_DIR/supabase-backend.log"

# ヘルプ表示
show_help() {
    echo -e "${BLUE}Supabase対応POSアプリ サーバーマネジメントスクリプト${NC}"
    echo ""
    echo "使用方法:"
    echo "  $0 [コマンド]"
    echo ""
    echo "コマンド:"
    echo -e "  ${GREEN}start${NC}            - Supabase対応FastAPIを開始"
    echo -e "  ${GREEN}stop${NC}             - Supabase対応FastAPIを停止"
    echo -e "  ${GREEN}restart${NC}          - Supabase対応FastAPIを再起動"
    echo -e "  ${GREEN}status${NC}           - サーバーの状態を確認"
    echo -e "  ${GREEN}logs${NC}             - ログを表示"
    echo -e "  ${GREEN}test${NC}             - ヘルスチェックと商品検索APIテスト"
    echo -e "  ${GREEN}force-kill${NC}       - ポート8000を強制解放"
    echo -e "  ${GREEN}help${NC}             - このヘルプを表示"
    echo ""
}

# プロセス存在確認
is_process_running() {
    local pid_file=$1
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# バックエンド開始
start_backend() {
    echo -e "${YELLOW}Supabase対応FastAPIを開始しています...${NC}"
    
    if is_process_running "$BACKEND_PID_FILE"; then
        echo -e "${YELLOW}Supabase対応FastAPIは既に実行中です${NC}"
        echo -e "${GREEN}現在の状態:${NC}"
        check_status
        return 0
    fi
    
    if [[ ! -d "$BACKEND_DIR" ]]; then
        echo -e "${RED}バックエンドディレクトリが見つかりません: $BACKEND_DIR${NC}"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # 環境変数ファイルを読み込み
    if [[ -f "../.env" ]]; then
        export $(grep -v '^#' ../.env | xargs)
    fi
    
    # 仮想環境確認
    if [[ ! -d "venv" ]]; then
        echo -e "${YELLOW}仮想環境を作成しています...${NC}"
        python3 -m venv venv
    fi
    
    # 仮想環境をアクティベートして依存関係をインストール
    source venv/bin/activate
    echo -e "${YELLOW}依存関係をインストール中...${NC}"
    pip install -r ../requirements.txt
    
    # Supabase対応FastAPI開始
    nohup python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > "$BACKEND_LOG_FILE" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    
    sleep 3
    if is_process_running "$BACKEND_PID_FILE"; then
        echo -e "${GREEN}Supabase対応FastAPIが開始されました (PID: $(cat "$BACKEND_PID_FILE"))${NC}"
        echo -e "${GREEN}URL: http://localhost:8000${NC}"
        echo -e "${GREEN}API ドキュメント: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}Supabase DB: https://zhppoucgzyogewhdjire.supabase.co${NC}"
    else
        echo -e "${RED}Supabase対応FastAPIの開始に失敗しました${NC}"
        return 1
    fi
}

# バックエンド停止
stop_backend() {
    echo -e "${YELLOW}Supabase対応FastAPIを停止しています...${NC}"
    
    # PIDファイルからプロセス停止を試行
    if is_process_running "$BACKEND_PID_FILE"; then
        local pid=$(cat "$BACKEND_PID_FILE")
        echo -e "${YELLOW}メインプロセス (PID: $pid) を停止中...${NC}"
        
        # プロセスグループ全体を停止（子プロセスも含む）
        kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
        
        # 少し待ってから強制終了
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}強制終了中...${NC}"
            kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
        fi
        
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # ポート8000を使用しているプロセスを確認・停止
    echo -e "${YELLOW}ポート8000のプロセスを確認中...${NC}"
    local port_pids=$(lsof -ti:8000 2>/dev/null)
    if [[ -n "$port_pids" ]]; then
        echo -e "${YELLOW}ポート8000で実行中のプロセスを停止中...${NC}"
        echo "$port_pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        
        # まだ残っている場合は強制終了
        port_pids=$(lsof -ti:8000 2>/dev/null)
        if [[ -n "$port_pids" ]]; then
            echo -e "${YELLOW}強制終了中...${NC}"
            echo "$port_pids" | xargs kill -KILL 2>/dev/null
        fi
    fi
    
    # 最終確認
    if lsof -i:8000 >/dev/null 2>&1; then
        echo -e "${RED}警告: ポート8000がまだ使用されています${NC}"
        echo -e "${YELLOW}手動で確認してください: lsof -i:8000${NC}"
    else
        echo -e "${GREEN}Supabase対応FastAPIが停止されました${NC}"
    fi
}

# 状態確認
check_status() {
    echo -e "${BLUE}=== Supabase対応FastAPI サーバー状態 ===${NC}"
    
    # バックエンド状態
    if is_process_running "$BACKEND_PID_FILE"; then
        local backend_pid=$(cat "$BACKEND_PID_FILE")
        echo -e "${GREEN}Supabase対応FastAPI: 実行中 (PID: $backend_pid)${NC}"
        echo -e "  URL: http://localhost:8000"
        echo -e "  API ドキュメント: http://localhost:8000/docs"
        echo -e "  Supabase DB: https://zhppoucgzyogewhdjire.supabase.co"
    else
        echo -e "${RED}Supabase対応FastAPI: 停止中${NC}"
    fi
    
    echo ""
}

# ログ表示
show_logs() {
    echo -e "${BLUE}=== Supabase対応FastAPI ログ (Ctrl+C で終了) ===${NC}"
    tail -f "$BACKEND_LOG_FILE" 2>/dev/null
}

# APIテスト実行
test_apis() {
    echo -e "${BLUE}=== Supabase対応FastAPI 接続テスト ===${NC}"
    
    if ! is_process_running "$BACKEND_PID_FILE"; then
        echo -e "${RED}エラー: Supabase対応FastAPIが実行されていません${NC}"
        echo -e "${YELLOW}先に './supabase_server_manager.sh start' でサーバーを開始してください${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}1. ヘルスチェックAPI テスト${NC}"
    echo "curl -X GET \"http://localhost:8000/health\""
    echo ""
    
    health_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "http://localhost:8000/health" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        echo "$health_response"
        echo ""
        if echo "$health_response" | grep -q "HTTP_CODE:200"; then
            echo -e "${GREEN}✓ ヘルスチェック: 成功${NC}"
        else
            echo -e "${RED}✗ ヘルスチェック: 失敗${NC}"
        fi
    else
        echo -e "${RED}✗ ヘルスチェック: 接続失敗${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}2. 商品検索API テスト (Supabaseデータベース接続)${NC}"
    echo "curl -X GET \"http://localhost:8000/products/4901427401912\""
    echo ""
    
    product_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "http://localhost:8000/products/4901427401912" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        echo "$product_response"
        echo ""
        if echo "$product_response" | grep -q "HTTP_CODE:200"; then
            echo -e "${GREEN}✓ 商品検索API: 成功 (Supabaseデータベース接続確認済み)${NC}"
        else
            echo -e "${RED}✗ 商品検索API: 失敗${NC}"
        fi
    else
        echo -e "${RED}✗ 商品検索API: 接続失敗${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}=== テスト完了 ===${NC}"
}

# ポート強制解放
force_kill_ports() {
    echo -e "${YELLOW}ポート8000を強制解放しています...${NC}"
    
    # ポート8000のプロセスを強制終了
    local port8000_pids=$(lsof -ti:8000 2>/dev/null)
    if [[ -n "$port8000_pids" ]]; then
        echo -e "${YELLOW}ポート8000のプロセスを強制終了中...${NC}"
        echo "$port8000_pids" | xargs kill -KILL 2>/dev/null
        echo -e "${GREEN}ポート8000を解放しました${NC}"
    else
        echo -e "${GREEN}ポート8000は使用されていません${NC}"
    fi
    
    # PIDファイルをクリア
    rm -f "$BACKEND_PID_FILE"
    
    echo -e "${GREEN}強制解放完了${NC}"
}

# メイン処理
case "${1:-help}" in
    "start")
        start_backend
        echo ""
        check_status
        ;;
    "stop")
        stop_backend
        ;;
    "restart")
        echo -e "${YELLOW}Supabase対応FastAPIを再起動しています...${NC}"
        stop_backend
        sleep 2
        start_backend
        echo ""
        check_status
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        test_apis
        ;;
    "force-kill")
        force_kill_ports
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}不明なコマンド: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac