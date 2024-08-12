import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMINS, FORCE_MSG
from database.database import *
from bot import Bot
from helper_func import *

# Add fsub in db 
@Bot.on_message(filters.command('addfsub') & filters.private & filters.user(ADMINS))
async def add_fsub(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to add as fsub in the bot. If adding more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    bot_id = client.me.id

    for channel_id in channel_ids:
        try:
            print(channel_id)
            test_msg = await client.send_message(int(channel_id), "test")
            await test_msg.delete()
        except:
            await message.reply(f"Please make admin bot in channel_id: {channel_id} or double check the id.")
            return

    fsub.update_one(
        {"_id": bot_id},
        {"$addToSet": {"channel_ids": {"$each": channel_ids}}},
        upsert=True
    )
    await message.reply(f"Added channel IDs: {', '.join(channel_ids)}")

### Deleting Channel IDs
@Bot.on_message(filters.command('delfsub') & filters.private & filters.user(ADMINS))
async def del_fsub(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to delete from fsub in the bot. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    bot_id = client.me.id

    fsub.update_one(
        {"_id": bot_id},
        {"$pull": {"channel_ids": {"$in": channel_ids}}}
    )
    await message.reply(f"Deleted channel IDs: {', '.join(channel_ids)}")

### Showing All Channel IDs
@Bot.on_message(filters.command('showfsub') & filters.private & filters.user(ADMINS))
async def show_fsub(client, message):
    bot_id = client.me.id
    fsub_entry = fsub.find_one({"_id": bot_id})

    if fsub_entry and "channel_ids" in fsub_entry:
        channel_ids = fsub_entry["channel_ids"]
        channel_info = []
        for channel_id in channel_ids:
            chat = await client.get_chat(int(channel_id))
            channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**")
        if channel_info:
            await message.reply(f"**Force Subscribed channels:**\n" + "\n".join(channel_info), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        else:
            await message.reply("No subscribed channels found.")
    else:
        await message.reply("No subscribed channel IDs found.")

# Add IDs in db
@Bot.on_message(filters.command('addreq') & filters.private & filters.user(ADMINS))
async def add_req(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to add. If adding more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]

    added_channels = []
    for channel_id in channel_ids:
        try:
            test_msg = await client.send_message(int(channel_id), "test")
            await test_msg.delete()
            req_db.update_one({"_id": channel_id}, {"$set": {"_id": channel_id}}, upsert=True)
            added_channels.append(channel_id)
        except Exception as e:
            await message.reply(f"Please make the bot an admin in channel ID: {channel_id} or double-check the ID. Error: {e}")
            return

    if added_channels:
        await message.reply(f"Added channel IDs: {', '.join(added_channels)}")

# Deleting Channel IDs
@Bot.on_message(filters.command('delreq') & filters.private & filters.user(ADMINS))
async def del_req(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to delete from fsub in the bot. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]

    deleted_channels = []
    for channel_id in channel_ids:
        try:
            result = req_db.delete_one({"_id": channel_id})
            if result.deleted_count > 0:
                deleted_channels.append(channel_id)
            else:
                await message.reply(f"Channel ID: {channel_id} not found in the database. Please double-check the ID.")
        except Exception as e:
            await message.reply(f"Error deleting channel ID: {channel_id}. Error: {e}")

    if deleted_channels:
        await message.reply(f"Deleted channel IDs: {', '.join(deleted_channels)}")

# Showing All Channel IDs
@Bot.on_message(filters.command('showreq') & filters.private & filters.user(ADMINS))
async def show_req(client, message):
    req_entries = req_db.find({})

    channel_info = []
    for entry in req_entries:
        channel_id = entry["_id"]
        user_count = len(entry.get("User_INFO", []))
        try:
            chat = await client.get_chat(int(channel_id))
            channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**: {user_count} user requests")
        except Exception as e:
            channel_info.append(f"→ **Channel ID: {channel_id}**: {user_count} users (Error: {e})")

    if channel_info:
        await message.reply(f"**Channels Added For Request Count:**\n" + "\n".join(channel_info), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        await message.reply("No channels found.")

@Bot.on_chat_join_request()
async def join_reqs(client, join_req: ChatJoinRequest):
    channel_id = join_req.chat.id
    
    if req_db.find_one({"_id": channel_id}):
        user_data = {
            "user_id": join_req.from_user.id,
            "first_name": join_req.from_user.first_name,
            "username": join_req.from_user.username,
            "date": join_req.date
        }

        # Update USER_INFO in db
        req_db.update_one(
            {"_id": channel_id},
            {"$push": {"User_INFO": user_data}},
            upsert=True
        )

# Resetting User_INFO for a Channel ID
@Bot.on_message(filters.command('rreset') & filters.private & filters.user(ADMINS))
async def reset_req(client, message):
    if len(message.command) != 2:
        await message.reply("Please provide a single channel ID to reset user info.")
        return

    channel_id = message.text.split()[1]
    try:
        result = req_db.update_one({"_id": channel_id}, {"$unset": {"User_INFO": ""}})
        if result.modified_count > 0:
            await message.reply(f"User info reset for channel ID: {channel_id}")
        else:
            await message.reply(f"Channel ID: {channel_id} not found in the database. Please double-check the ID.")
    except Exception as e:
        await message.reply(f"Error resetting user info for channel ID: {channel_id}. Error: {e}")
