
# ----------- dependencies ----------- #
from aiogram.filters import Command
from aiogram import types
from database import TelegramChat
from typing import List
# ----------- ------------ ----------- #

# variables whose names begin with "__" mean that these variables should not be used in the app.py module

# commands
start_command = Command('start')

# messages
start_message = '''
<b>👋 Welcome to the bot %s!</b>\n\nHere you can conveniently <b>track</b> messages in various groups and channels.
'''

no_chats_message = '''
<b>You haven't added any chats yet.</b>
'''

chat_list_message = '''
<b>Chat list:</b>
'''

default_menu_message = '''
<b>Menu.</b>
'''

cancel_message = '''
<b>The process was interrupted.</b>
'''

write_chat_username_message = '''
Send username or chat ID for its handling.
'''

chat_added_message = '''
Chat "%s" has been added.
'''

# or chat ID
incorrect_chat_username_message = '''
<b>❌ Incorrect username or chat ID.</b>
'''

chat_doesnt_exist_message = '''
<b>❌ This chat does not exist.</b>
'''

chat_doesnt_exist_callback_answer = '''
This chat does not exist.
'''

telegram_chat_information_message = '''
<b>Chat information.</b>

Database ID: <code>%s</code>
Chat title: <code>%s</code>
Username: <code>%s</code>
Status: <code>%s</code>
'''

telegram_chat_deleted_message = '''
<b>Chat has been deleted.</b>
'''

chat_already_deleted_message = '''
This chat has already been deleted.
'''

chat_notification_message = '''
<b>❕ New message in chat %s.</b>\n\n%s
'''

# additions
__chats_markup_title  = 'Title'
__chats_markup_status = 'Status'
__chat_markup_add     = '➕ Add new'
__chat_delete_title   = 'Delete the chat'
chats_button_title    = '💬 Chats'
menu_button_title     = '◀️ Menu'
cancel_button_title   = 'Cancel'

telegram_chat_statuses = {True: '⚙️ Working...',
                         False: '💤 Sleeping...'}

# markups
# -------------------------- #
__cancel_buttons = [[types.KeyboardButton(text = cancel_button_title)]]

cancel_markup = types.ReplyKeyboardMarkup(keyboard = __cancel_buttons, resize_keyboard = True)
# -------------------------- #

# -------------------------- #
__menu_buttons = [
    [types.KeyboardButton(text = chats_button_title)]
    ]


menu_markup = types.ReplyKeyboardMarkup(keyboard = __menu_buttons, is_persistent = True, resize_keyboard = True)
# -------------------------- #

# -------------------------- #
async def generate_chats_markup(chat_list: List[TelegramChat]) -> types.InlineKeyboardMarkup:
    button_list = []
    for chat in chat_list:
        button_list.append([types.InlineKeyboardButton(text = chat.title, callback_data = f'chat_info#{chat.id}'),
                            types.InlineKeyboardButton(text = telegram_chat_statuses[chat.status], callback_data = f'toggle_chat_status#{chat.id}')])
    if button_list:
        button_list.insert(0, [types.InlineKeyboardButton(text = __chats_markup_title, callback_data = '#'),
                               types.InlineKeyboardButton(text = __chats_markup_status, callback_data = '#')])
    button_list.append([types.InlineKeyboardButton(text = __chat_markup_add, callback_data = 'add_chat')])
    return types.InlineKeyboardMarkup(inline_keyboard = button_list)
# -------------------------- #

# -------------------------- #
async def generate_chat_delete_markup(database_chat_id: int) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(inline_keyboard = [[
        types.InlineKeyboardButton(text = __chat_delete_title, callback_data = f'delete_chat#{database_chat_id}')
        ]])
# -------------------------- #

# some functions to shorten the code in app.py
async def send_chat_list(message: types.Message, chat_list: List[TelegramChat]):
    answer_text = None
            
    if chat_list: answer_text = chat_list_message
    else: answer_text = no_chats_message

    await message.answer(text = answer_text, parse_mode = 'html', reply_markup = await generate_chats_markup(chat_list))