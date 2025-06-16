from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.data_store import tasks_list


def build_task_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    for index, task in enumerate(tasks_list.get(user_id, []), start=1):
        button = InlineKeyboardButton(
            text=f"{index}. {task['task']} - {task['time']}",
            callback_data=f"done_{index}"  # уникальный callback_data
        )
        keyboard_buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def build_reminder_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    for index, task in enumerate(tasks_list.get(user_id, []), start=1):
        if task['is_remind']:
            text = f"✅ {index}. {task['task']} - {task['time']}"
        else:
            text = f"{index}. {task['task']} - {task['time']}"

        callback_data = f"remind_{index}"

        button = InlineKeyboardButton(text=text, callback_data=callback_data)

        keyboard_buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def build_delete_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    for index, task in enumerate(tasks_list.get(user_id, []), start=1):
        if task['is_remind']:
            text = f"✅ {index}. {task['task']} - {task['time']}"
        else:
            text = f"{index}. {task['task']} - {task['time']}"

        callback_data = f"delete{index}"

        button = InlineKeyboardButton(text=text, callback_data=callback_data)

        keyboard_buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)



def build_time_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard_buttons = []

    for index, task in enumerate(tasks_list.get(user_id, []), start=1):
        if task['is_remind']:
            text = f"✅ {index}. {task['task']} - {task['time']}"
        else:
            text = f"{index}. {task['task']} - {task['time']}"

        callback_data = f"change_time_{index}"

        button = InlineKeyboardButton(text=text, callback_data=callback_data)

        keyboard_buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
