# -*- coding: utf-8 -*-
"""
比特币双均线策略回测后端
支持交易成本、止损止盈、高级统计指标
"""
import datetime
import csv
import time
import os
import sys
from functools import lru_cache
from typing import List, Dict, Any

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 导入本地数据生成器
try:
    from btc_data_local import generate_local_btc_data
except ImportError:
    # 如果导入失败，定义一个简单的生成函数
    def generate_local_btc_data():
        return []

# 通用请求头，模拟浏览器访问
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


app = FastAPI(title="BTC Backtest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _download_from_yahoo() -> List[Dict[str, Any]]:
    start_date = datetime.date(2016, 1, 1)
    # 扩展到2026年1月1日，但如果今天还没到，就使用今天
    target_end = datetime.date(2026, 1, 1)
    end_date = min(target_end, datetime.date.today() + datetime.timedelta(days=1))
    period1 = int(datetime.datetime.combine(start_date, datetime.time.min).timestamp())
    period2 = int(datetime.datetime.combine(end_date, datetime.time.min).timestamp())

    url = (
        "https://query1.finance.yahoo.com/v7/finance/download/BTC-USD"
        f"?period1={period1}&period2={period2}"
        "&interval=1d&events=history&includeAdjustedClose=true"
    )

    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Yahoo Finance 下载失败: HTTP {resp.status_code}")

    content = resp.content.decode("utf-8", errors="ignore").splitlines()
    reader = csv.DictReader(content)

    rows: List[Dict[str, Any]] = []
    for r in reader:
        if r.get("Date") in (None, "", "null"):
            continue
        try:
            date = datetime.datetime.strptime(r["Date"], "%Y-%m-%d").date()
            close = float(r["Close"]) if r.get("Close") not in (None, "", "null") else None
        except Exception:
            continue
        if close is None:
            continue
        try:
            open_ = float(r["Open"]) if r.get("Open") not in (None, "", "null") else close
            high = float(r["High"]) if r.get("High") not in (None, "", "null") else close
            low = float(r["Low"]) if r.get("Low") not in (None, "", "null") else close
            volume = float(r["Volume"]) if r.get("Volume") not in (None, "", "null") else 0.0
        except Exception:
            open_ = high = low = close
            volume = 0.0

        rows.append(
            {
                "date": date,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )

    if not rows:
        raise RuntimeError("Yahoo Finance 数据为空")

    rows.sort(key=lambda x: x["date"])
    return rows


def _download_from_binance() -> List[Dict[str, Any]]:
    """
    备用数据源：Binance 现货 BTCUSDT 日线，起始 2017-08-17，扩展到2026-01-01。
    """
    start_date = datetime.datetime(2017, 8, 17)
    # 扩展到2026年1月1日，但如果今天还没到，就使用今天
    target_end = datetime.datetime(2026, 1, 1)
    end_date = min(target_end, datetime.datetime.utcnow())
    start_ts = int(start_date.timestamp() * 1000)
    end_ts = int(end_date.timestamp() * 1000)

    # Binance 单次最多 1000 根，循环拉取
    rows: List[Dict[str, Any]] = []
    next_start = start_ts
    limit = 1000
    while True:
        url = (
            "https://api.binance.com/api/v3/klines"
            f"?symbol=BTCUSDT&interval=1d&startTime={next_start}&endTime={end_ts}&limit={limit}"
        )
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Binance 下载失败: HTTP {resp.status_code}")
        # 避免请求过快
        time.sleep(0.1)
        data = resp.json()
        if not isinstance(data, list) or not data:
            break
        for k in data:
            # kline: [open time, open, high, low, close, volume, close time, ...]
            try:
                open_time = int(k[0]) // 1000
                date = datetime.datetime.utcfromtimestamp(open_time).date()
                open_ = float(k[1])
                high = float(k[2])
                low = float(k[3])
                close = float(k[4])
                volume = float(k[5])
            except Exception:
                continue
            rows.append(
                {
                    "date": date,
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                }
            )
        # 准备下一段
        last_open_time = int(data[-1][0])
        next_start = last_open_time + 24 * 3600 * 1000
        if next_start > end_ts or len(data) < limit:
            break

    if not rows:
        raise RuntimeError("Binance 数据为空")
    rows.sort(key=lambda x: x["date"])
    return rows


def _download_from_coingecko() -> List[Dict[str, Any]]:
    """
    第三个数据源：CoinGecko API（免费，无需API key）
    注意：CoinGecko免费版有速率限制，但通常比Yahoo/Binance更宽松
    """
    # CoinGecko 需要按日期范围分批获取，这里获取最近几年的数据
    rows: List[Dict[str, Any]] = []
    
    # CoinGecko 的 market_chart API 可以获取最多90天的数据
    # 我们需要循环获取历史数据
    # 但免费API有限制，所以我们使用一个更简单的方法：获取最近的数据
    # 为了获取更长的历史，我们使用ohlc API（需要pro版本）
    # 作为备选，我们使用一个公开的CSV数据源或者简化版本
    
    # 尝试使用CoinGecko的简单价格历史API
    # 注意：免费API限制较多，这里作为最后的备选
    try:
        # 使用CoinGecko的market_chart，获取最多90天的数据
        # 为了获取更长的历史，我们需要多次请求
        end_date = datetime.datetime.utcnow()
        start_date = datetime.datetime(2020, 1, 1)  # 从2020年开始
        
        # CoinGecko的market_chart API返回的是从今天往前推的数据
        # 我们只能获取最近的数据，所以这里简化处理
        # 注意：CoinGecko的"max"参数会返回所有历史数据，但可能不包含未来日期
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "max",  # 获取最大历史数据（到当前日期）
            "interval": "daily"
        }
        
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"CoinGecko 下载失败: HTTP {resp.status_code}")
        
        data = resp.json()
        prices = data.get("prices", [])
        
        if not prices:
            raise RuntimeError("CoinGecko 返回空数据")
        
        # prices格式: [[timestamp_ms, price], ...]
        for item in prices:
            try:
                timestamp_ms = item[0]
                price = float(item[1])
                date = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).date()
                # CoinGecko只提供价格，我们用价格作为open/high/low/close
                rows.append({
                    "date": date,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 0.0,
                })
            except Exception:
                continue
        
        if not rows:
            raise RuntimeError("CoinGecko 数据为空")
        
        rows.sort(key=lambda x: x["date"])
        return rows
    except Exception as e:
        raise RuntimeError(f"CoinGecko API错误: {str(e)}")


