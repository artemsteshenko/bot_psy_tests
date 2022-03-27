
TOKEN = '5284807030:AAGqW96sGN2sXItVZdCvQd4JCEOb4GJ86nc'

import os
import logging
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

# Stages
SAVE, RESULT, QUASTION = range(8, 11)
# Callback data
ONE, TWO, THREE, FOUR = range(4 ,8)

FULLY_AGREE, AGREE, DISAGREE = '1', '2', '3'
answers = {'1': 'Полностью согласен', '2': 'Согласен', '3': 'Не согласен'}

TEXT = '''Все поведенческие стратегии, которые формируются у человека в процессе жизни, можно подразделить на три большие группы:

• Стратегия разрешения проблем – это активная поведенческая стратегия, при которой человек старается использовать все имеющиеся у него личностные ресурсы для поиска возможных способов эффективного разрешения проблемы.

• Стратегия поиска социальной поддержки – это активная поведенческая стратегия, при которой человек для эффективного разрешения проблемы обращается за помощью и поддержкой к окружающей его среде: семье, друзьям, значимым другим.

• Стратегия избегания – это поведенческая стратегия, при которой человек старается избежать контакта с окружающей его действительностью, уйти от решения проблем. Человек может использовать пассивные способы избегания, например, уход в болезнь или употребление алкоголя, наркотиков, может совсем «уйти от решения проблем», использовав активный способ избегания – суицид.

Стратегия избегания – одна из ведущих поведенческих стратегий при формировании дезадаптивного, псевдосовладающего поведения. Она направлена на преодоление или снижение дистресса человеком, который находится на более низком уровне развития. Использование этой стратегии обусловлено недостаточностью развития личностно-средовых копинг-ресурсов и навыков активного разрешения проблем. Однако она может носить адекватный либо неадекватный характер в зависимости от конкретной стрессовой ситуации, возраста и состояния ресурсной системы личности.

Наиболее эффективным является использование всех трех поведенческих стратегий, в зависимости от ситуации. В некоторых случаях человек может самостоятельно справиться с возникшими трудностями, в других ему требуется поддержка окружающих, в третьих он просто может избежать столкновения с проблемной ситуацией, заранее подумав о ее негативных последствиях.'''

QUASTIONS = ['Позволяю себе поделиться чувством с другом.',
             'Стараюсь все сделать так, чтобы иметь возможность наилучшим образом решить проблему.' ,
             'Осуществляю поиск всех возможных решений, прежде чем что-то предпринять.',
             'Пытаюсь отвлечься от проблемы.', 'Принимаю сочувствие и понимание от кого-либо.',
             'Делаю все возможное, чтобы не дать окружающим увидеть, что мои дела плохи.',
             'Обсуждаю ситуацию с людьми, так как обсуждение помогает мне чувствовать себя лучше.',
             'Ставлю для себя ряд целей, позволяющих постепенно справляться с ситуацией.',
             'Очень тщательно взвешиваю возможности выбора.', 'Мечтаю, фантазирую о лучших временах.',
             'Пытаюсь различными способами решать проблему, пока не найду подходящий.',
             'Доверяю свои страхи родственнику или другу.', 'Больше времени, чем обычно, провожу одна.',]
             # 'Рассказываю другим людям о ситуации, так как только ее обсуждение помогает мне прийти к ее разрешению.',
             # 'Думаю о том, что нужно сделать, чтобы исправить положение.',
             # 'Сосредотачиваюсь полностью на решении проблемы.', 'Обдумываю про себя план действий.',
             # 'Смотрю телевизор дольше, чем обычно.',
             # 'Иду к кому-нибудь (другу или специалисту), чтобы он помог мне чувствовать себя лучше.',
             # 'Стою твердо и борюсь за то, что мне нужно в этой ситуации.', 'Избегаю общения с людьми.',
             # 'Переключаюсь на хобби или занимаюсь спортом, чтобы избежать проблем.',
             # 'Иду к другу за советом – как исправить ситуацию.',
             # 'Иду к другу, чтобы он помог мне лучше почувствовать проблему.',
             # 'Принимаю сочувствие, взаимопонимание друзей.',
             # 'Сплю больше обычного.', 'Фантазирую о том, что все могло бы быть иначе.',
             # 'Представляю себя героем книги или кино.', 'Пытаюсь решить проблему.',
             # 'Хочу, чтобы люди оставили меня одну.', 'Принимаю помощь от друзей или родственников.',
             # 'Ищу успокоения у тех, кто знает меня лучше.',
             # 'Пытаюсь тщательно планировать свои действия, а не действовать импульсивно под влиянием внешнего побуждения.']

