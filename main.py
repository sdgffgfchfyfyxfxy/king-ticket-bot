import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)
from config import TOKEN, ADMIN_ID
from database.db import init_db, get_ticket_by_id, add_ticket_message
from states.states import TicketStates, AdminStates
from handlers.user_handlers import (
    start_command, back_to_main_callback, create_ticket_start,
    receive_ticket_title, receive_ticket_content, show_confirmation,
    cancel_ticket, edit_ticket_menu, edit_title_start, save_edited_title,
    edit_msg_start, save_edited_message, send_ticket_final,
    my_tickets_handler, view_ticket_handler, finish_edit, user_reply_new_message
)
from handlers.admin_handlers import (
    admin_panel_callback, admin_stats_callback, admin_open_tickets_callback,
    admin_closed_tickets_callback, admin_users_callback, admin_settings_callback,
    admin_broadcast_start, admin_broadcast_send, admin_reply_start,
    admin_send_reply_content, admin_close_ticket_callback
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def user_active_ticket_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_ticket_id = context.user_data.get('user_reply_active_ticket')
    if not active_ticket_id:
        return
        
    msg = update.message
    ticket = await get_ticket_by_id(active_ticket_id)
    if not ticket or ticket['status'] != 'Open':
        await msg.reply_text("❌ این تیکت بسته شده یا وجود ندارد.")
        context.user_data.pop('user_reply_active_ticket', None)
        return
        
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
        
    await add_ticket_message(active_ticket_id, update.effective_user.id, file_type, file_id, caption)
    await msg.reply_text("✅ پیام جدید شما برای ادمین ارسال شد.")
    
    user = update.effective_user
    admin_text = f"💬 **پیام جدید روی تیکت #{active_ticket_id}** از طرف {user.full_name} (`{user.id}`):"
    bot = context.bot
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    
    if file_type == "photo":
        await bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=caption)
    elif file_type == "video":
        await bot.send_video(chat_id=ADMIN_ID, video=file_id, caption=caption)
    elif file_type == "voice":
        await bot.send_voice(chat_id=ADMIN_ID, voice=file_id, caption=caption)
    elif file_type == "document":
        await bot.send_document(chat_id=ADMIN_ID, document=file_id, caption=caption)
    else:
        await bot.send_message(chat_id=ADMIN_ID, text=caption)
        
    context.user_data.pop('user_reply_active_ticket', None)

def main():
    asyncio.get_event_loop().run_until_complete(init_db())
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    ticket_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_ticket_start, pattern="^create_ticket$")],
        states={
            TicketStates.TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ticket_title)],
            TicketStates.CONTENT: [
                MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, receive_ticket_content),
                CallbackQueryHandler(show_confirmation, pattern="^show_confirm$")
            ],
            TicketStates.CONFIRM: [
                CallbackQueryHandler(edit_ticket_menu, pattern="^edit_ticket$"),
                CallbackQueryHandler(send_ticket_final, pattern="^send_ticket$"),
                CallbackQueryHandler(cancel_ticket, pattern="^cancel_ticket$"),
                CallbackQueryHandler(edit_title_start, pattern="^edit_title$"),
                CallbackQueryHandler(edit_msg_start, pattern="^edit_msg_[123]$"),
                CallbackQueryHandler(finish_edit, pattern="^finish_edit$"),
                CallbackQueryHandler(show_confirmation, pattern="^show_confirm$")
            ],
            TicketStates.EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_title)],
            TicketStates.EDIT_MSG_1: [MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, save_edited_message)],
            TicketStates.EDIT_MSG_2: [MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, save_edited_message)],
            TicketStates.EDIT_MSG_3: [MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, save_edited_message)],
        },
        fallbacks=[CallbackQueryHandler(cancel_ticket, pattern="^cancel_ticket$")]
    )
    
    admin_reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_reply_start, pattern="^admin_reply_\\d+$")],
        states={
            AdminStates.REPLYING: [MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, admin_send_reply_content)]
        },
        fallbacks=[CommandHandler("cancel", back_to_main_callback)]
    )
    
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_broadcast_start, pattern="^adm_broadcast$")],
        states={
            AdminStates.BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_send)]
        },
        fallbacks=[CommandHandler("cancel", back_to_main_callback)]
    )
    
    app.add_handler(ticket_conv_handler)
    app.add_handler(admin_reply_conv)
    app.add_handler(broadcast_conv)
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(my_tickets_handler, pattern="^my_tickets$"))
    app.add_handler(CallbackQueryHandler(view_ticket_handler, pattern="^view_ticket_\\d+$"))
    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_stats_callback, pattern="^adm_stats$"))
    app.add_handler(CallbackQueryHandler(admin_open_tickets_callback, pattern="^adm_open_tickets$"))
    app.add_handler(CallbackQueryHandler(admin_closed_tickets_callback, pattern="^adm_closed_tickets$"))
    app.add_handler(CallbackQueryHandler(admin_users_callback, pattern="^adm_users$"))
    app.add_handler(CallbackQueryHandler(admin_settings_callback, pattern="^adm_settings$"))
    app.add_handler(CallbackQueryHandler(admin_close_ticket_callback, pattern="^admin_close_\\d+$"))
    app.add_handler(CallbackQueryHandler(user_reply_new_message, pattern="^user_reply_\\d+$"))
    
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL) & ~filters.COMMAND, user_active_ticket_message_handler))

    logger.info("ربات با موفقیت شروع به کار کرد...")
    app.run_polling()

if __name__ == "__main__":
    main()