@lru_cache(maxsize=1)
def load_btc_daily() -> List[Dict[str, Any]]:
    """
    下载真实 BTC 日线数据，按优先级尝试：Yahoo -> Binance -> CoinGecko
    """
    errors = []
    
    # 尝试 Yahoo Finance
    try:
        rows = _download_from_yahoo()
        if not rows:
            raise RuntimeError("Yahoo Finance 返回空数据")
        print(f"[OK] 成功从 Yahoo Finance 下载 {len(rows)} 条BTC数据")
        return rows
    except Exception as e_yahoo:
        error_msg = f"Yahoo: {str(e_yahoo)}"
        errors.append(error_msg)
        print(f"[FAIL] Yahoo Finance 下载失败: {e_yahoo}，尝试 Binance...")
    
    # 尝试 Binance
    try:
        rows = _download_from_binance()
        if not rows:
            raise RuntimeError("Binance 返回空数据")
        print(f"[OK] 成功从 Binance 下载 {len(rows)} 条BTC数据")
        return rows
    except Exception as e_binance:
        error_msg = f"Binance: {str(e_binance)}"
        errors.append(error_msg)
        print(f"[FAIL] Binance 下载失败: {e_binance}，尝试 CoinGecko...")
    
    # 尝试 CoinGecko
    try:
        rows = _download_from_coingecko()
        if not rows:
            raise RuntimeError("CoinGecko 返回空数据")
        print(f"[OK] 成功从 CoinGecko 下载 {len(rows)} 条BTC数据")
        return rows
    except Exception as e_coingecko:
        error_msg = f"CoinGecko: {str(e_coingecko)}"
        errors.append(error_msg)
        print(f"[FAIL] CoinGecko 下载失败: {e_coingecko}，使用本地数据...")
    
    # 最后备选：使用本地生成的数据
    try:
        print("[WARN] 所有在线数据源均失败，使用本地生成的示例数据（仅用于测试）...")
        rows = generate_local_btc_data()
        if not rows:
            raise RuntimeError("本地数据生成失败")
        print(f"[OK] 使用本地数据 {len(rows)} 条BTC数据（注意：这是模拟数据，仅用于功能测试）")
        return rows
    except Exception as e_local:
        error_msg = f"本地数据: {str(e_local)}"
        errors.append(error_msg)
        all_errors = "\n  - ".join(errors)
        final_error = f"所有数据源均失败（包括本地数据）:\n  - {all_errors}\n\n建议：请检查网络连接，或稍后再试。"
        print(f"[FAIL] {final_error}")
        raise RuntimeError(final_error)


