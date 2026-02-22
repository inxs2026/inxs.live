#!/usr/bin/env python3
"""
Stock Watchlist Report - Carlo's Portfolio Monitor
Fetches real-time prices and day performance for watchlist stocks
"""

import yfinance as yf
from datetime import datetime, time
import pytz

# Carlo's watchlist (Canadian stocks - add .TO suffix)
WATCHLIST = [
    "BCE.TO", "BMO.TO", "CM.TO", "CNQ.TO", "EIF.TO", "ENB.TO",
    "GLCC.TO", "MFC.TO", "NTR.TO", "PEY.TO", "PMIF.TO", "RY.TO",
    "SRU-UN.TO", "T.TO", "TD.TO", "TRP.TO", "WCP.TO", "ZWC.TO"
]

STOCK_NAMES = {
    "BCE.TO": "Bell Canada",
    "BMO.TO": "Bank of Montreal",
    "CM.TO": "CIBC",
    "CNQ.TO": "Canadian Natural",
    "EIF.TO": "Exchange Income",
    "ENB.TO": "Enbridge",
    "GLCC.TO": "Great Lakes Cheese",
    "MFC.TO": "Manulife Financial",
    "NTR.TO": "Nutrien",
    "PEY.TO": "Peyto Exploration",
    "PMIF.TO": "PIMCO Monthly",
    "RY.TO": "Royal Bank",
    "SRU-UN.TO": "SmartREIT",
    "T.TO": "Telus",
    "TD.TO": "TD Bank",
    "TRP.TO": "TC Energy",
    "WCP.TO": "Whitecap Resources",
    "ZWC.TO": "BMO Banks Covered Call"
}

def is_market_open():
    """Check if TSX is currently open (9:30 AM - 4:00 PM EST, Mon-Fri, excluding holidays)"""
    est = pytz.timezone('America/Toronto')
    now = datetime.now(est)
    
    # TSX Holidays 2026 (market closed)
    holidays_2026 = [
        (1, 1),   # New Year's Day
        (2, 16),  # Family Day
        (4, 3),   # Good Friday
        (5, 18),  # Victoria Day
        (7, 1),   # Canada Day
        (8, 3),   # Civic Holiday
        (9, 7),   # Labour Day
        (10, 12), # Thanksgiving
        (12, 25), # Christmas
        (12, 28), # Boxing Day (in lieu)
    ]
    
    # Check if holiday
    if (now.month, now.day) in holidays_2026:
        return False
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if within market hours (9:30 AM - 4:00 PM)
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now.time()
    
    return market_open <= current_time < market_close

def get_market_comment(symbol, change_pct, price):
    """Generate brief one-line comment based on performance"""
    if abs(change_pct) < 0.5:
        return "Flat trading"
    elif change_pct > 2:
        return "Strong rally"
    elif change_pct > 1:
        return "Good gains"
    elif change_pct > 0.5:
        return "Modest uptick"
    elif change_pct < -2:
        return "Sharp decline"
    elif change_pct < -1:
        return "Selling pressure"
    else:
        return "Minor pullback"

def generate_report():
    """Fetch stock data and generate formatted report"""
    
    est = pytz.timezone('America/Toronto')
    now = datetime.now(est)
    report_time = now.strftime("%I:%M %p EST")
    report_date = now.strftime("%A, %B %d, %Y")
    
    market_open = is_market_open()
    
    report = f"📊 **STOCK WATCHLIST REPORT**\n"
    report += f"{report_date} • {report_time}\n"
    
    if market_open:
        report += "🟢 **MARKET OPEN** (Live Prices)\n"
    else:
        report += "🔴 **MARKET CLOSED** (Last Close)\n"
    
    report += "=" * 50 + "\n\n"
    
    gainers = []
    losers = []
    gainer_count = 0
    loser_count = 0
    flat_count = 0
    total_change_pct = 0
    valid_stocks = 0
    
    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            
            if market_open:
                # During market hours: get intraday data
                data = ticker.history(period="1d", interval="1m")
                
                if data.empty:
                    # Fallback to basic info if intraday fails
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                    open_price = info.get('regularMarketOpen') or info.get('open', current_price)
                else:
                    current_price = data['Close'].iloc[-1]
                    open_price = data['Open'].iloc[0]
            else:
                # Market closed: show previous close
                info = ticker.info
                current_price = info.get('previousClose', 0)
                open_price = info.get('regularMarketOpen') or info.get('open', current_price)
            
            if current_price == 0:
                report += f"❓ **{symbol.replace('.TO', '')}** - No data available\n\n"
                continue
            
            change = current_price - open_price
            change_pct = (change / open_price) * 100 if open_price != 0 else 0
            
            # Track for portfolio summary
            total_change_pct += change_pct
            valid_stocks += 1
            
            # Arrow and color
            if change_pct > 0.1:
                arrow = "🟢 ↑"
                gainers.append((symbol, change_pct))
                gainer_count += 1
            elif change_pct < -0.1:
                arrow = "🔴 ↓"
                losers.append((symbol, change_pct))
                loser_count += 1
            else:
                arrow = "⚪ →"
                flat_count += 1
            
            comment = get_market_comment(symbol, change_pct, current_price)
            name = STOCK_NAMES.get(symbol, symbol.replace('.TO', ''))
            
            if market_open:
                report += f"{arrow} **{symbol.replace('.TO', '')}** - {name}\n"
                report += f"   ${current_price:.2f} ({change:+.2f}$) • {comment}\n\n"
            else:
                # When closed, just show last close price
                report += f"⚪ **{symbol.replace('.TO', '')}** - {name}\n"
                report += f"   ${current_price:.2f} (Last Close)\n\n"
            
        except Exception as e:
            report += f"❌ **{symbol.replace('.TO', '')}** - Error: {str(e)}\n\n"
    
    # Build portfolio snapshot and insert it at the top
    if valid_stocks > 0 and market_open:
        avg_change = total_change_pct / valid_stocks
        
        # Direction indicator
        if avg_change > 0.5:
            snapshot_arrow = "🟢 ↑"
        elif avg_change < -0.5:
            snapshot_arrow = "🔴 ↓"
        else:
            snapshot_arrow = "⚪ →"
        
        snapshot_line = f"\n**📊 PORTFOLIO SNAPSHOT**\n{snapshot_arrow} Average: {avg_change:+.2f}% | 🟢 {gainer_count} Up | 🔴 {loser_count} Down | ⚪ {flat_count} Flat\n\n"
        
        # Insert snapshot after the first "==" line
        report = report.replace("=" * 50 + "\n\n", "=" * 50 + snapshot_line, 1)
    
    # Summary (only during market hours)
    if market_open and (gainers or losers):
        report += "=" * 50 + "\n"
        report += f"**MARKET MOVERS**\n"
        
        if gainers:
            gainers.sort(key=lambda x: x[1], reverse=True)
            top_gainer = gainers[0]
            report += f"🏆 Top Gainer: {top_gainer[0].replace('.TO', '')} (+{top_gainer[1]:.2f}%)\n"
        
        if losers:
            losers.sort(key=lambda x: x[1])
            top_loser = losers[0]
            report += f"📉 Top Loser: {top_loser[0].replace('.TO', '')} ({top_loser[1]:.2f}%)\n"
    
    report += f"\n✅ Next update: {'3:00 PM' if now.hour < 15 else 'Tomorrow 10:00 AM'} EST"
    
    return report

if __name__ == "__main__":
    print(generate_report())