problem_coeffs = [-0.0 ,-1.0 ,-1.0 ,-0.0 ,-0.0 ,-0.0 ,0.0 ,-1.0 ,-1.0 ,-0.0 ,-1.0 ,-0.0 ,-0.0 ,-0.0 ,-1.0 ,-1.0 ,-1.0
                  ,0.0 ,0.0 ,-1.0 ,0.0 ,0.0 ,0.0,
-0.0 ,-0.0 ,-0.0 ,0.0 ,-0.0 ,-1.0 ,-0.0 ,0.0 ,0.0 ,-1.0 ,44.0]

social_coeffs = [-0.0 ,-1.0 ,0.0 ,-0.0 ,0.0 ,-1.0 ,0.0 -1.0 ,0.0 ,-0.0 ,-0.0 ,0.0 ,-1.0 ,0.0 ,-1.0 ,-0.0 ,0.0 ,-0.0
                 ,-0.0 ,-1.0 ,-0.0 ,0.0 ,0.0 ,-1.0 ,-1.0,
-1.0 ,0.0 ,0.0 ,0.0 ,0.0 ,-0.0 ,-1.0 ,-1.0 ,0.0 ,44.0]

avoid_coeffs = [-0.0 ,0.0 ,0.0 ,-0.0 ,-1.0 ,0.0 ,-1.0 ,-0.0 ,-0.0 ,0.0 ,-1.0 ,0.0 ,-0.0 ,-1.0 ,0.0 ,-0.0 ,0.0 ,-0.0
                ,-1.0 ,-0.0 ,-0.0 ,-1.0,
 -1.0 ,-0.0 ,0.0 ,-0.0 ,-1.0 ,-1.0 ,-1.0 ,0.0 ,-1.0 ,-0.0 ,0.0 ,0.0 ,44.0]


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    global all
    all = []
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Тест на переживание перемен", callback_data=str(ONE)),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Выберите тест:", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return QUASTION


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Test 1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)

    return QUASTION


def result(update: Update, context: CallbackContext) -> int:
    problem_res = problem_coeffs[-1]
    social_res = problem_coeffs[-1]
    avoid_res = problem_coeffs[-1]
    for i in range(len(all)):
        problem_res += int(all[i]) * problem_coeffs[i]
        social_res += int(all[i]) * social_coeffs[i]
        avoid_res += int(all[i]) * avoid_coeffs[i]

    bot = Bot(token=TOKEN)
    TELEGRAM_CHAT_ID = update.callback_query.message.chat_id
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=TEXT)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Ваш результат:\nСтратегия разрешения проблем: {str(problem_res)}\nСтратегия поиска социальной поддержки: {str(social_res)}\nСтратегия избегания: {str(avoid_res)}\n\n")



def one(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    print(update)
    query.answer()
    print(query)
    keyboard = [
        [
            InlineKeyboardButton("Полностью согласен", callback_data=str(FULLY_AGREE)),
            InlineKeyboardButton("Согласен", callback_data=str(AGREE)),
            InlineKeyboardButton("Не согласен", callback_data=str(DISAGREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print(QUASTIONS[len(all)])

    query.edit_message_text(
        text=QUASTIONS[len(all)], reply_markup=reply_markup
    )
    return SAVE


def two(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    # query.answer()
    print(query)
    print(query.message.text, query.message.reply_markup.inline_keyboard[0][0].text)
    all.append(query.data)
    print(all)

    keyboard = [
        [
            InlineKeyboardButton(f"Далее", callback_data=str(ONE)),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Ваш ответ \"{answers[all[-1]]}\"", reply_markup=reply_markup
    )
    if len(QUASTIONS) != len(all):
        return QUASTION
    else:
        return RESULT


def three(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, let's do it again!", callback_data=str(ONE)),
            InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Third CallbackQueryHandler. Do want to start over?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return RESULT





def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUASTION: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),

            ],
            SAVE: [

                CallbackQueryHandler(two, pattern='^' + str(FULLY_AGREE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(AGREE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(DISAGREE) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),

            ],
            RESULT: [

                CallbackQueryHandler(result, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
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

