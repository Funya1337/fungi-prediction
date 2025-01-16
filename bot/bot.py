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

data = pd.read_csv('../mushrooms.csv')
pickle_in = open('../classifier.pkl', 'rb')

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
    ('форма_шляпки', ['выпуклая (x)', 'колокольчатая (b)', 'вдавленная (s)', 'плоская (f)', 'бугорчатая (k)', 'коническая (c)'], [5, 0, 4, 2, 3, 1]),
('поверхность_шляпки', ['гладкая (s)', 'чешуйчатая (y)', 'волокнистая (f)', 'с бороздками (g)'], [2, 3, 0, 1]),
('цвет_шляпки', ['коричневый (n)', 'жёлтый (y)', 'белый (w)', 'серый (g)', 'красный (e)', 'розовый (p)', 'бежевый (b)', 'пурпурный (u)', 'цинамоновый (c)', 'зелёный (r)'], [4, 9, 8, 3, 2, 5, 0, 7, 1, 6]),
('синеет', ['да (t)', 'нет (f)'], [1, 0]),
('запах', ['резкий (p)', 'миндальный (a)', 'анисовый (l)', 'нет (n)', 'гнилостный (f)', 'креозотовый (c)', 'рыбный (y)', 'пряный (s)', 'затхлый (m)'], [6, 0, 3, 5, 2, 1, 8, 7, 4]),
('прикрепление_пластинок', ['свободные (f)', 'приросшие (a)'], [0, 1]),
('расстояние_между_пластинками', ['плотное (c)', 'скученное (w)'], [0, 1]),
('размер_пластинок', ['узкие (n)', 'широкие (b)'], [1, 0]),
('цвет_пластинок', ['чёрный (k)', 'коричневый (n)', 'серый (g)', 'розовый (p)', 'белый (w)', 'шоколадный (h)', 'пурпурный (u)', 'красный (e)', 'бежевый (b)', 'зелёный (r)', 'жёлтый (y)', 'оранжевый (o)'], [4, 5, 2, 7, 10, 3, 9, 1, 0, 8, 11, 6]),
('форма_ножки', ['расширяющаяся (e)', 'сужающаяся (t)'], [0, 1]),
('основание_ножки', ['равномерное (e)', 'булавовидное (c)', 'утолщённое (b)', 'укоренённое (r)', 'отсутствует (?)'], [3, 2, 1, 4, 0]),
('поверхность_ножки_над_кольцом', ['гладкая (s)', 'волокнистая (f)', 'шелковистая (k)', 'чешуйчатая (y)'], [2, 0, 1, 3]),
('поверхность_ножки_под_кольцом', ['гладкая (s)', 'волокнистая (f)', 'чешуйчатая (y)', 'шелковистая (k)'], [2, 0, 1, 3]),
('цвет_ножки_над_кольцом', ['белый (w)', 'серый (g)', 'розовый (p)', 'коричневый (n)', 'бежевый (b)', 'красный (e)', 'оранжевый (o)', 'цинамоновый (c)', 'жёлтый (y)'], [7, 3, 6, 4, 0, 2, 5, 1, 8]),
('цвет_ножки_под_кольцом', ['белый (w)', 'розовый (p)', 'серый (g)', 'бежевый (b)', 'коричневый (n)', 'красный (e)', 'жёлтый (y)', 'оранжевый (o)', 'цинамоновый (c)'], [7, 6, 3, 0, 4, 2, 8, 5, 1]),
('цвет_вуали', ['белый (w)', 'коричневый (n)', 'оранжевый (o)', 'жёлтый (y)'], [2, 0, 1, 3]),
('число_колец', ['одно (o)', 'два (t)', 'нет (n)'], [1, 2, 0]),
('тип_кольца', ['подвесное (p)', 'исчезающее (e)', 'большое (l)', 'расходящееся (f)', 'нет (n)'], [4, 0, 2, 1, 3]),
('цвет_спорового_порошка', ['чёрный (k)', 'коричневый (n)', 'пурпурный (u)', 'шоколадный (h)', 'белый (w)', 'зелёный (r)', 'оранжевый (o)', 'жёлтый (y)', 'бежевый (b)'], [2, 3, 6, 1, 7, 5, 4, 8, 0]),
('популяция', ['рассеянная (s)', 'нумерованная (n)', 'обильная (a)', 'несколько (v)', 'единичная (y)', 'скученная (c)'], [3, 2, 0, 4, 5, 1]),
('среда_обитания', ['городская (u)', 'травы (g)', 'лиственные (m)', 'луга (d)', 'тропинки (p)', 'мусор (w)', 'леса (l)'], [5, 1, 3, 0, 4, 6, 2]),

]

user_states = {}
#print
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
    choices.insert(14, 0)
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