def calculate_trade_cost(price: float, quantity: float, fee_rate: float, slippage_rate: float) -> float:
    """
    计算交易成本（手续费 + 滑点）
    - fee_rate: 手续费率（如0.001表示0.1%）
    - slippage_rate: 滑点率（如0.0005表示0.05%）
    """
    trade_value = price * quantity
    fee = trade_value * fee_rate
    slippage = trade_value * slippage_rate
    return fee + slippage


def run_double_ma_strategy(
    data: List[Dict[str, Any]], 
    short: int, 
    long: int, 
    initial_capital: float = 10000.0,
    # 交易成本参数
    fee_rate: float = 0.001,  # 手续费率，默认0.1%
    slippage_rate: float = 0.0005,  # 滑点率，默认0.05%
    # 风险管理参数
    stop_loss_pct: float = 0.0,  # 止损百分比，0表示不使用
    take_profit_pct: float = 0.0,  # 止盈百分比，0表示不使用
) -> Dict[str, Any]:
    """
    增强版双均线策略：收盘价短均线上穿长均线做多，下穿全部平仓。
    不做做空，只做多，始终满仓或空仓。
    
    新增功能：
    - 交易成本模拟（手续费+滑点）
    - 止损止盈功能
    - 高级统计指标（Sortino、Calmar等）
    """
    if short >= long:
        raise ValueError("短均线周期必须小于长均线周期")
    
    if not data or len(data) < long:
        raise ValueError(f"数据不足，至少需要 {long} 条记录，当前只有 {len(data) if data else 0} 条")

    rows = sorted(data, key=lambda x: x["date"])

    closes = [r["close"] for r in rows]
    dates = [r["date"] for r in rows]
    
    # 验证数据有效性
    if not closes or all(c <= 0 for c in closes):
        raise ValueError("数据无效：收盘价必须大于0")

    n = len(rows)
    ma_short = [None] * n
    ma_long = [None] * n

    # 简单移动平均
    for i in range(n):
        if i + 1 >= short:
            window = closes[i + 1 - short : i + 1]
            ma_short[i] = sum(window) / len(window)
        if i + 1 >= long:
            window = closes[i + 1 - long : i + 1]
            ma_long[i] = sum(window) / len(window)

    signal = [0] * n
    for i in range(n):
        if ma_short[i] is not None and ma_long[i] is not None and ma_short[i] > ma_long[i]:
            signal[i] = 1

    position = [0] * n
    for i in range(1, n):
        position[i] = signal[i - 1]

    # 使用更真实的交易逻辑，考虑交易成本和止损止盈
    equity = [initial_capital] * n
    cash = initial_capital
    holdings = 0.0  # 持仓数量
    entry_price = 0.0
    entry_index = 0
    highest_price_after_entry = 0.0  # 用于跟踪最高价（移动止损）
    
    # 计算每日收益率（用于统计）
    pct_change = [0.0] * n
    for i in range(1, n):
        if closes[i - 1] != 0:
            pct_change[i] = closes[i] / closes[i - 1] - 1.0
    
    strategy_ret = [0.0] * n
    
    for i in range(1, n):
        current_price = closes[i]
        prev_pos = position[i - 1]
        curr_pos = position[i]
        
        # 检查止损止盈（仅在持仓时）
        if holdings > 0 and entry_price > 0:
            # 更新最高价
            if current_price > highest_price_after_entry:
                highest_price_after_entry = current_price
            
            # 检查止损
            if stop_loss_pct > 0:
                stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
                if current_price <= stop_loss_price:
                    # 触发止损，强制平仓
                    trade_cost = calculate_trade_cost(current_price, holdings, fee_rate, slippage_rate)
                    cash = holdings * current_price - trade_cost
                    holdings = 0.0
                    entry_price = 0.0
                    highest_price_after_entry = 0.0
                    position[i] = 0  # 更新position数组
                    equity[i] = cash
                    strategy_ret[i] = (cash - equity[i - 1]) / equity[i - 1] if equity[i - 1] > 0 else 0.0
                    continue
            
            # 检查止盈
            if take_profit_pct > 0:
                take_profit_price = entry_price * (1 + take_profit_pct / 100)
                if current_price >= take_profit_price:
                    # 触发止盈，强制平仓
                    trade_cost = calculate_trade_cost(current_price, holdings, fee_rate, slippage_rate)
                    cash = holdings * current_price - trade_cost
                    holdings = 0.0
                    entry_price = 0.0
                    highest_price_after_entry = 0.0
                    position[i] = 0  # 更新position数组
                    equity[i] = cash
                    strategy_ret[i] = (cash - equity[i - 1]) / equity[i - 1] if equity[i - 1] > 0 else 0.0
                    continue
        
        # 买入信号：从空仓到持仓
        if prev_pos == 0 and curr_pos == 1:
            if cash > 0:
                # 计算可买入数量（考虑交易成本）
                trade_cost_estimate = cash * (fee_rate + slippage_rate)
                available_cash = cash - trade_cost_estimate
                if available_cash > 0:
                    holdings = available_cash / current_price
                    trade_cost = calculate_trade_cost(current_price, holdings, fee_rate, slippage_rate)
                    cash = cash - holdings * current_price - trade_cost
                    entry_price = current_price
                    entry_index = i
                    highest_price_after_entry = current_price
        
        # 卖出信号：从持仓到空仓
        elif prev_pos == 1 and curr_pos == 0:
            if holdings > 0:
                trade_cost = calculate_trade_cost(current_price, holdings, fee_rate, slippage_rate)
                cash = holdings * current_price - trade_cost
                holdings = 0.0
                entry_price = 0.0
                highest_price_after_entry = 0.0
        
        # 计算当前净值
        equity[i] = cash + holdings * current_price
        if equity[i - 1] > 0:
            strategy_ret[i] = (equity[i] - equity[i - 1]) / equity[i - 1]
        else:
            strategy_ret[i] = 0.0

    # 重新计算交易记录（基于实际交易）
    trades: List[Dict[str, Any]] = []
    current_pos = 0
    entry_price_record = 0.0
    entry_date_record: datetime.date | None = None
    entry_index_record = 0
    exit_reason = "signal"  # signal, stop_loss, take_profit

    for i in range(1, n):
        pos = int(position[i])
        prev_pos = int(position[i - 1])
        price = float(closes[i])
        date = dates[i]
        
        # 买入
        if prev_pos == 0 and pos == 1:
            current_pos = 1
            entry_price_record = price
            entry_date_record = date
            entry_index_record = i
            exit_reason = "signal"
        
        # 卖出（检查是否因为止损止盈）
        elif prev_pos == 1 and pos == 0:
            exit_price = price
            exit_date = date
            
            # 检查是否因为止损止盈
            if entry_price_record > 0:
                if stop_loss_pct > 0 and price <= entry_price_record * (1 - stop_loss_pct / 100):
                    exit_reason = "stop_loss"
                elif take_profit_pct > 0 and price >= entry_price_record * (1 + take_profit_pct / 100):
                    exit_reason = "take_profit"
                else:
                    exit_reason = "signal"
            
            trades.append(
                {
                    "entry_date": entry_date_record.isoformat() if entry_date_record else None,
                    "exit_date": exit_date.isoformat(),
                    "entry_price": entry_price_record,
                    "exit_price": exit_price,
                    "pnl_pct": (exit_price - entry_price_record) / entry_price_record
                    if entry_price_record > 0
                    else 0.0,
                    "exit_reason": exit_reason,
                }
            )
            current_pos = 0
            entry_price_record = 0.0
            entry_date_record = None
            exit_reason = "signal"

    equity_curve: List[Dict[str, Any]] = []
    for i in range(n):
        if ma_short[i] is None or ma_long[i] is None:
            continue
        equity_curve.append(
            {
                "date": dates[i].isoformat(),
                "close": float(closes[i]),
                "ma_short": float(ma_short[i]),
                "ma_long": float(ma_long[i]),
                "equity": float(equity[i]),
                "position": int(position[i]),
            }
        )

    if equity_curve:
        total_ret = equity_curve[-1]["equity"] / initial_capital - 1.0
    else:
        total_ret = 0.0

    max_drawdown = 0.0
    if equity_curve:
        peak = equity_curve[0]["equity"]
        max_dd = 0.0
        for pt in equity_curve:
            eq = pt["equity"]
            if eq > peak:
                peak = eq
            dd = eq / peak - 1.0
            if dd < max_dd:
                max_dd = dd
        max_drawdown = float(max_dd)

    # 年化收益（CAGR）与高级指标
    cagr = 0.0
    sharpe = 0.0
    sortino = 0.0
    calmar = 0.0
    annualized_vol = 0.0
    max_drawdown_duration = 0
    
    if equity_curve and len(dates) > 0:
        days = (dates[-1] - dates[0]).days
        if days > 0:
            years = days / 365.25
            if years > 0:
                final_equity = equity_curve[-1]["equity"]
                if final_equity > 0 and initial_capital > 0:
                    cagr = (final_equity / initial_capital) ** (1 / years) - 1.0
        
        # 计算收益率序列（用于统计）
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i - 1]["equity"] > 0:
                ret = (equity_curve[i]["equity"] - equity_curve[i - 1]["equity"]) / equity_curve[i - 1]["equity"]
                returns.append(ret)
        
        if len(returns) > 1:
            mean_ret = sum(returns) / len(returns)
            var = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
            std = var ** 0.5 if var > 0 else 0.0
            
            # 年化波动率
            annualized_vol = std * (252 ** 0.5) if std > 0 else 0.0
            
            # 夏普比率（无风险利率视为0）
            if annualized_vol > 0:
                sharpe = (cagr) / annualized_vol
            
            # Sortino比率（只考虑下行波动）
            downside_returns = [r for r in returns if r < 0]
            if len(downside_returns) > 0:
                downside_var = sum(r ** 2 for r in downside_returns) / len(downside_returns)
                downside_std = downside_var ** 0.5 if downside_var > 0 else 0.0
                annualized_downside_vol = downside_std * (252 ** 0.5) if downside_std > 0 else 0.0
                if annualized_downside_vol > 0:
                    sortino = (cagr) / annualized_downside_vol
                elif cagr > 0:
                    sortino = float('inf')
            
            # Calmar比率（年化收益/最大回撤）
            if max_drawdown < 0:
                calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0.0
        
        # 计算最大回撤持续时间
        peak = equity_curve[0]["equity"]
        current_dd_duration = 0
        for pt in equity_curve:
            eq = pt["equity"]
            if eq > peak:
                peak = eq
                current_dd_duration = 0
            else:
                current_dd_duration += 1
                max_drawdown_duration = max(max_drawdown_duration, current_dd_duration)

    # 交易统计
    win_count = 0
    loss_count = 0
    win_sum = 0.0
    loss_sum = 0.0
    hold_days = []
    for t in trades:
        pnl = t["pnl_pct"]
        if pnl > 0:
            win_count += 1
            win_sum += pnl
        elif pnl < 0:
            loss_count += 1
            loss_sum += pnl
        if t["entry_date"] and t["exit_date"]:
            try:
                d1 = datetime.datetime.strptime(t["entry_date"], "%Y-%m-%d").date()
                d2 = datetime.datetime.strptime(t["exit_date"], "%Y-%m-%d").date()
                hold_days.append((d2 - d1).days or 1)
            except Exception:
                pass
    total_trades = len(trades)
    win_rate = win_count / total_trades if total_trades > 0 else 0.0
    avg_win = win_sum / win_count if win_count > 0 else 0.0
    avg_loss = loss_sum / loss_count if loss_count > 0 else 0.0
    profit_factor = (win_sum) / abs(loss_sum) if loss_sum != 0 else None
    avg_hold = sum(hold_days) / len(hold_days) if hold_days else None

    return {
        "params": {
            "short": short,
            "long": long,
            "initial_capital": initial_capital,
            "fee_rate": fee_rate,
            "slippage_rate": slippage_rate,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
        },
        "equity_curve": equity_curve,
        "trades": trades,
        "summary": {
            "total_return_pct": float(total_ret * 100),
            "cagr_pct": float(cagr * 100),
            "sharpe_ratio": float(sharpe) if not (isinstance(sharpe, float) and sharpe == float('inf')) else None,
            "sortino_ratio": float(sortino) if not (isinstance(sortino, float) and sortino == float('inf')) else None,
            "calmar_ratio": float(calmar) if not (isinstance(calmar, float) and calmar == float('inf')) else None,
            "annualized_volatility_pct": float(annualized_vol * 100),
            "max_drawdown_pct": float(max_drawdown * 100),
            "max_drawdown_duration": max_drawdown_duration,
            "num_trades": total_trades,
            "win_rate_pct": float(win_rate * 100),
            "profit_factor": float(profit_factor) if profit_factor is not None else None,
            "avg_win_pct": float(avg_win * 100) if win_count > 0 else None,
            "avg_loss_pct": float(avg_loss * 100) if loss_count > 0 else None,
            "avg_hold_days": float(avg_hold) if avg_hold is not None else None,
        },
    }


