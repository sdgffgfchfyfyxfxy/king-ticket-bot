from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import (
    get_stats, get_all_users, get_tickets_by_status, 
    get_all_users_details, get_ticket_by_id, add_reply, close_ticket
)
from keyboards.keyboards import admin_panel_keyboard, admin_ticket_action_keyboard
from states.states import AdminStates
from config import ADMIN_ID

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.answer("شما دسترسی به پنل ادمین ندارید!", show_alert=True)
        return
        
    try:
        await query.message.edit_text("⚙️ **پنل مدیریت پیشرفته ربات**", reply_markup=admin_panel_keyboard(), parse_mode="Markdown")
    except Exception:
        await query.message.reply_text("⚙️ **پنل مدیریت پیشرفته ربات**", reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    users, open_t, closed_t, total_m = await get_stats()
    text = (
        f"📊 **آمار کلی ربات:**\n\n"
        f"👥 تعداد کل کاربران: {users}\n"
        f"📂 تعداد تیکت‌های باز: {open_t}\n"
        f"📁 تعداد تیکت‌های بسته: {closed_t}\n"
        f"💬 تعداد کل پیام‌ها و پاسخ‌ها: {total_m}"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]])
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_open_tickets_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    tickets = await get_tickets_by_status("Open")
    if not tickets:
        text = "📂 هیچ تیکت بازی وجود ندارد."
    else:
        text = "📂 **تیکت‌های باز:**\n\n"
        for t in tickets:
            text += f"🔹 تیکت #{t['ticket_id']} | کاربر: {t['user_id']} | عنوان: {t['title']}\n"
            
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]])
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_closed_tickets_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    tickets = await get_tickets_by_status("Closed")
    if not tickets:
        text = "📁 هیچ تیکت بسته‌ای وجود ندارد."
    else:
        text = "📁 **تیکت‌های بسته (آخرین‌ها):**\n\n"
        for t in tickets[:20]:
            text += f"🔸 تیکت #{t['ticket_id']} | کاربر: {t['user_id']} | عنوان: {t['title']}\n"
            
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]])
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    users = await get_all_users_details()
    text = f"👥 **لیست کاربران (تعداد کل: {len(users)}):**\n\n"
    for u in users[:15]:
        text += f"• {u['full_name']} (@{u['username'] if u['username'] else 'ندارد'}) - ID: `{u['user_id']}`\n"
        
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]])
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    text = "⚙️ **تنظیمات ربات:**\n\nوضعیت دیتابیس: متصل (SQLite)\nنسخه کتابخانه: python-telegram-bot v21+\nهاست: Railway"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]])
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
        
    await query.message.reply_text("📨 لطفاً متن یا پیام همگانی خود را ارسال کنید:")
    return AdminStates.BROADCAST

async def admin_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
        
    text = update.message.text
    users = await get_all_users()
    success = 0
    failed = 0
    
    status_msg = await update.message.reply_text(f"⏳ در حال ارسال پیام همگانی به {len(users)} کاربر...")
    
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
        except Exception:
            failed += 1
            
    await status_msg.edit_text(f"✅ ارسال پیام همگانی پایان یافت.\n\nموفق: {success}\nناموفق: {failed}")
    return ConversationHandler.END

async def admin_reply_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
        
    data = query.data
    ticket_id = int(data.split("_")[-1])
    context.user_data['admin_reply_ticket_id'] = ticket_id
    
    ticket = await get_ticket_by_id(ticket_id)
    if not ticket:
        await query.message.reply_text("❌ تیکت مورد نظر یافت نشد.")
        return ConversationHandler.END
        
    context.user_data['admin_reply_target_user'] = ticket['user_id']
    
    await query.message.reply_text(f"💬 حالت پاسخ به تیکت #{ticket_id} فعال شد.\nپیام، عکس، فایل یا ویدیو خود را بفرستید:")
    return AdminStates.REPLYING

async def admin_send_reply_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
        
    msg = update.message
    ticket_id = context.user_data.get('admin_reply_ticket_id')
    target_user_id = context.user_data.get('admin_reply_target_user')
    
    if not ticket_id or not target_user_id:
        await msg.reply_text("❌ خطا در تعیین تیکت هدف.")
        return ConversationHandler.END
        
    file_type = "text"
    file_id = ""
    caption = msg.text or msg.caption or ""
    
    if msg.photo:
        file_type = "photo"
        file_id = msg.photo[-1].file_id
    elif msg.video:
        file_type = "video"
        file_id = msg.video.file_id
    elif msg.voice:
        file_type = "voice"
        file_id = msg.voice.file_id
    elif msg.document:
        file_type = "document"
        file_id = msg.document.file_id
        
    await add_reply(ticket_id, ADMIN_ID, file_type, file_id, caption)
    
    bot = context.bot
    full_cap = f"🛠 [پاسخ ادمین به تیکت #{ticket_id}]:\n{caption}"
    
    try:
        if file_type == "photo":
            await bot.send_photo(chat_id=target_user_id, photo=file_id, caption=full_cap)
        elif file_type == "video":
            await bot.send_video(chat_id=target_user_id, video=file_id, caption=full_cap)
        elif file_type == "voice":
            await bot.send_voice(chat_id=target_user_id, voice=file_id, caption=full_cap)
        elif file_type == "document":
            await bot.send_document(chat_id=target_user_id, document=file_id, caption=full_cap)
        else:
            await bot.send_message(chat_id=target_user_id, text=full_cap)
            
        await msg.reply_text("✅ پاسخ با موفقیت برای کاربر ارسال شد.")
    except Exception as e:
        await msg.reply_text(f"❌ خطا در ارسال پیام به کاربر: {e}")
        
    return AdminStates.REPLYING

async def admin_close_ticket_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        return
        
    data = query.data
    ticket_id = int(data.split("_")[-1])
    
    ticket = await get_ticket_by_id(ticket_id)
    if not ticket:
        await query.message.reply_text("❌ تیکت یافت نشد.")
        return
        
    await close_ticket(ticket_id)
    try:
        await query.message.edit_text(f"🔒 تیکت #{ticket_id} بسته شد.")
    except Exception:
        await query.message.reply_text(f"🔒 تیکت #{ticket_id} بسته شد.")
    
    try:
        await context.bot.send_message(chat_id=ticket['user_id'], text=f"✅ تیکت شماره #{ticket_id} شما بسته شد.")
    except Exception:
        pass