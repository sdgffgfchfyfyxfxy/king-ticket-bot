from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard(is_admin: bool = False):
    keyboard = [
        [InlineKeyboardButton("🎫 ساخت تیکت جدید 📬", callback_data="create_ticket")],
        [InlineKeyboardButton("✨️ تیکت های ایجاد شده 🏅", callback_data="my_tickets")],
        [InlineKeyboardButton("🪄 ورود به ربات اصلی خرید/کانفیگ رایگان ⚜️", url="https://t.me/kingconfi8sbot")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("🔐 پنل مدیریت", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def confirm_ticket_keyboard():
    keyboard = [
        [InlineKeyboardButton("📭 ویرایش ♻️", callback_data="edit_ticket")],
        [InlineKeyboardButton("✔️ ارسال 🚀", callback_data="send_ticket")],
        [InlineKeyboardButton("❄️ لغو ❌", callback_data="cancel_ticket")]
    ]
    return InlineKeyboardMarkup(keyboard)

def edit_ticket_keyboard(msg_count: int):
    keyboard = [
        [InlineKeyboardButton("ویرایش عنوان", callback_data="edit_title")],
        [InlineKeyboardButton("ویرایش پیام اول", callback_data="edit_msg_1")]
    ]
    if msg_count >= 2:
        keyboard.append([InlineKeyboardButton("ویرایش پیام دوم", callback_data="edit_msg_2")])
    if msg_count >= 3:
        keyboard.append([InlineKeyboardButton("ویرایش پیام سوم", callback_data="edit_msg_3")])
    keyboard.append([InlineKeyboardButton("اتمام ویرایش", callback_data="finish_edit")])
    return InlineKeyboardMarkup(keyboard)

def user_tickets_keyboard(tickets):
    keyboard = []
    for t in tickets:
        status_icon = "🟢" if t["status"] == "Open" else "🔴"
        text = f"{status_icon} #{t['ticket_id']} - {t['title']} ({t['status']})"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"view_ticket_{t['ticket_id']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def view_ticket_keyboard(ticket_id: int, status: str):
    keyboard = []
    if status == "Open":
        keyboard.append([InlineKeyboardButton("💬 ارسال پیام جدید", callback_data=f"user_reply_{ticket_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به تیکت‌ها", callback_data="my_tickets")])
    return InlineKeyboardMarkup(keyboard)

def admin_ticket_action_keyboard(ticket_id: int):
    keyboard = [
        [InlineKeyboardButton("💬 پاسخ", callback_data=f"admin_reply_{ticket_id}")],
        [InlineKeyboardButton("🔒 بستن تیکت", callback_data=f"admin_close_{ticket_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="adm_stats"), InlineKeyboardButton("📨 پیام همگانی", callback_data="adm_broadcast")],
        [InlineKeyboardButton("📂 تیکت های باز", callback_data="adm_open_tickets"), InlineKeyboardButton("📁 تیکت های بسته", callback_data="adm_closed_tickets")],
        [InlineKeyboardButton("👥 کاربران", callback_data="adm_users"), InlineKeyboardButton("⚙️ تنظیمات", callback_data="adm_settings")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
