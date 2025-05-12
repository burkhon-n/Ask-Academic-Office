from chatbot import get_answer
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from config import Config
import asyncio

bot = AsyncTeleBot(Config.BOT_TOKEN)

@bot.message_handler(commands=['start'])
async def start_command(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Salom! Yangi O‘zbekiston Universiteti haqida savollaringiz bormi? Sizga yordam berishga tayyorman. Savolingizni yozing.",
        reply_markup=None
    )

@bot.message_handler(content_types=['text'], chat_types=['private'])
async def handle_text_message(message: Message):

    if not message.chat.id == Config.ADMIN_ID:
       
        question = message.text
        answer = get_answer(question)
        
        if answer.output_text == "FORWARD_TO_ADMIN":
        
            await bot.forward_message(
                chat_id=Config.ADMIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
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


if __name__ == "__main__":
    asyncio.run(bot.polling())