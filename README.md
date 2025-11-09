# Telegram pseudo-24/7 bot on GitHub Actions

1. Fork this repo  
2. Settings → Secrets → New repository secret  
   Name: `BOT_TOKEN`  Value: `<your-telegram-bot-token>`  
3. Actions tab → enable workflows  
4. Bot answers `/start` and echoes any text.  
   Job runs every 5 min → 2000 free minutes/month ≈ 6.6 days continuous.  
   Add UptimeRobot ping inside `bot.py` if you need external monitoring.
