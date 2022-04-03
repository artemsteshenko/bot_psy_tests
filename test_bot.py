
TOKEN = '5178260352:AAHVZ1RI6YfNdUIwHczMq7CIMv2Z0dw8xTI'

import os
import logging
import pickle
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)
PORT = int(os.environ.get('PORT', 443))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

with open('answers.pickle', 'rb') as f:
    ANSWERS = pickle.load(f)

with open('questions.pickle', 'rb') as f:
    QUESTIONS = pickle.load(f)

with open('test_models.pickle', 'rb') as f:
    MODELS = pickle.load(f)

with open('test_texts.pickle', 'rb') as f:
    TEXTS = pickle.load(f)

with open('test_names.pickle', 'rb') as f:
    TEST_NAMES = pickle.load(f)

ans_names = []
for key in ANSWERS:
    for ans in ANSWERS[key]:
        ans_names.append(ans)
ans_names = list(set(ans_names))

# Stages
SAVE, RESULT, QUESTION, MENU = range(8, 12)
# Callback data
TEST_NAME = 'amirkhan'


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    global MEMORY
    MEMORY = []
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [InlineKeyboardButton(TEST_NAMES[test_name], callback_data=test_name)] for test_name in TEST_NAMES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите тест", reply_markup=reply_markup)
    return QUESTION


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    query = update.callback_query
    query.answer()
    global MEMORY
    MEMORY = []
    keyboard = [
        [InlineKeyboardButton(TEST_NAMES[test_name], callback_data=test_name)] for test_name in TEST_NAMES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите тест", reply_markup=reply_markup)

    return QUESTION


def result(update: Update, context: CallbackContext) -> int:
    result_output = {}
    result_text = 'Ваш результат:'
    print('result')

    for model_name in MODELS[TEST_NAME]:
        model = MODELS[TEST_NAME][model_name]
        regressor = model[1][0]
        print(model_name, regressor)
        result_output[model_name] = round(regressor.predict(pd.DataFrame(np.array(MEMORY).reshape(1,-1)))[0],2)
        result_text += f'\n{model_name}: {str(result_output[model_name])}'

    keyboard = [
        [
            InlineKeyboardButton(f"Выбрать тест", callback_data=MENU),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.edit_message_text(
        text=TEXTS[TEST_NAME]+'\n\n\n'+result_text,
        reply_markup=reply_markup
    )
    return MENU


def question(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    global TEST_NAME

    query = update.callback_query
    TEST_NAME = query.data
    query.answer()
    keyboard = [[InlineKeyboardButton(ans, callback_data=ans)] for ans in ANSWERS[TEST_NAME]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=QUESTIONS[TEST_NAME][len(MEMORY)], reply_markup=reply_markup
    )
    return SAVE


def save(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    MEMORY.append(ANSWERS[TEST_NAME][query.data])

    keyboard = [
        [
            InlineKeyboardButton(f"Далее", callback_data=str(TEST_NAME)),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Ваш ответ \"{query.data}\"\nПройдено {len(MEMORY)} из {len(QUESTIONS[TEST_NAME])}", reply_markup=reply_markup
    )

    if len(QUESTIONS[TEST_NAME]) != len(MEMORY):
        return QUESTION
    else:
        return RESULT


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [
                CallbackQueryHandler(question, pattern='^' + str(test_name) + '$')
                for test_name in TEST_NAMES
            ],
            SAVE: [CallbackQueryHandler(save, pattern='^' + str(answer) + '$')
                   for answer in ans_names],
            RESULT: [
                CallbackQueryHandler(result, pattern='^' + str(test_name) + '$')
                for test_name in TEST_NAMES
            ],
            MENU: [
                CallbackQueryHandler(start_over, pattern='^' + str(MENU) + '$')
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url='https://ancient-waters-23105.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()