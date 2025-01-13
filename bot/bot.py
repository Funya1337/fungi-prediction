import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import pickle

load_dotenv()
TOKEN = os.getenv("TOKEN")

data = pd.read_csv('fungi-prediction\mushrooms.csv')
pickle_in = open('fungi-prediction\classifier.pkl', 'rb')

le = LabelEncoder()
for column in data.columns:
    data[column] = le.fit_transform(data[column])

x = data.drop('class', axis=1)

pca1 = PCA(n_components=7)
pca_fit = pca1.fit_transform(x)
pca1.explained_variance_ratio_

classifier = pickle.load(pickle_in)

# All parameters and their encoded values
parameters = [
    ('cap_shape', ['x', 'b', 's', 'f', 'k', 'c'], [5, 0, 4, 2, 3, 1]),
    ('cap_surface', ['s', 'y', 'f', 'g'], [2, 3, 0, 1]),
    ('cap_color', ['n', 'y', 'w', 'g', 'e', 'p', 'b', 'u', 'c', 'r'], [4, 9, 8, 3, 2, 5, 0, 7, 1, 6]),
    ('bruises', ['t', 'f'], [1, 0]),
    ('odor', ['p', 'a', 'l', 'n', 'f', 'c', 'y', 's', 'm'], [6, 0, 3, 5, 2, 1, 8, 7, 4]),
    ('gill_attachment', ['f', 'a'], [0, 1]),
    ('gill_spacing', ['c', 'w'], [0, 1]),
    ('grill_size', ['n', 'b'], [1, 0]),
    ('grill_color', ['k', 'n', 'g', 'p', 'w', 'h', 'u', 'e', 'b', 'r', 'y', 'o'], [4, 5, 2, 7, 10, 3, 9, 1, 0, 8, 11, 6]),
    ('stalk_shape', ['e', 't'], [0, 1]),
    ('stalk_root', ['e', 'c', 'b', 'r', '?'], [3, 2, 1, 4, 0]),
    ('stalk_surface_above_ring', ['s', 'f', 'k', 'y'], [2, 0, 1, 3]),
    ('stalk_surface_below_ring', ['s', 'f', 'y', 'k'], [2, 0, 1, 3]),
    ('stalk_color_above_ring', ['w', 'g', 'p', 'n', 'b', 'e', 'o', 'c', 'y'], [7, 3, 6, 4, 0, 2, 5, 1, 8]),
    ('stalk_color_below_ring', ['w', 'p', 'g', 'b', 'n', 'e', 'y', 'o', 'c'], [7, 6, 3, 0, 4, 2, 8, 5, 1]),
    ('veil_type', ['p'], [0]),
    ('veil_color', ['w', 'n', 'o', 'y'], [2, 0, 1, 3]),
    ('ring_number', ['o', 't', 'n'], [1, 2, 0]),
    ('ring_type', ['p', 'e', 'l', 'f', 'n'], [4, 0, 2, 1, 3]),
    ('spore_print_color', ['k', 'n', 'u', 'h', 'w', 'r', 'o', 'y', 'b'], [2, 3, 6, 1, 7, 5, 4, 8, 0]),
    ('population', ['s', 'n', 'a', 'v', 'y', 'c'], [3, 2, 0, 4, 5, 1]),
    ('habitat', ['u', 'g', 'm', 'd', 'p', 'w', 'l'], [5, 1, 3, 0, 4, 6, 2]),
]

user_states = {}
print(123)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_states[user_id] = {"step": 0, "choices": []}  # Инициализация состояния пользователя

    await ask_next_parameter(update, context, user_id)

async def ask_next_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    state = user_states[user_id]
    step = state["step"]

    if step >= len(parameters):
        await process_final_result(update, context, user_id)
        return

    param_name, values, value_map = parameters[step]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(value, callback_data=value)] for value in values
    ])

    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"Выберите значение для {param_name}:", reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            f"Выберите значение для {param_name}:", reply_markup=keyboard
        )

async def handle_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    value = query.data

    state = user_states[user_id]
    step = state["step"]

    # Добавление значения в выбор пользователя
    param_name, values, value_map = parameters[step]
    
    if value in values:
        index = values.index(value)
        if index < len(value_map):  # Проверяем, существует ли индекс в value_map
            state["choices"].append(value_map[index])
        else:
            await query.answer("Ошибка: несоответствие данных. Попробуйте снова.")
            return
    else:
        await query.answer("Неверное значение. Попробуйте снова.")
        return

    # Переход к следующему параметру
    state["step"] += 1
    user_states[user_id] = state

    await query.answer()
    await ask_next_parameter(update, context, user_id)

async def process_final_result(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    state = user_states[user_id]
    choices = state["choices"]

    print(state)
    print(choices)
    print("asdfasdfasdfasdfasdf")

    pred = classifier.predict(pca1.transform([choices]))[0]
    res = ""
    if (pred == 1):
        res = "Гриб ядовит (ОПАСНОСТЬ)"
    else:
        res = "Гриб съедобен (ОПАСНОСТИ НЕТ)"

    # Здесь вы можете добавить логику для обработки результата (например, предсказание модели)
    # Для примера просто выводим список выбора пользователя
    result_message = f"Результат: {res}"

    if update.callback_query:
        await update.callback_query.message.reply_text(result_message)
    else:
        await update.message.reply_text(result_message)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_value))

    application.run_polling()

if __name__ == "__main__":
    main()