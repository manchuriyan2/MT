import asyncio
import random
import time
import string
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import *
from database.database import *
from plugins.forcesub import *

SECONDS = TIME
PROTECT_CONTENT = False

WAIT_MSG = """<b>Processing ...</b>"""
REPLY_ERROR = """<blockquote><b>Use this command as a reply to any telegram message without any spaces.</b></blockquote>"""

@Bot.on_message(filters.command('start') & filters.private & subscribed & requested)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except Exception as e:
            print(f"Error adding user: {e}")
    
    if USE_SHORTLINK:
        if id not in ADMINS:
            try:
                verify_status = await get_verify_status(id)
                if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                    await update_verify_status(id, is_verified=False)
                if "verify_" in message.text:
                    _, token = message.text.split("_", 1)
                    if verify_status['verify_token'] != token:
                        return await message.reply("<blockquote><b>🔴 Your token verification is invalid or expired, hit /start command and try again<b></blockquote>")
                    await update_verify_status(id, is_verified=True, verified_time=time.time())
                    reply_markup = None if verify_status["link"] == "" else None
                    await message.reply(f"<blockquote><b>Hooray 🎉, your token verification is successful\n\n Now you can access all files for 24-hrs...</b></blockquote>", reply_markup=reply_markup, protect_content=False, quote=True)
            except Exception as e:
                print(f"Error verifying user: {e}")

    if len(message.text) > 7:
        if USE_SHORTLINK and id not in ADMINS:
            try:
                verify_status = await get_verify_status(id)
                if not verify_status['is_verified']:
                    return
            except Exception as e:
                print(f"Error checking verification status: {e}")
                return
        
        try:
            base64_string = message.text.split(" ", 1)[1]
            _string = await decode(base64_string)
            argument = _string.split("-")
            ids = []
            if len(argument) == 3:
                start, end = int(argument[1]), int(argument[2])
                ids = range(min(start, end), max(start, end) + 1)
            elif len(argument) == 2:
                ids = [int(argument[1])]
            
            temp_msg = await message.reply("Please wait... 🫷")
            messages = await get_messages(client, ids)
            await temp_msg.delete()
            snt_msgs = []
            for msg in messages:
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name) if bool(CUSTOM_CAPTION) & bool(msg.document) else "" if not msg.caption else msg.caption.html
                reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None
                try:
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)
                    snt_msgs.append(snt_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    snt_msgs.append(snt_msg)
                except Exception as e:
                    print(f"Error copying message: {e}")
            
            notification_msg = await message.reply(f"<blockquote><b>🔴 This file will be deleted in {SECONDS // 60} minutes. Please save or forward it to your saved messages before it gets deleted.</b></blockquote>")
            await asyncio.sleep(SECONDS)
            for snt_msg in snt_msgs:
                try:
                    await snt_msg.delete()
                except Exception as e:
                    print(f"Error deleting message: {e}")
            await notification_msg.edit(f"<blockquote><b>🗑️ Hey @{message.from_user.username} your file has been successfully deleted!</b></blockquote>")
            return
    if USE_SHORTLINK:
        if id in ADMINS:
            return
        try:
            verify_status = await get_verify_status(id)
            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_API_URL, SHORTLINK_API_KEY, f'https://t.me/{client.username}?start=verify_{token}')
                btn = [[InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)], [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)]] + ([[InlineKeyboardButton("💰 Purchase premium membership", callback_data="buy_prem")]] if USE_PAYMENT else [])
                await message.reply(f"<blockquote><b>ℹ️ Hi @{message.from_user.username}\nYour verification is expired, click on below button and complete the verification to\n <u>Get free access for 24-hrs</u></b></blockquote>", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)
        except Exception as e:
            print(f"Error handling shortlink: {e}")

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = []
    bot_id = client.me.id
    try:
        fsub_entry = await fsub.find_one({"_id": bot_id})
        req_db_entry = await req_db.find_one({"_id": bot_id})
    except Exception as e:
        print(f"Error fetching database entries: {e}")
        await message.reply("An error occurred while fetching data. Please try again later.")
        return

    fsub_channels = fsub_entry.get("channel_ids", []) if fsub_entry else []
    req_db_channels = req_db_entry.get("channel_ids", []) if req_db_entry else []

    for idx, force_sub_channel in enumerate(fsub_channels, start=1):
        try:
            invite_link = await client.create_chat_invite_link(chat_id=force_sub_channel)
            if invite_link and invite_link.invite_link:
                buttons.append(InlineKeyboardButton(f"Join Channel {idx}", url=invite_link.invite_link))
        except Exception as e:
            print(f"Error creating invite link for channel {force_sub_channel}: {e}")

    for idx, request_channel in enumerate(req_db_channels, start=len(fsub_channels)+1):
        try:
            invite_link = await client.create_chat_invite_link(chat_id=request_channel, creates_join_request=True)
            if invite_link and invite_link.invite_link:
                buttons.append(InlineKeyboardButton(f"Request Channel {idx}", url=invite_link.invite_link))
        except Exception as e:
            print(f"Error creating invite link for channel {request_channel}: {e}")

    button_rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    if len(message.command) > 1:
        button_rows.append([InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    if not button_rows:
        button_rows = [[InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}")]]
    
    try:
        await message.reply(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(button_rows),
            quote=True,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error sending reply: {e}")
        await message.reply("An error occurred while sending the message. Please try again later.")
     
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
        await asyncio.sleep(5)
        await msg.delete()


if USE_PAYMENT:
    @Bot.on_message(filters.command('add_prem') & filters.private & filters.user(ADMINS))
    async def add_user_premium_command(client: Bot, message: Message):
        while True:
            try:
                user_id = await client.ask(text="Enter id of user\nHit /cancel to cancel : ",chat_id = message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return  
            if user_id.text == "/cancel":
                await user_id.edit("Cancelled!")
                return
            try:
                await Bot.get_users(user_ids=user_id.text, self=client)
                break
            except:
                await user_id.edit("The admin id is incorrect.", quote = True)
                continue
        user_id = int(user_id.text)
        while True:
            try:
                timeforprem = await client.ask(text="<blockquote><b>Enter the amount of time Choose correctly.\n\nEnter 0 : For zero \nEnter 1 : For 7 days\nEnter 2 : For 1 month\nEnter 3 : For 3 months\nEnter 4 : For 6 months\nEnter 5 : For 1 year</b></blockquote>", chat_id=message.from_user.id, timeout=60)
            except Exception as e:
                print(e)
                return
            if not int(timeforprem.text) in [0, 1, 2, 3, 4, 5]:
                await message.reply("You have given wrong input.")
                continue
            else:
                break
        timeforprem = int(timeforprem.text)
        if timeforprem==0:
            timestring = "24 hrs"           
        elif timeforprem==1:
            timestring = "7 days"
        elif timeforprem==2:
            timestring = "1 month"
        elif timeforprem==3:
            timestring = "3 month"
        elif timeforprem==4:
            timestring = "6 month"
        elif timeforprem==5:
            timestring = "1 year"
        try:
            await increasepremtime(user_id, timeforprem)
            await message.reply("Premium added!")
            await client.send_message(
            chat_id=user_id,
            text=f"Premium plan of {timestring} added to your account.",
        )
        except Exception as e:
            print(e)
            await message.reply("Some error occurred.\nCheck logs...\nIf you got premium added message then its ok.")
        return
