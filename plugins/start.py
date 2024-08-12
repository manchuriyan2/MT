import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, DELAY
from database.database import add_user, del_user, full_userbase

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    text = message.text
    if len(text) > 7:
        await message.delete()
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        string = await decode(base64_string)
        argument = string.split("-")

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        else:
            return

        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return

        await temp_msg.delete()

        for msg in messages:
            caption = msg.caption.html if msg.caption else ""

            try:
                sent_message = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=msg.reply_markup,
                    protect_content=True
                )
                asyncio.create_task(delete_message_after_delay(client, message.from_user.id, sent_message.id, DELAY))
                await asyncio.sleep(1)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_message = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=msg.reply_markup,
                    protect_content=True
                )
                asyncio.create_task(delete_message_after_delay(client, message.from_user.id, sent_message.id, DELAY))
            except Exception as e:
                print(f"Error sending message: {e}")

        await message.reply("Broadcast completed. Files will be deleted in 10 minutes.")
        return

    await message.reply("Invalid command or parameters.")

     
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")


@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("Broadcasting Message...")
        status_msg = await message.reply("Broadcast Status:\nProcessing...")

        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

            # Update status every 10 users
            if total % 10 == 0:
                status = f"""<b>Broadcast Status</b>\n\nTotal Users: <code>{total}</code>\nSuccessful: <code>{successful}</code>\nBlocked Users: <code>{blocked}</code>\nDeleted Accounts: <code>{deleted}</code>\nUnsuccessful: <code>{unsuccessful}</code>"""
                await status_msg.edit(status)
        
        # Final status update
        status = f"""<b>Broadcast Completed</b>\n\nTotal Users: <code>{total}</code>\nSuccessful: <code>{successful}</code>\nBlocked Users: <code>{blocked}</code>\nDeleted Accounts: <code>{deleted}</code>\nUnsuccessful: <code>{unsuccessful}</code>"""
        await pls_wait.edit(status)
        await status_msg.delete()

    else:
        msg = await message.reply("Please reply to a message to broadcast.")
        await asyncio.sleep(8)
        await msg.delete()
