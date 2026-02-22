# REMINDERS GUIDE

## How to Set Reminders

Reminders automatically appear in your morning briefing at 7 AM.

### Where to Add Reminders

**File:** `memory/reminders.md`

### Formats

1. **Specific Date:**
   ```
   - [2026-02-16] Call dentist for checkup
   ```

2. **Urgent (shows every day until removed):**
   ```
   - [urgent] Sign contract by Friday
   ```

3. **Today (shows only today):**
   ```
   - [today] Pick up package from post office
   ```

### Examples

```markdown
# REMINDERS

## Your Reminders:

- [2026-02-17] Tax documents due
- [urgent] Review racing performance database
- [today] Call mom
- [2026-02-20] Dentist appointment 2 PM
```

### Quick Commands

**Add a reminder:**
```bash
echo "- [2026-02-20] Remember this thing" >> ~/.openclaw/workspace/memory/reminders.md
```

**View current reminders:**
```bash
cat ~/.openclaw/workspace/memory/reminders.md
```

**Via voice/text to Chi:**
- "Remind me tomorrow to call John"
- "Add urgent reminder: review contract"

## How It Works

1. Reminders appear **first** in your morning briefing (7 AM)
2. System checks:
   - `memory/reminders.md` for date/urgent/today tags
   - `memory/active-tasks.md` for urgent items
3. Only matching reminders show up that day
4. Remove completed reminders manually from the file

## Tips

✅ **Do:**
- Use specific dates for important deadlines
- Mark time-sensitive items as [urgent]
- Remove completed reminders to keep list clean

❌ **Don't:**
- Leave old reminders in the file
- Use vague descriptions
- Forget to include [date] or [urgent] tags

---

**Your morning briefing now includes:**
1. ⏰ REMINDERS (if any)
2. 🌤️ WEATHER
3. 🇨🇦 CANADA NEWS
4. 🇺🇸 USA NEWS
5. 📈 STOCK MARKET
6. 🏇 RACING (Thu-Sun)
