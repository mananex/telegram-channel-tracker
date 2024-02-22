# ----------- dependencies ----------- #
from telethon.client import TelegramClient
from telethon import events
from telethon import types as telethon_types
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import Base, TelegramChat, async_engine, async_session, fetchone, fetchmany, insert, execute_stmt
from sqlalchemy import select, update, delete
from additional import *
from configuration import *
import asyncio
# ----------- ------------ ----------- #

client = TelegramClient('session1', api_id = API_ID, api_hash = API_HASH)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

event_handlers_list = []

# --------------- -------------- --------------- #
class AddChatForm(StatesGroup):
    chat = State() # username or ID
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
def is_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID: return True
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
async def validate_username(chat: int | str) -> str | int | bool: # also can check chat ID
    '''
    Check if the username or chat ID is correct and returns back the username or chat ID if yes. Return false otherwise. 
    (Also can check chat ID)
    '''
    try:
        if chat[0] == '@': return chat
        else: return int(chat)
    except:
        return False
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
async def check_username_avilability(chat: int | str) -> bool | str: # also can check chat ID
    '''
    Check whether an entity exists by the specified username or chat ID. Returns first_name of the chat.
    (Also can check chat ID)
    '''
    try:
        entity = await client.get_entity(chat)
        entity_type = type(entity)
        
        if entity_type == telethon_types.User: return entity.first_name
        else: return entity.title
    except:
        return False
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
async def handle_chat(event: events.NewMessage.Event) -> None:
    message: telethon_types.Message = event.message
    entity = await client.get_entity(event.chat_id)
    
    message_addition = None
    message_part = None
    
    if entity.username: message_addition = f'@{entity.username}'
    else: message_addition = await check_username_avilability(event.chat_id)
    
    if len(message.message) < chat_message_max_letters: message_part = message.message
    else: message_part = message.message[:chat_message_max_letters - 4] + '...'

    await bot.send_message(chat_id = ADMIN_ID, text = chat_notification_message % (message_addition, message_part), parse_mode = 'html')
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
async def reset_event_handlers() -> None:
    '''
    Deletes current telethon event handlers and adds new ones - taking them from the database
    '''
    async with async_session() as session:
        telegram_chats: List[TelegramChat] = list(await fetchmany(select(TelegramChat), session))
        for chat in telegram_chats:
            if chat.status:
                client.add_event_handler(handle_chat, events.NewMessage(chats = [await validate_username(chat.username)], outgoing = True))
            else: 
                client.remove_event_handler(handle_chat, events.NewMessage(chats = [await validate_username(chat.username)], outgoing = True))
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.message(start_command)
async def start_handler(message: types.Message) -> None:
    if is_admin(message):
        bot_info = await bot.get_me()
        await message.answer(text = start_message % (bot_info.first_name), reply_markup = menu_markup, parse_mode = 'html')
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.message(F.text == chats_button_title)
async def chats_handler(message: types.Message) -> None:
    if is_admin(message):
        async with async_session() as session:
            chat_list = list(await fetchmany(select(TelegramChat), session))
            await send_chat_list(message, chat_list)
            await reset_event_handlers()
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.message(F.text == menu_button_title)
async def menu_handler(message: types.Message) -> None:
    if is_admin(message):
        await message.answer(text = default_menu_message, reply_markup = menu_markup, parse_mode = 'html')
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.message(F.text == cancel_button_title)
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    if is_admin(message):
        current_state = await state.get_state()
        if current_state != None:
            await state.clear()
            await message.reply(text = cancel_message, reply_markup = menu_markup, parse_mode = 'html')
# --------------- -------------- --------------- #



# Adding new chat
# --------------- -------------- --------------- #
@router.callback_query(F.data == 'add_chat')
async def add_chat_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AddChatForm.chat)
    await call.message.answer(text = write_chat_username_message, reply_markup = cancel_markup)
    
@router.message(AddChatForm.chat)
async def get_chat_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    valid_username = await validate_username(message.text)
    if valid_username:
        chat_title = await check_username_avilability(valid_username)
        if chat_title:
            async with async_session() as session:
                await insert(TelegramChat(title = chat_title, username = valid_username, status = False), session)
                chat_list = list(await fetchmany(select(TelegramChat), session))
                await send_chat_list(message, chat_list)
                await message.answer(text = chat_added_message % (chat_title), reply_markup = menu_markup)
        else:
            await message.answer(text = chat_doesnt_exist_message, reply_markup = menu_markup, parse_mode = 'html')
    else:
        await message.answer(text = incorrect_chat_username_message, reply_markup = menu_markup, parse_mode = 'html')
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.callback_query(F.data.startswith('chat_info'))
async def chat_info_handler(call: types.CallbackQuery) -> None:
    database_chat_id = int(call.data.split('#')[1])
    async with async_session() as session:
        telegram_chat: TelegramChat = await fetchone(select(TelegramChat).where(TelegramChat.id == database_chat_id), session)
        if telegram_chat:
            await call.message.answer(
                text = telegram_chat_information_message % (telegram_chat.id, telegram_chat.title, telegram_chat.username, telegram_chat_statuses[telegram_chat.status]),
                reply_markup = await generate_chat_delete_markup(telegram_chat.id),
                parse_mode = 'html')
        else:
            await call.answer(text = chat_doesnt_exist_callback_answer)
            return
    await call.answer()
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.callback_query(F.data.startswith('toggle_chat_status'))
async def toggle_chat_status_handler(call: types.CallbackQuery) -> None:
    database_chat_id = int(call.data.split('#')[1])
    async with async_session() as session:
        telegram_chat_status = await fetchone(select(TelegramChat.status).where(TelegramChat.id == database_chat_id), session)
        if telegram_chat_status != None:
            chat_list = list(await fetchmany(select(TelegramChat), session))
            await execute_stmt(update(TelegramChat).where(TelegramChat.id == database_chat_id).values(status = not telegram_chat_status), session)
            await call.message.edit_reply_markup(reply_markup = await generate_chats_markup(chat_list))
            await reset_event_handlers()
        else:
            await call.answer(text = chat_doesnt_exist_callback_answer)
            return
    await call.answer()
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.callback_query(F.data.startswith('delete_chat'))
async def delete_chat_handler(call: types.CallbackQuery) -> None:
    database_chat_id = int(call.data.split('#')[1])
    async with async_session() as session:
        chat = await fetchone(select(TelegramChat).where(TelegramChat.id == database_chat_id), session)
        if chat:
            await execute_stmt(delete(TelegramChat).where(TelegramChat.id == database_chat_id), session)
            await call.message.answer(text = telegram_chat_deleted_message, reply_markup = menu_markup, parse_mode = 'html')
            await call.message.delete()
            
            chat_list = list(await fetchmany(select(TelegramChat), session))
            await send_chat_list(call.message, chat_list)
        else:
            await call.answer(text = chat_already_deleted_message)
            return
    await call.answer()
# --------------- -------------- --------------- #



# --------------- -------------- --------------- #
@router.callback_query(F.data == '#')
async def answer_pass_query(call: types.CallbackQuery) -> None:
    await call.answer()
# --------------- -------------- --------------- #



# ---------------   bot startup   --------------- #
async def main() -> None:
    print('Working with tables...')
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print('starting...')
    await bot.delete_webhook(drop_pending_updates = True)
    await client.start()
    await dp.start_polling(bot, handle_signals = True)
# --------------- ---------------- --------------- #

# ----------- run ----------- #
if __name__ == '__main__':
    asyncio.run(main())
# ----------- --- ----------- #