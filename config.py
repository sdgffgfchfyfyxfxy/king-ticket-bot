import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("توکن ربات (TOKEN) در متغیرهای محیطی یافت نشد!")

if not ADMIN_ID_STR:
    raise ValueError("شناسه ادمین (ADMIN_ID) در متغیرهای محیطی یافت نشد!")

try:
    ADMIN_ID = int(ADMIN_ID_STR)
except ValueError:
    raise ValueError("مقدار ADMIN_ID باید یک عدد صحیح باشد!")