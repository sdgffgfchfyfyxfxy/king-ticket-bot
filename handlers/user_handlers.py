from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import (
    add_user, get_user_open_tickets_count, create_ticket, 
    add_ticket_message, get_user_tickets, get_ticket_by_id, 
    get_ticket_messages, get_ticket_replies
)
from keyboards.keyboards import (
    main_menu_keyboard, confirm_ticket_keyboard, edit_ticket_keyboard,
    user_tickets_keyboard, view_ticket_keyboard, admin_ticket_action_keyboard
)
from states.states import TicketStates
from config import ADMIN_ID

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.full_name, user.username)
    
    try:
        await update.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
    
    text = (
        "سلام رفیق 😎👋\n\n"
        "🎟 به بات تیکت امن kingk-configs خوش اومدی 🫴😑\n\n"
        "💨 اینجا میتونی خیلی امن و راحت تیکت ثبت کنی و ادمین از داخل همینجا بهت پاسخ بده 🤌🗿\n\n"
        "🫷🫪 ولی اگر برای خرید کانفیگ یا دریافت کانفیگ رایگان اومدی، لطفاً مستقیم به پشتیبانی پیام بده:\n\n"
        "@mr1kk1rn0 🚀"
    )
    is_admin = (user.id == ADMIN_ID)
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    is_admin = (user.id == ADMIN_ID)
    text = "منوی اصلی ربات:"
    try:
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(is_admin))
    except Exception:
        await query.message.reply_text(text, reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END

async def create_ticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    open_count = await get_user_open_tickets_count(user.id)
    if open_count >= 3:
        await query.message.reply_text("❌ شما در حال حاضر ۳ تیکت باز دارید و نمی‌توانید تیکت جدیدی ایجاد کنید.")
        return ConversationHandler.END
        
    context.user_data['ticket_messages'] = []
    
    try:
        await query.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
        
    await query.message.reply_text(
        "✔️ شما درحال ایجاد تیکت جدید هستید ⚠️\n\nیک نام برای تیکت خود ارسال کنید ♻️"
    )
    return TicketStates.TITLE

async def receive_ticket_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    if not title or len(title.strip()) == 0:
        await update.message.reply_text("عنوان تیکت نمی‌تواند خالی باشد. لطفاً یک نام معتبر ارسال کنید:")
        return TicketStates.TITLE
        
    context.user_data['ticket_title'] = title.strip()
    
    try:
        await update.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
        
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تایید", callback_data="show_confirm")]])
    await update.message.reply_text(
        "🎁 داش، حالا متن، عکس، ویدیو یا فایل تیکتت رو بفرست همینجا ✨️\n\n"
        "(حداکثر ۳ پیام. پس از ارسال پیام‌ها، دکمه زیر را بزنید)",
        reply_markup=kb
    )
    return TicketStates.CONTENT

async def receive_ticket_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    messages = context.user_data.get('ticket_messages', [])
    
    if len(messages) >= 3:
        await msg.reply_text("⚠️ حداکثر ۳ پیام می‌توانید ارسال کنید. لطفاً دکمه تایید را بزنید.")
        return TicketStates.CONTENT
        
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
    elif msg.text:
        file_type = "text"
        file_id = ""
        
    messages.append({"file_type": file_type, "file_id": file_id, "caption": caption})
    context.user_data['ticket_messages'] = messages
    return TicketStates.CONTENT

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    messages = context.user_data.get('ticket_messages', [])
    if not messages:
        await query.message.reply_text("⚠️ شما هنوز هیچ پیامی ارسال نکرده‌اید!")
        return TicketStates.CONTENT
        
    try:
        await query.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
        
    await query.message.reply_text(
        "🪄 آیا مایل به ارسال این تیکت هستین؟ 🎟",
        reply_markup=confirm_ticket_keyboard()
    )
    return TicketStates.CONFIRM

async def cancel_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    
    try:
        await query.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
        
    await query.message.reply_text("❌ عملیات لغو شد.", reply_markup=main_menu_keyboard(update.effective_user.id == ADMIN_ID))
    return ConversationHandler.END

async def edit_ticket_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg_count = len(context.user_data.get('ticket_messages', []))
    
    title = context.user_data.get('ticket_title', 'بدون عنوان')
    text = f"عنوان تیکت: {title}\nتعداد پیام‌ها: {msg_count}\n\nلطفاً بخشی که می‌خواهید ویرایش کنید را انتخاب نمایید:"
    try:
        await query.message.edit_text(text, reply_markup=edit_ticket_keyboard(msg_count))
    except Exception:
        await query.message.reply_text(text, reply_markup=edit_ticket_keyboard(msg_count))
    return TicketStates.CONFIRM

async def finish_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_confirmation(update, context)

async def edit_title_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.edit_text("عنوان جدید تیکت را ارسال کنید:")
    except Exception:
        await query.message.reply_text("عنوان جدید تیکت را ارسال کنید:")
    return TicketStates.EDIT_TITLE

async def save_edited_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_title = update.message.text
    if not new_title or not new_title.strip():
        await update.message.reply_text("عنوان نمی‌تواند خالی باشد. دوباره ارسال کنید:")
        return TicketStates.EDIT_TITLE
        
    context.user_data['ticket_title'] = new_title.strip()
    await update.message.reply_text("✅ عنوان ویرایش شد.")
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تایید نهایی", callback_data="show_confirm")]])
    await update.message.reply_text("برای بازگشت به تایید، دکمه زیر را بزنید:", reply_markup=kb)
    return TicketStates.CONFIRM

async def edit_msg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "edit_msg_1":
        context.user_data['editing_index'] = 0
        state = TicketStates.EDIT_MSG_1
    elif data == "edit_msg_2":
        context.user_data['editing_index'] = 1
        state = TicketStates.EDIT_MSG_2
    elif data == "edit_msg_3":
        context.user_data['editing_index'] = 2
        state = TicketStates.EDIT_MSG_3
    else:
        return TicketStates.CONFIRM
        
    try:
        await query.message.edit_text("محتوای جدید برای این پیام را ارسال کنید (متن، عکس و ...):")
    except Exception:
        await query.message.reply_text("محتوای جدید برای این پیام را ارسال کنید (متن، عکس و ...):")
    return state

async def save_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    idx = context.user_data.get('editing_index', 0)
    messages = context.user_data.get('ticket_messages', [])
    
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
    
    if 0 <= idx < len(messages):
        messages[idx] = {"file_type": file_type, "file_id": file_id, "caption": caption}
    elif idx == len(messages):
        messages.append({"file_type": file_type, "file_id": file_id, "caption": caption})
    
    context.user_data['ticket_messages'] = messages
    await update.message.reply_text("✅ پیام با موفقیت ویرایش شد.")
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تایید نهایی", callback_data="show_confirm")]])
    await update.message.reply_text("برای بازگشت به تایید، دکمه زیر را بزنید:", reply_markup=kb)
    return TicketStates.CONFIRM

async def send_ticket_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    title = context.user_data.get('ticket_title')
    messages = context.user_data.get('ticket_messages', [])
    
    if not title or not messages:
        await query.message.reply_text("❌ خطایی رخ داد. اطلاعات تیکت کامل نیست.")
        return ConversationHandler.END
        
    ticket_id = await create_ticket(user.id, title)
    
    for m in messages:
        await add_ticket_message(ticket_id, user.id, m['file_type'], m['file_id'], m['caption'])
        
    try:
        await query.message.reply_sticker("CAACAgIAAxkBAAE...")
    except Exception:
        pass
        
    await query.message.reply_text(
        f"✅ تیکت شما با شماره #{ticket_id} با موفقیت ثبت شد و برای ادمین ارسال گردید.",
        reply_markup=main_menu_keyboard(user.id == ADMIN_ID)
    )
    
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    admin_text = (
        f"🚨 **تیکت جدید دریافت شد!**\n\n"
        f"📌 شماره تیکت: #{ticket_id}\n"
        f"👤 نام کاربر: {user.full_name}\n"
        f"🆔 آیدی: {user.id}\n"
        f"🔗 Username: @{user.username if user.username else 'ندارد'}\n"
        f"🏷 عنوان: {title}\n"
        f"⏰ زمان: {now_str}\n\n"
        f"💬 **پیام‌های کاربر:**"
    )
    
    bot = context.bot
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    
    for m in messages:
        ft = m['file_type']
        fid = m['file_id']
        cap = m['caption']
        if ft == "photo":
            await bot.send_photo(chat_id=ADMIN_ID, photo=fid, caption=cap)
        elif ft == "video":
            await bot.send_video(chat_id=ADMIN_ID, video=fid, caption=cap)
        elif ft == "voice":
            await bot.send_voice(chat_id=ADMIN_ID, voice=fid, caption=cap)
        elif ft == "document":
            await bot.send_document(chat_id=ADMIN_ID, document=fid, caption=cap)
        else:
            await bot.send_message(chat_id=ADMIN_ID, text=cap)
            
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"مدیریت تیکت #{ticket_id}:",
        reply_markup=admin_ticket_action_keyboard(ticket_id)
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def my_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    tickets = await get_user_tickets(user.id)
    if not tickets:
        await query.message.edit_text(
            "📭 شما تاکنون هیچ تیکتی ایجاد نکرده‌اید.",
            reply_markup=user_tickets_keyboard([])
        )
        return
        
    await query.message.edit_text(
        "✨️ تیکت‌های ایجاد شده شما:",
        reply_markup=user_tickets_keyboard(tickets)
    )

async def view_ticket_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    ticket_id = int(data.split("_")[-1])
    
    ticket = await get_ticket_by_id(ticket_id)
    if not ticket:
        await query.message.reply_text("❌ تیکت مورد نظر یافت نشد.")
        return
        
    messages = await get_ticket_messages(ticket_id)
    replies = await get_ticket_replies(ticket_id)
    
    text = f"📂 **تیکت #{ticket['ticket_id']}**\n🏷 عنوان: {ticket['title']}\nوضعیت: {ticket['status']}\nتاریخ: {ticket['created_at']}\n\n--- **پیام‌های تیکت** ---"
    try:
        await query.message.edit_text(text, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown")
    
    bot = context.bot
    chat_id = update.effective_chat.id
    
    for m in messages:
        ft = m['file_type']
        fid = m['file_id']
        cap = m['caption']
        full_cap = f"👤 [شما]: {cap}"
        if ft == "photo":
            await bot.send_photo(chat_id=chat_id, photo=fid, caption=full_cap)
        elif ft == "video":
            await bot.send_video(chat_id=chat_id, video=fid, caption=full_cap)
        elif ft == "voice":
            await bot.send_voice(chat_id=chat_id, voice=fid, caption=full_cap)
        elif ft == "document":
            await bot.send_document(chat_id=chat_id, document=fid, caption=full_cap)
        else:
            await bot.send_message(chat_id=chat_id, text=full_cap)
            
    if replies:
        await bot.send_message(chat_id=chat_id, text="--- **پاسخ‌های ادمین** ---")
        for r in replies:
            ft = r['file_type']
            fid = r['file_id']
            cap = r['caption']
            full_cap = f"🛠 [پشتیبانی/ادمین]: {cap}"
            if ft == "photo":
                await bot.send_photo(chat_id=chat_id, photo=fid, caption=full_cap)
            elif ft == "video":
                await bot.send_video(chat_id=chat_id, video=fid, caption=full_cap)
            elif ft == "voice":
                await bot.send_voice(chat_id=chat_id, voice=fid, caption=full_cap)
            elif ft == "document":
                await bot.send_document(chat_id=chat_id, document=fid, caption=full_cap)
            else:
                await bot.send_message(chat_id=chat_id, text=full_cap)
                
    await bot.send_message(
        chat_id=chat_id,
        text="گزینه‌ها:",
        reply_markup=view_ticket_keyboard(ticket_id, ticket['status'])
    )

async def user_reply_new_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    ticket_id = int(data.split("_")[-1])
    
    context.user_data['user_reply_active_ticket'] = ticket_id
    await query.message.reply_text(f"💬 لطفاً پیام جدید خود را برای تیکت #{ticket_id} ارسال کنید:")
