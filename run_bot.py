import os
import asyncio
import dotenv
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from backend.telegram_bot import start_command, handle_text, handle_voice
from backend.database import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    dotenv.load_dotenv()
    await init_db()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Missing TELEGRAM_BOT_TOKEN")
        return
        
    print("Starting JanSetu Telegram Bot in Standalone Mode...")
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    
    await application.initialize()
    await application.start()
    
    print("Bot is actively polling for messages!")
    await application.updater.start_polling(drop_pending_updates=True)
    
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("Stopping...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
