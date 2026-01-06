"""
本地BTC数据生成器 - 当所有在线API都失败时使用
生成2016-2024年的示例BTC日线数据用于回测测试
"""
import datetime
import random

# 设置随机种子以确保数据一致性
random.seed(42)

def generate_local_btc_data() -> list:
    """
    生成本地BTC历史数据（2016-01-01 到 2026-01-01）
    使用真实的价格趋势模拟，但数据是生成的，仅用于测试
    """
    rows = []
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2026, 1, 1)
    
    # 使用真实BTC价格趋势的近似值
    # 2016年初: ~$400, 2017年底: ~$20k, 2018年底: ~$3k, 2020年底: ~$30k, 2021年底: ~$50k, 2024: ~$40k-60k, 2025-2026: 预测趋势
    base_prices = {
        2016: 400,
        2017: 1000,
        2018: 6000,
        2019: 7000,
        2020: 10000,
        2021: 35000,
        2022: 20000,
        2023: 30000,
        2024: 45000,
        2025: 50000,
        2026: 55000,
    }
    
    current_date = start_date
    current_price = base_prices[2016]
    
    while current_date <= end_date:
        year = current_date.year
        
        # 根据年份调整基础价格
        if year in base_prices:
            target_price = base_prices[year]
            # 平滑过渡到目标价格（每年开始时调整）
            if current_date.month == 1 and current_date.day == 1:
                current_price = target_price
            else:
                price_diff = target_price - current_price
                current_price += price_diff * 0.0001  # 缓慢调整
        
        # 添加随机波动（日波动约2-5%）
        daily_change = random.uniform(-0.05, 0.05)
        current_price *= (1 + daily_change)
        current_price = max(current_price, 100)  # 最低价格限制
        
        # 生成OHLC数据
        open_price = current_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, current_price) * random.uniform(1.0, 1.03)
        low_price = min(open_price, current_price) * random.uniform(0.97, 1.0)
        close_price = current_price
        volume = random.uniform(10000000, 50000000)
        
        rows.append({
            "date": current_date,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": round(volume, 2),
        })
        
        current_date += datetime.timedelta(days=1)
    
    return rows
