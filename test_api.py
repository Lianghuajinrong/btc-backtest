# -*- coding: utf-8 -*-
"""测试API的脚本"""
import requests
import json
import sys

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_api():
    url = "http://127.0.0.1:8000/api/backtest/double_ma"
    params = {
        "short": 10,
        "long": 50,
        "initial_capital": 10000,
        "fee_rate": 0.001,
        "slippage_rate": 0.0005,
        "stop_loss_pct": 5,
        "take_profit_pct": 10
    }
    
    print("正在测试API...")
    print(f"URL: {url}")
    print(f"参数: {params}")
    print("-" * 50)
    
    try:
        r = requests.get(url, params=params, timeout=60)
        print(f"状态码: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            summary = data.get('summary', {})
            params_data = data.get('params', {})
            
            print("\n=== 回测结果 ===")
            print(f"总收益: {summary.get('total_return_pct', 'N/A')}%")
            print(f"年化收益: {summary.get('cagr_pct', 'N/A')}%")
            print(f"夏普比率: {summary.get('sharpe_ratio', 'N/A')}")
            print(f"Sortino比率: {summary.get('sortino_ratio', 'N/A')}")
            print(f"Calmar比率: {summary.get('calmar_ratio', 'N/A')}")
            print(f"年化波动率: {summary.get('annualized_volatility_pct', 'N/A')}%")
            print(f"最大回撤: {summary.get('max_drawdown_pct', 'N/A')}%")
            print(f"最大回撤天数: {summary.get('max_drawdown_duration', 'N/A')} 天")
            print(f"交易次数: {summary.get('num_trades', 'N/A')}")
            print(f"胜率: {summary.get('win_rate_pct', 'N/A')}%")
            print(f"盈亏比: {summary.get('profit_factor', 'N/A')}")
            
            print("\n=== 参数设置 ===")
            print(f"手续费率: {params_data.get('fee_rate', 'N/A')}")
            print(f"滑点率: {params_data.get('slippage_rate', 'N/A')}")
            print(f"止损: {params_data.get('stop_loss_pct', 'N/A')}%")
            print(f"止盈: {params_data.get('take_profit_pct', 'N/A')}%")
            
            print("\n=== 测试通过 ===")
            return True
        else:
            print(f"错误: {r.text}")
            return False
            
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api()
