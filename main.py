from chatbot import get_answer
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from config import Config
from models import Message as SavedMessage
from database import engine, Base
import json
import asyncio

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)

bot = AsyncTeleBot(Config.BOT_TOKEN)

@bot.message_handler(commands=['start'])
async def start_command(message: Message):
    if not message.chat.id == int(Config.ADMIN_ID):
        await bot.send_message(
            chat_id=message.chat.id,
            text="Salom! Yangi O‘zbekiston Universiteti haqida savollaringiz bormi? Sizga yordam berishga tayyorman. Savolingizni yozing.",
            reply_markup=None
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Salom! Siz adminstrator sifatida bot bilan ishlayapsiz. Sizga uzatilgan xabarlarga javob berish uchun botni ishlatishingiz mumkin.",
            reply_markup=None
        )

@bot.message_handler(content_types=['text'], chat_types=['private'])
async def handle_text_message(message: Message):

    if not message.chat.id == int(Config.ADMIN_ID):
        await bot.send_chat_action(
            chat_id=message.chat.id,
            action='typing'
        )
       
        question = message.text
        answer = get_answer(question)
        
        if answer.output_text == "FORWARD_TO_ADMIN":
        
            msg = await bot.forward_message(
                chat_id=Config.ADMIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            SavedMessage.create(
                message=json.dumps(message.json),
                forwarded_id=msg.message_id
            )
            await bot.send_message(
                message.chat.id,
                text="Savolingizga birozdan so‘ng javob beramiz. Iltimos kuting.",
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=answer.output_text
            )

    else:
        if message.reply_to_message:
            forwarded_message = SavedMessage.get(forwarded_id=message.reply_to_message.message_id)
            if forwarded_message:
                original_message = json.loads(forwarded_message.message)
                original_chat_id = original_message['chat']['id']
                await bot.copy_message(
                    chat_id=original_chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_to_message_id=original_message['message_id']
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Xatolik: Savol topilmadi."
                )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Iltimos, javob berish uchun avvalgi xabarga javob bering."
            )
            

if __name__ == "__main__":
    asyncio.run(bot.polling())