@app.get("/api/btc_daily")
def get_btc_daily():
    """
    提供原始 BTC 日线数据，方便未来其他策略共用。
    """
    try:
        rows = load_btc_daily()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    records = []
    for row in rows:
        records.append(
            {
                "date": row["date"].isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
        )
    return {"symbol": "BTC-USD", "timeframe": "1d", "data": records}


@app.get("/api/backtest/double_ma")
def backtest_double_ma(
    short: int = Query(10, ge=2, le=200),
    long: int = Query(50, ge=5, le=400),
    initial_capital: float = Query(10000.0, gt=0),
    # 交易成本参数
    fee_rate: float = Query(0.001, ge=0, le=0.01, description="手续费率，默认0.1%"),
    slippage_rate: float = Query(0.0005, ge=0, le=0.01, description="滑点率，默认0.05%"),
    # 风险管理参数
    stop_loss_pct: float = Query(0.0, ge=0, le=50, description="止损百分比，0表示不使用"),
    take_profit_pct: float = Query(0.0, ge=0, le=100, description="止盈百分比，0表示不使用"),
):
    """
    增强版双均线策略回测接口。
    新增功能：
    - 交易成本模拟（手续费+滑点）
    - 止损止盈功能
    - 高级统计指标（Sortino、Calmar等）
    """
    try:
        data = load_btc_daily()
        if not data:
            raise HTTPException(status_code=500, detail="无法获取BTC数据，请检查网络连接")
        result = run_double_ma_strategy(
            data=data, 
            short=short, 
            long=long, 
            initial_capital=initial_capital,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"回测错误: {error_detail}")  # 打印到控制台
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os

    # 支持生产环境（Railway、Render等）的PORT环境变量
    port = int(os.environ.get("PORT", 8000))
    # 生产环境不使用reload
    reload = os.environ.get("ENV", "production") == "development"
    
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=reload)

