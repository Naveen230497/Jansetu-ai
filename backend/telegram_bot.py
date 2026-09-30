import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from . import database, gemini_service
from .models import CitizenRequest, CategoryEnum, SentimentEnum, SourceEnum
from .live_feed import manager

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Welcome to JanSetu AI! \n"
        "Please send your infrastructure feedback or complaints via text or voice message.\n\n"
        "JanSetu AI में आपका स्वागत है!\n"
        "कृपया अपनी बुनियादी ढांचा प्रतिक्रिया या शिकायतें टेक्स्ट या वॉयस मैसेज के माध्यम से भेजें।"
    )
    await update.message.reply_text(msg)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        classification = gemini_service.classify_text(text)
        req = CitizenRequest(
            raw_text=text,
            translated_text=classification.translated_text,
            language_detected=classification.language,
            category=classification.category,
            location_district=classification.district,
            location_state=classification.state,
            urgency=classification.urgency,
            sentiment=classification.sentiment,
            latitude=classification.latitude,
            longitude=classification.longitude,
            source=SourceEnum.TELEGRAM
        )
        req_id = await database.insert_request(req)
        
        # Broadcast real-time
        dump = req.model_dump()
        dump['id'] = req_id
        dump['timestamp'] = dump['timestamp'].isoformat() if dump.get('timestamp') else None
        await manager.broadcast_new_request(dump)
        
        reply = f"Thank you. Your feedback regarding {classification.category.value} in {classification.district} has been recorded.\nधन्यवाद। आपकी प्रतिक्रिया दर्ज कर ली गई है।"
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error handling text: {e}")
        await update.message.reply_text("Sorry, we could not process your request at this time.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        voice = update.message.voice or update.message.audio
        file = await context.bot.get_file(voice.file_id)
        
        # Download as bytearray
        audio_bytes = await file.download_as_bytearray()
        
        classification = gemini_service.classify_audio(bytes(audio_bytes), voice.mime_type or 'audio/ogg')
        req = CitizenRequest(
            raw_text="[Voice Message]",
            translated_text=classification.translated_text,
            language_detected=classification.language,
            category=classification.category,
            location_district=classification.district,
            location_state=classification.state,
            urgency=classification.urgency,
            sentiment=classification.sentiment,
            latitude=classification.latitude,
            longitude=classification.longitude,
            source=SourceEnum.TELEGRAM
        )
        req_id = await database.insert_request(req)
        
        # Broadcast real-time
        dump = req.model_dump()
        dump['id'] = req_id
        dump['timestamp'] = dump['timestamp'].isoformat() if dump.get('timestamp') else None
        await manager.broadcast_new_request(dump)
        
        reply = f"Voice feedback received regarding {classification.category.value} in {classification.district}.\nवॉयस फीडबैक प्राप्त हुआ।"
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error handling voice: {e}")
        await update.message.reply_text("Sorry, we could not process your voice message.")

# Global reference
bot_app = None

def setup_bot(app: FastAPI):
    global bot_app
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("No TELEGRAM_BOT_TOKEN provided, skipping bot setup.")
        return None

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    
    bot_app = application
    return application

async def start_telegram_bot():
    if bot_app and not bot_app._initialized:
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)

async def stop_telegram_bot():
    if bot_app and bot_app._initialized:
        if bot_app.updater and bot_app.updater.running:
            await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
