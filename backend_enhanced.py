"""
增强版后端 - 量化金融工程师优化版本
添加了交易成本、风险管理、高级指标等功能
"""

import datetime
import time
from functools import lru_cache
from typing import List, Dict, Any, Optional, Tuple

import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 导入原始数据获取函数（假设已存在）
# from backend import load_btc_daily

app = FastAPI(title="BTC Backtest API Enhanced", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_ma(data: List[float], period: int) -> List[Optional[float]]:
    """计算移动平均线"""
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            ma.append(sum(data[i - period + 1 : i + 1]) / period)
    return ma


def apply_stop_loss_take_profit(
    entry_price: float,
    current_price: float,
    position: str,  # 'long' or 'short'
    stop_loss_pct: float,
    take_profit_pct: float,
) -> Tuple[bool, Optional[str]]:
    """
    应用止损止盈逻辑
    返回: (是否触发, 触发类型)
    """
    if position == "long":
        # 做多：止损在下方，止盈在上方
        if stop_loss_pct > 0 and current_price <= entry_price * (1 - stop_loss_pct / 100):
            return True, "stop_loss"
        if take_profit_pct > 0 and current_price >= entry_price * (1 + take_profit_pct / 100):
            return True, "take_profit"
    else:  # short
        # 做空：止损在上方，止盈在下方
        if stop_loss_pct > 0 and current_price >= entry_price * (1 + stop_loss_pct / 100):
            return True, "stop_loss"
        if take_profit_pct > 0 and current_price <= entry_price * (1 - take_profit_pct / 100):
            return True, "take_profit"
    return False, None


def apply_trailing_stop(
    entry_price: float,
    current_price: float,
    highest_price: float,
    position: str,
    trailing_stop_pct: float,
) -> Tuple[bool, float]:
    """
    应用移动止损（跟踪止损）
    返回: (是否触发, 新的最高价)
    """
    if position == "long":
        new_highest = max(highest_price, current_price)
        if trailing_stop_pct > 0 and current_price <= new_highest * (1 - trailing_stop_pct / 100):
            return True, new_highest
        return False, new_highest
    else:  # short
        new_lowest = min(highest_price, current_price)  # 这里highest_price实际是最低价
        if trailing_stop_pct > 0 and current_price >= new_lowest * (1 + trailing_stop_pct / 100):
            return True, new_lowest
        return False, new_lowest


def calculate_trade_cost(price: float, quantity: float, fee_rate: float, slippage_rate: float) -> float:
    """
    计算交易成本
    - fee_rate: 手续费率（如0.001表示0.1%）
    - slippage_rate: 滑点率（如0.0005表示0.05%）
    """
    trade_value = price * quantity
    fee = trade_value * fee_rate
    slippage = trade_value * slippage_rate
    return fee + slippage


def run_enhanced_double_ma_strategy(
    data: List[Dict[str, Any]],
    short_period: int,
    long_period: int,
    initial_capital: float,
    # 风险管理参数
    stop_loss_pct: float = 0.0,  # 止损百分比，0表示不使用
    take_profit_pct: float = 0.0,  # 止盈百分比，0表示不使用
    trailing_stop_pct: float = 0.0,  # 移动止损百分比，0表示不使用
    # 交易成本参数
    fee_rate: float = 0.001,  # 手续费率（0.1%）
    slippage_rate: float = 0.0005,  # 滑点率（0.05%）
    # 仓位管理
    position_size_pct: float = 1.0,  # 每次使用的资金比例（1.0表示满仓）
) -> Dict[str, Any]:
    """
    增强版双均线策略回测
    """
    if len(data) < long_period:
        raise ValueError(f"数据不足，需要至少 {long_period} 条记录")

    closes = [d["close"] for d in data]
    ma_short = calculate_ma(closes, short_period)
    ma_long = calculate_ma(closes, long_period)

    capital = initial_capital
    position = None  # 'long', 'short', None
    position_entry_price = 0.0
    position_entry_index = 0
    position_highest_price = 0.0  # 用于移动止损
    position_quantity = 0.0

    equity_curve = []
    trades = []
    current_trade = None

    for i in range(long_period, len(data)):
        close = closes[i]
        ma_s = ma_short[i]
        ma_l = ma_long[i]
        prev_ma_s = ma_short[i - 1]
        prev_ma_l = ma_long[i - 1]

        # 检查止损止盈
        if position:
            # 检查固定止损止盈
            if stop_loss_pct > 0 or take_profit_pct > 0:
                triggered, trigger_type = apply_stop_loss_take_profit(
                    position_entry_price, close, position, stop_loss_pct, take_profit_pct
                )
                if triggered:
                    # 平仓
                    trade_cost = calculate_trade_cost(close, position_quantity, fee_rate, slippage_rate)
                    if position == "long":
                        capital = position_quantity * close - trade_cost
                    else:
                        capital = capital + (position_entry_price - close) * position_quantity - trade_cost

                    pnl_pct = (
                        (close - position_entry_price) / position_entry_price * 100
                        if position == "long"
                        else (position_entry_price - close) / position_entry_price * 100
                    )

                    trades.append(
                        {
                            "entry_date": data[position_entry_index]["date"],
                            "exit_date": data[i]["date"],
                            "entry_price": position_entry_price,
                            "exit_price": close,
                            "quantity": position_quantity,
                            "pnl": capital - initial_capital,
                            "pnl_pct": pnl_pct,
                            "hold_days": i - position_entry_index,
                            "exit_reason": trigger_type,
                        }
                    )

                    position = None
                    current_trade = None
                    continue

            # 检查移动止损
            if trailing_stop_pct > 0:
                triggered, new_highest = apply_trailing_stop(
                    position_entry_price, close, position_highest_price, position, trailing_stop_pct
                )
                position_highest_price = new_highest
                if triggered:
                    # 平仓
                    trade_cost = calculate_trade_cost(close, position_quantity, fee_rate, slippage_rate)
                    if position == "long":
                        capital = position_quantity * close - trade_cost
                    else:
                        capital = capital + (position_entry_price - close) * position_quantity - trade_cost

                    pnl_pct = (
                        (close - position_entry_price) / position_entry_price * 100
                        if position == "long"
                        else (position_entry_price - close) / position_entry_price * 100
                    )

                    trades.append(
                        {
                            "entry_date": data[position_entry_index]["date"],
                            "exit_date": data[i]["date"],
                            "entry_price": position_entry_price,
                            "exit_price": close,
                            "quantity": position_quantity,
                            "pnl": capital - initial_capital,
                            "pnl_pct": pnl_pct,
                            "hold_days": i - position_entry_index,
                            "exit_reason": "trailing_stop",
                        }
                    )

                    position = None
                    current_trade = None
                    continue

        # 交易信号
        golden_cross = prev_ma_s <= prev_ma_l and ma_s > ma_l  # 金叉：买入信号
        death_cross = prev_ma_s >= prev_ma_l and ma_s < ma_l  # 死叉：卖出信号

        if golden_cross and position != "long":
            # 买入
            if position == "short":
                # 先平空仓
                trade_cost = calculate_trade_cost(close, position_quantity, fee_rate, slippage_rate)
                capital = capital + (position_entry_price - close) * position_quantity - trade_cost

                pnl_pct = (position_entry_price - close) / position_entry_price * 100

                trades.append(
                    {
                        "entry_date": data[position_entry_index]["date"],
                        "exit_date": data[i]["date"],
                        "entry_price": position_entry_price,
                        "exit_price": close,
                        "quantity": position_quantity,
                        "pnl": capital - initial_capital,
                        "pnl_pct": pnl_pct,
                        "hold_days": i - position_entry_index,
                        "exit_reason": "signal",
                    }
                )

            # 开多仓
            trade_cost = calculate_trade_cost(close, capital * position_size_pct, fee_rate, slippage_rate)
            position_quantity = (capital * position_size_pct - trade_cost) / close
            capital = capital - capital * position_size_pct

            position = "long"
            position_entry_price = close
            position_entry_index = i
            position_highest_price = close

        elif death_cross and position != "short":
            # 卖出（做空）
            if position == "long":
                # 先平多仓
                trade_cost = calculate_trade_cost(close, position_quantity, fee_rate, slippage_rate)
                capital = position_quantity * close - trade_cost

                pnl_pct = (close - position_entry_price) / position_entry_price * 100

                trades.append(
                    {
                        "entry_date": data[position_entry_index]["date"],
                        "exit_date": data[i]["date"],
                        "entry_price": position_entry_price,
                        "exit_price": close,
                        "quantity": position_quantity,
                        "pnl": capital - initial_capital,
                        "pnl_pct": pnl_pct,
                        "hold_days": i - position_entry_index,
                        "exit_reason": "signal",
                    }
                )

            # 开空仓（简化处理，实际做空需要借币）
            # 这里我们只做多，死叉时平仓
            position = None
            position_quantity = 0.0

        # 计算当前净值
        if position == "long":
            current_equity = capital + position_quantity * close
        elif position == "short":
            current_equity = capital + (position_entry_price - close) * position_quantity
        else:
            current_equity = capital

        equity_curve.append(
            {
                "date": data[i]["date"],
                "close": close,
                "ma_short": ma_s,
                "ma_long": ma_l,
                "equity": current_equity,
                "position": position,
            }
        )

    # 如果最后还有持仓，平仓
    if position:
        final_close = closes[-1]
        trade_cost = calculate_trade_cost(final_close, position_quantity, fee_rate, slippage_rate)
        if position == "long":
            capital = position_quantity * final_close - trade_cost
        else:
            capital = capital + (position_entry_price - final_close) * position_quantity - trade_cost

        pnl_pct = (
            (final_close - position_entry_price) / position_entry_price * 100
            if position == "long"
            else (position_entry_price - final_close) / position_entry_price * 100
        )

        trades.append(
            {
                "entry_date": data[position_entry_index]["date"],
                "exit_date": data[-1]["date"],
                "entry_price": position_entry_price,
                "exit_price": final_close,
                "quantity": position_quantity,
                "pnl": capital - initial_capital,
                "pnl_pct": pnl_pct,
                "hold_days": len(data) - 1 - position_entry_index,
                "exit_reason": "end_of_data",
            }
        )

    # 计算统计指标
    final_equity = capital
    total_return_pct = (final_equity - initial_capital) / initial_capital * 100

    # 计算回撤
    equity_values = [e["equity"] for e in equity_curve]
    peak = initial_capital
    max_drawdown_pct = 0.0
    max_drawdown_duration = 0
    current_drawdown_duration = 0

    for equity in equity_values:
        if equity > peak:
            peak = equity
            current_drawdown_duration = 0
        else:
            drawdown_pct = (peak - equity) / peak * 100
            max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
            current_drawdown_duration += 1
            max_drawdown_duration = max(max_drawdown_duration, current_drawdown_duration)

    # 计算年化收益
    days = len(equity_curve)
    years = days / 365.25
    if years > 0:
        cagr_pct = ((final_equity / initial_capital) ** (1 / years) - 1) * 100
    else:
        cagr_pct = 0.0

    # 计算收益率序列（用于计算波动率和夏普比率）
    returns = []
    for i in range(1, len(equity_values)):
        ret = (equity_values[i] - equity_values[i - 1]) / equity_values[i - 1]
        returns.append(ret)

    if len(returns) > 0:
        import math

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        annualized_vol = std_dev * math.sqrt(252) * 100  # 年化波动率

        # 夏普比率（假设无风险利率为0）
        sharpe_ratio = (cagr_pct / 100) / (annualized_vol / 100) if annualized_vol > 0 else 0.0

        # Sortino比率（只考虑下行波动）
        downside_returns = [r for r in returns if r < 0]
        if len(downside_returns) > 0:
            downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
            downside_std = math.sqrt(downside_variance)
            annualized_downside_vol = downside_std * math.sqrt(252) * 100
            sortino_ratio = (cagr_pct / 100) / (annualized_downside_vol / 100) if annualized_downside_vol > 0 else 0.0
        else:
            sortino_ratio = float("inf") if cagr_pct > 0 else 0.0

        # Calmar比率
        calmar_ratio = cagr_pct / max_drawdown_pct if max_drawdown_pct > 0 else 0.0
    else:
        annualized_vol = 0.0
        sharpe_ratio = 0.0
        sortino_ratio = 0.0
        calmar_ratio = 0.0

    # 交易统计
    num_trades = len(trades)
    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]

    win_rate_pct = len(winning_trades) / num_trades * 100 if num_trades > 0 else 0.0

    avg_win_pct = sum(t["pnl_pct"] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
    avg_loss_pct = sum(t["pnl_pct"] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0

    total_profit = sum(t["pnl"] for t in winning_trades)
    total_loss = abs(sum(t["pnl"] for t in losing_trades))
    profit_factor = total_profit / total_loss if total_loss > 0 else float("inf") if total_profit > 0 else 0.0

    avg_hold_days = sum(t["hold_days"] for t in trades) / num_trades if num_trades > 0 else 0.0

    return {
        "equity_curve": equity_curve,
        "trades": trades,
        "summary": {
            "total_return_pct": total_return_pct,
            "cagr_pct": cagr_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "max_drawdown_duration": max_drawdown_duration,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "annualized_volatility_pct": annualized_vol,
            "num_trades": num_trades,
            "win_rate_pct": win_rate_pct,
            "profit_factor": profit_factor,
            "avg_win_pct": avg_win_pct,
            "avg_loss_pct": avg_loss_pct,
            "avg_hold_days": avg_hold_days,
            "final_equity": final_equity,
        },
        "params": {
            "short": short_period,
            "long": long_period,
            "initial_capital": initial_capital,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
            "trailing_stop_pct": trailing_stop_pct,
            "fee_rate": fee_rate,
            "slippage_rate": slippage_rate,
            "position_size_pct": position_size_pct,
        },
    }


@app.get("/api/backtest/double_ma_enhanced")
async def backtest_enhanced_double_ma(
    short: int = Query(10, ge=2, le=200),
    long: int = Query(50, ge=5, le=400),
    initial_capital: float = Query(10000, ge=100),
    stop_loss_pct: float = Query(0.0, ge=0, le=50),
    take_profit_pct: float = Query(0.0, ge=0, le=100),
    trailing_stop_pct: float = Query(0.0, ge=0, le=50),
    fee_rate: float = Query(0.001, ge=0, le=0.01),
    slippage_rate: float = Query(0.0005, ge=0, le=0.01),
    position_size_pct: float = Query(1.0, ge=0.1, le=1.0),
):
    """
    增强版双均线策略回测API
    包含风险管理、交易成本、高级指标等功能
    """
    if short >= long:
        raise HTTPException(status_code=400, detail="短均线必须小于长均线")

    # 这里应该调用数据获取函数
    # data = load_btc_daily()
    # 为了示例，这里返回一个占位符
    data = []

    if not data:
        raise HTTPException(status_code=500, detail="无法获取数据")

    try:
        result = run_enhanced_double_ma_strategy(
            data=data,
            short_period=short,
            long_period=long,
            initial_capital=initial_capital,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trailing_stop_pct=trailing_stop_pct,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
            position_size_pct=position_size_pct,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend_enhanced:app", host="0.0.0.0", port=port, reload=False)
