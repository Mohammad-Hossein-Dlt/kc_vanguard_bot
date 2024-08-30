from telegram import KeyboardButton, ReplyKeyboardMarkup
from raw_texts import (
    BUY_SERVICE,
    FREE_TEST,
    WALLET,
    RATES,
    SERVICE_MANAGEMENT,
    # GET_APP,
    CONNECTION_GUIDE,
    USER_PROFILE,
    SUPPORT,
    BACK_TO_HOME,
)


keys = [
    [
        KeyboardButton(text=BUY_SERVICE),
    ],
    [
        KeyboardButton(text=FREE_TEST),
        KeyboardButton(text=WALLET),

    ],
    [

        KeyboardButton(text=RATES),
        KeyboardButton(text=SERVICE_MANAGEMENT),
    ],
    [
        # KeyboardButton(text=GET_APP),
        KeyboardButton(text=CONNECTION_GUIDE),
        KeyboardButton(text=USER_PROFILE),
    ],
    [
        KeyboardButton(text=SUPPORT),
    ]
]
home_markup = ReplyKeyboardMarkup(
    keyboard=keys,
    resize_keyboard=True,
)


back = [
    [
        KeyboardButton(text=BACK_TO_HOME),
    ],
]
back_markup = ReplyKeyboardMarkup(
    keyboard=back,
    resize_keyboard=True,
)
