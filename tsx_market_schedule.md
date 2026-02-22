# TSX Market Schedule

## Regular Trading Hours
**Monday - Friday:** 9:30 AM - 4:00 PM EST
**Weekends:** CLOSED

## 2026 Market Holidays (TSX CLOSED)

1. **New Year's Day** - Thursday, January 1, 2026
2. **Family Day** - Monday, February 16, 2026
3. **Good Friday** - Friday, April 3, 2026
4. **Victoria Day** - Monday, May 18, 2026
5. **Canada Day** - Wednesday, July 1, 2026
6. **Civic Holiday** - Monday, August 3, 2026
7. **Labour Day** - Monday, September 7, 2026
8. **Thanksgiving Day** - Monday, October 12, 2026
9. **Christmas Day** - Friday, December 25, 2026
10. **In Lieu of Boxing Day** - Monday, December 28, 2026

### Early Close
**Christmas Eve** - Thursday, December 24, 2026
- TSX/TSXV: 1:00 PM EST
- ALPHA/ALPHA X/DRK: 1:30 PM EST

## Stock Report Impact

**Automated reports (10 AM & 3 PM):**
- Run Monday-Friday only (already configured in cron)
- Will show "MARKET CLOSED" on holidays
- No manual intervention needed - script detects market status

**Manual on-demand reports:**
- Available anytime
- Will display last close prices when market is closed

## Upcoming Holidays (2026)
- ❌ Family Day - Feb 16 (ALREADY PASSED in our timeline - Feb 19)
- ❌ Good Friday - Apr 3
- ❌ Victoria Day - May 18
- ❌ Canada Day - Jul 1
- ❌ Civic Holiday - Aug 3
- ❌ Labour Day - Sep 7
- ❌ Thanksgiving - Oct 12
- ❌ Christmas - Dec 25
- ❌ Boxing Day (in lieu) - Dec 28

## Notes
- Market is closed on Canadian statutory holidays
- Early close on Christmas Eve at 1:00 PM
- Automated reports configured to run Mon-Fri only
- Script automatically detects if market is open/closed
- ~15 minute data delay on all free quotes

Source: https://www.tsx.com/en/trading/calendars-and-trading-hours/calendar
Last updated: Feb 19, 2026
