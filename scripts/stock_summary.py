#!/usr/bin/env python3
"""
Portfolio Summary Report - Quick snapshot of overall performance
"""

import yfinance as yf
from datetime import datetime
import pytz

# Carlo's watchlist
WATCHLIST = [
    "BCE.TO", "BMO.TO", "CM.TO", "CNQ.TO", "EIF.TO", "ENB.TO",
    "GLCC.TO", "MFC.TO", "NTR.TO", "PEY.TO", "PMIF.TO", "RY.TO",
    "SRU-UN.TO", "T.TO", "TD.TO", "TRP.TO", "WCP.TO", "ZWC.TO"
]

def generate_summary():
    """Generate quick portfolio summary"""
    
    est = pytz.timezone('America/Toronto')
    now = datetime.now(est)
    report_time = now.strftime("%I:%M %p EST")
    
    gainers = 0
    losers = 0
    flat = 0
    total_change_pct = 0
    stock_count = 0
    
    changes = []
    
    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                open_price = info.get('regularMarketOpen') or info.get('open', current_price)
            else:
                current_price = data['Close'].iloc[-1]
                open_price = data['Open'].iloc[0]
            
            if current_price == 0 or open_price == 0:
                continue
            
            change_pct = ((current_price - open_price) / open_price) * 100
            changes.append((symbol.replace('.TO', ''), change_pct))
            
            total_change_pct += change_pct
            stock_count += 1
            
            if change_pct > 0.1:
                gainers += 1
            elif change_pct < -0.1:
                losers += 1
            else:
                flat += 1
                
        except Exception:
            continue
    
    if stock_count == 0:
        return "⚠️ Unable to generate summary - no data available"
    
    avg_change = total_change_pct / stock_count
    
    # Direction indicator
    if avg_change > 0.5:
        direction = "🟢 PORTFOLIO UP"
        arrow = "↑"
    elif avg_change < -0.5:
        direction = "🔴 PORTFOLIO DOWN"
        arrow = "↓"
    else:
        direction = "⚪ PORTFOLIO FLAT"
        arrow = "→"
    
    report = f"📊 **PORTFOLIO SUMMARY**\n"
    report += f"{report_time}\n"
    report += "=" * 40 + "\n\n"
    
    report += f"{direction}\n"
    report += f"**Average Change: {arrow} {avg_change:+.2f}%**\n\n"
    
    report += f"**Market Breakdown:**\n"
    report += f"🟢 Gainers: {gainers}\n"
    report += f"🔴 Losers: {losers}\n"
    report += f"⚪ Flat: {flat}\n\n"
    
    # Top 3 gainers and losers
    changes.sort(key=lambda x: x[1], reverse=True)
    
    report += f"**Top 3 Gainers:**\n"
    for i in range(min(3, len(changes))):
        symbol, pct = changes[i]
        if pct > 0:
            report += f"  {i+1}. {symbol}: +{pct:.2f}%\n"
    
    report += f"\n**Top 3 Decliners:**\n"
    changes.reverse()
    for i in range(min(3, len(changes))):
        symbol, pct = changes[i]
        if pct < 0:
            report += f"  {i+1}. {symbol}: {pct:.2f}%\n"
    
    return report

if __name__ == "__main__":
    print(generate_summary())
