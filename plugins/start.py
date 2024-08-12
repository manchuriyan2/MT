import re
import os
import asyncio
import random
import time
import base64
import string
import logging

from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import *
from helper_func import *
from database.database import *

SECONDS = TIME 
TUT_VID = f"{TUT_VID}"
PROTECT_CONTENT = False

WAIT_MSG = """<b>Processing ...</b>"""
REPLY_ERROR = """<blockquote><b>Use this command as a replay to any telegram message without any spaces.</b></blockquote>"""


@Bot.on_message(filters.command('start') & filters.private & subscribed & subscribed2)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    if USE_SHORTLINK:
        for i in range(1):
            if id in ADMINS:
                continue
            verify_status = await get_verify_status(id)
            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                await update_verify_status(id, is_verified=False)
            if "verify_" in message.text:
                _, token = message.text.split("_", 1)
                if verify_status['verify_token'] != token:
                    return await message.reply("<blockquote><b>🔴 Your token verification is invalid or Expired, Hit /start command and try again<b></blockquote>")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                if verify_status["link"] == "":
                    reply_markup = None
                await message.reply(f"<blockquote><b>Hooray 🎉, your token verification is successful\n\n Now you can access all files for 24-hrs...</b></blockquote>", reply_markup=reply_markup, protect_content=False, quote=True)
    if len(message.text) > 7:
        for i in range(1):
            if USE_SHORTLINK : 
                if id not in ADMINS:
                    try:
                        if not verify_status['is_verified']:
                            continue
                    except:
                        continue
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except:
                    return
                if start <= end:
                    ids = range(start, end+1)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except:
                    return
            temp_msg = await message.reply("Please wait... 🫷")
            try:
                messages = await get_messages(client, ids)
            except:
                await message.reply_text("Something went wrong..!")
                return
            await temp_msg.delete()
            snt_msgs = []
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,    filename=msg.document.file_name)
                else:   
                    caption = "" if not msg.caption else msg.caption.html   
                if DISABLE_CHANNEL_BUTTON:  
                    reply_markup = msg.reply_markup 
                else:   
                    reply_markup = None 
                try:    
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)    
                    snt_msgs.append(snt_msg)    
                except FloodWait as e:  
                    await asyncio.sleep(e.x)    
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode= ParseMode.HTML,  reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    snt_msgs.append(snt_msg)    
                except: 
                    pass    
                
            notification_msg = await message.reply(f"<blockquote><b>🔴 This file will be  deleted in  {SECONDS // 60} minutes. Please save or forward it to your saved messages before it gets deleted.</b></blockquote>")
            await asyncio.sleep(SECONDS)    
            for snt_msg in snt_msgs:    
                try:    
                    await snt_msg.delete()  
                except: 
                    pass    
            await notification_msg.edit(f"<blockquote><b>🗑️ Hey @{message.from_user.username} your file has been successfully deleted!</b></blockquote>")  
            return  
    if (1 == 1):
        for i in range(1):
            if USE_SHORTLINK : 
                if id not in ADMINS:
                    try:
                        if not verify_status['is_verified']:
                            continue
                    except:
                        continue
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🦋 More", callback_data="about"),
                        InlineKeyboardButton("📴 Close", callback_data="close")
                    ]
                ]
            )
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )
            return
    if (1 == 1):
        if USE_SHORTLINK : 
            if id in ADMINS:
                return
            verify_status = await get_verify_status(id)
            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_API_URL, SHORTLINK_API_KEY,f'https://t.me/{client.username}?start=verify_{token}')
                if USE_PAYMENT:
                    btn = [
                    [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                    [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)],
                    [InlineKeyboardButton("💰 Purchase premium membership", callback_data="buy_prem")]
                    ]
                else:
                    btn = [
                    [InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=link)],
                    [InlineKeyboardButton('🦋 Tutorial', url=TUT_VID)]
                    ]
                await message.reply(f"<blockquote><b>ℹ️ Hi @{message.from_user.username}\nYour verification is expired, click on below button and complete the verification to\n <u>Get free access for 24-hrs</u></b></blockquote>", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)
                return
        return

     
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
