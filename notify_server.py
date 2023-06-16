from keyboards import user as user_kb
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from datetime import datetime, timedelta

from pydantic import BaseModel
from create_bot import bot
from utils import db
import uvicorn

app = FastAPI()
scheduler = AsyncIOScheduler()


class LavaWebhook(BaseModel):
    order_id: str
    status: str
    amount: float


async def stock_notify(user_id):
    await bot.send_message(user_id,
                           "Успей пополнить баланс в течении 24 часов и получи на счёт +30% от суммы пополнения⤵️",
                           reply_markup=user_kb.get_pay(user_id, 30))
    await db.update_new_stock_time(user_id, int(datetime.now().timestamp()))


@app.on_event('startup')
def init_scheduler():
    scheduler.start()


@app.post('/stock/{user_id}')
async def create_notify_request(user_id: int):
    run_date = datetime.now() + timedelta(minutes=10)
    try:
        scheduler.add_job(stock_notify, "date", run_date=run_date, args=[user_id], id=str(user_id))
    except ConflictingIdError:
        scheduler.remove_job(str(user_id))
        scheduler.add_job(stock_notify, "date", run_date=run_date, args=[user_id], id=str(user_id))


@app.delete('/stock/{user_id}')
async def delete_notify_request(user_id: int):
    try:
        scheduler.remove_job(str(user_id))
    except JobLookupError:
        return


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
