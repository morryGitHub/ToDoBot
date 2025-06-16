import dateparser
import asyncio

from sqlite3 import connect
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.data_store import tasks_list, reminder_tasks
from timer.reminder_job import send_reminder
from keyboards.userkb import build_task_keyboard, build_reminder_keyboard, build_time_keyboard

from data.bot import bot  # импортируем объект bot из bot.py

user = Router()


class Task(StatesGroup):
    task = State()
    time = State()
    new_time = State()


@user.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я — твой персональный бот для управления задачами 📝\n"
        "Вот что я умею:\n"
        "➕ /add — добавить новую задачу\n"
        "📋 /list — показать все задачи\n"
        "✅ /done — отметить задачу как выполненную\n"
        "❌ /delete — удалить задачу\n\n"
        "Начни с команды /add, чтобы создать свою первую задачу!\n\n"
        "🕒 Внимание: бот работает по часовому поясу UTC+0 (Ирландия зимой, Лондон зимой).\n"
        "Если вы в другом часовом поясе — учитывайте это при установке времени задач."
    )


@user.message(Command("add"))
async def add(message: Message, state: FSMContext):
    await state.set_state(Task.task)
    await message.answer("📝 Пожалуйста, напишите задачу, которую нужно добавить в список дел.")


@user.message(Task.task)
async def task(message: Message, state: FSMContext):
    task_text = message.text
    user_id = message.from_user.id

    if user_id not in tasks_list:
        tasks_list[user_id] = []

    await state.update_data(task=task_text)
    await state.set_state(Task.time)
    await message.answer("📝 Пожалуйста, напишите время, на которое нужно добавить задание.")


@user.message(Task.time)
async def task(message: Message, state: FSMContext):
    time_text = message.text
    user_id = message.from_user.id

    dt = dateparser.parse(time_text, languages=['ru'])
    if not dt:
        await message.answer("⛔ Не удалось разобрать дату. Пример: «завтра в 14:30» или «15/06/2025 21:30».")
        return

    try:
        user_friendly = dt.strftime("%d.%m.%Y %H:%M")
    except AttributeError:
        await message.answer(
            "Не удалось разобрать дату\n📝 Пожалуйста, напишите время, на которое нужно добавить задание.")
        return

    await state.update_data(time=user_friendly)

    data = await state.get_data()
    new_task = {"task": data["task"],
                "time": data["time"],
                "is_remind": False,
                "timeout": False}
    tasks_list[user_id].append(new_task)

    await message.answer(f"📝 Ваша задача <b>{data['task']}</b> была добавлена в список дел.", parse_mode="HTML")
    await message.answer("Теперь вы можете установить напоминание с помощью /remind.")
    await state.clear()


@user.message(Command("change_time"))
async def change_time(message: Message):
    user_id = message.from_user.id

    if user_id not in tasks_list or not tasks_list[user_id]:
        await message.answer("🗒️ Сначала добавьте задачу с помощью /add.")
        return
    keyboard = build_time_keyboard(user_id)
    await message.answer("📋 Выберите задание которое нужно изменить:", reply_markup=keyboard)


@user.callback_query(F.data.startswith("change_"))
async def select_task_to_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task_index = int(callback.data.split("_")[-1])
    await state.update_data(change_index=task_index)
    await state.set_state(Task.new_time)
    await callback.message.answer("🕒 Введите новое время для задачи:")


@user.message(Task.new_time)
async def set_new_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    task_index = data.get("change_index")

    dt = dateparser.parse(message.text, languages=['ru'])
    if not dt:
        await message.answer("⛔ Не удалось разобрать дату. Пример: «завтра в 14:30» или «15/06/2025 21:30».")
        return

    formatted_time = dt.strftime("%d.%m.%Y %H:%M")

    # Обновляем время задачи
    tasks_list[user_id][task_index - 1]["time"] = formatted_time
    tasks_list[user_id][task_index - 1]["is_remind"] = False  # сбрасываем напоминание

    await message.answer("✅ Время задачи обновлено.\nТеперь вы можете снова установить напоминание с помощью /remind.")
    await state.clear()


