#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"○ 𝖢𝗋𝖾𝖺𝗍𝗈𝗋 : <a href='tg://user?id={OWNER_ID}'>𝖳𝗁𝗂𝗌 𝖯𝖾𝗋𝗌𝗈𝗇</a>\n○ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 : <code>𝖯𝖺𝗒𝗍𝗁𝗈𝗇 𝟥</code>\n○ 𝖲𝗈𝗎𝗋𝖼𝖾 𝖢𝗈𝖽𝖾 : <a href='tg://user?id={OWNER_ID}'>𝖯𝖺𝗂𝖽</a>\n○ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 : <a href='https://t.me/Vip_studios'>𝖵𝖨𝖯 𝖲𝗍𝗎𝖽𝗂𝗈𝗌</a>\n○ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖦𝗋𝗈𝗎𝗉 : <a href='https://t.me/+UoOAfvRc8R0zNjg1'>𝖣𝗂𝗌𝖼𝗎𝗌𝗌𝗂𝗈𝗇 𝖢𝗁𝖺𝗍</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
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
