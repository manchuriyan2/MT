from pyrogram import __version__
from bot import Bot
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<blockquote>Bot Developer: @StupidBoi69\nMore Bots: @jr_bots\n\n📞 To resolve any issues contact to bot developer 🍷🗿.</blockquote>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📴 Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    elif data == "buy_prem":
        await query.message.edit_text(
            text=f"<blockquote><b>⏺️ Hello {query.from_user.username}\n\n💰 Premium Membership Plans 💰\n\n↪️ ₹49 INR For 7 Days\n↪️ ₹149 INR For 1 Month\n↪️ ₹349 INR For 3 Months\n\n💳 UPI ID: nehasaini5103@okicici\n👛 QR Code - https://graph.org/file/fd1487021734ee86c78b4.jpg\n\nIf payment is not getting sent on above given QR code then inform admin, he will give you new QR code\n\nMust Send Screenshot after payment</b></blockquote>",
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup(
                [   
                    [
                        InlineKeyboardButton("💳 Send Payment Screenshot", url=f"https://t.me/StupidBoi69")
                    ],
                    [
                        InlineKeyboardButton("📴 Close", callback_data = "close")
                    ]
                ]
            )
        )            