@user.message(Command("list"))
async def list_tasks(message: Message):
    user_id = message.from_user.id

    if user_id not in tasks_list or not tasks_list[user_id]:
        await message.answer("🗒️ Сначала добавьте задачу с помощью /add.")
        return

    # Формируем список задач в одну строку
    user_tasks = tasks_list[user_id]
    print(user_tasks)

    task_lines = []
    for i, task_dict in enumerate(user_tasks):
        data = user_tasks[0]
        # task_dict — словарь с одной парой {текст: время}
        task_text = data['task']
        task_time = data['time']

        task_lines.append(f"{i + 1}. {task_text} — {task_time}")

    result = "\n".join(task_lines)
    await message.answer(f"📋 Ваш список дел:\n{result}")


@user.message(Command("clear"))
async def clear_tasks(message: Message):
    user_id = message.from_user.id

    if user_id not in tasks_list or not tasks_list[user_id]:
        await message.answer("🗒️ Сначала добавьте задачу с помощью /add.")
        return

    tasks_list[user_id].clear()
    await message.answer("✅ Ваш список задач очищен.")


@user.message(Command("done"))
async def done_task(message: Message):
    user_id = message.from_user.id

    if user_id not in tasks_list or not tasks_list[user_id]:
        await message.answer("🗒️ Сначала добавьте задачу с помощью /add.")
        return
    keyboard = build_task_keyboard(user_id)
    await message.answer("📋 Выберите задание которое выполнено:", reply_markup=keyboard)


@user.callback_query(F.data.startswith('done_'))
async def done(callback: CallbackQuery):
    await callback.answer()

    task_index = int(callback.data.split('_')[1])  # номер задачи из callback_data
    user_id = callback.from_user.id

    # Обновляем текст задачи с отметкой выполнено (например, в списке)
    tasks = tasks_list.get(user_id, [])
    if 0 < task_index <= len(tasks):
        tasks[task_index - 1] = f"{tasks[task_index - 1]}"
        tasks_list[user_id].pop(task_index - 1)

    # Строим новую клавиатуру с обновлённым текстом кнопок
    new_markup = build_task_keyboard(user_id)

    # Обновляем клавиатуру у сообщения
    await callback.message.edit_reply_markup(reply_markup=new_markup)
    await callback.message.answer(f"Задача {task_index} отмечена как выполненная.")


@user.message(Command("remind"))
async def set_reminder(message: Message):
    user_id = message.from_user.id

    if user_id not in tasks_list or not tasks_list[user_id]:
        await message.answer("🗒️ Сначала добавьте задачу с помощью /add.")
        return
    keyboard = build_reminder_keyboard(user_id)
    await message.answer("📋 Выберите задание которое нужно напомнить:", reply_markup=keyboard)




@user.callback_query(F.data.startswith("remind_"))
async def remind(callback: CallbackQuery):
    await callback.answer()
    task_index = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    tasks = tasks_list.get(user_id, [])

    if 0 < task_index <= len(tasks):
        task_key = (user_id, task_index)

        if not tasks[task_index - 1]["is_remind"]:
            tasks[task_index - 1]["is_remind"] = True

            new_markup = build_reminder_keyboard(user_id)
            await callback.message.edit_reply_markup(reply_markup=new_markup)

            # ✅ Сохраняем в БД
            with connect("reminder_tasks.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reminders (task_id, remind_time, status) VALUES (?, ?, ?)",
                    (task_index, tasks[task_index - 1]['time'], 'pending')
                )
                conn.commit()

            # ✅ Сохраняем задачу напоминания в памяти
            reminder_task = asyncio.create_task(
                send_reminder(bot, user_id, tasks[task_index - 1]['task'], tasks[task_index - 1]['time'])
            )
            reminder_tasks[task_key] = reminder_task

            await callback.message.answer("⏰ Вы установили таймер.")
        else:
            tasks[task_index - 1]["is_remind"] = False

            # ❌ Отменяем задачу
            reminder_task = reminder_tasks.get(task_key)
            if reminder_task and not reminder_task.done():
                reminder_task.cancel()
                del reminder_tasks[task_key]

            # ❌ Удаляем из БД
            with connect("reminder_tasks.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM reminders WHERE task_id = ? AND status = 'pending'",
                    (task_index,)
                )
                conn.commit()

            new_markup = build_reminder_keyboard(user_id)
            await callback.message.edit_reply_markup(reply_markup=new_markup)
            await callback.message.answer("⏰ Вы сняли задание с таймера.")
