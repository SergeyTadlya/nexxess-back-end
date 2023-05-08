from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def faqs_topics_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Topic 1', callback_data='faq_topic1'),
         InlineKeyboardButton('Topic 2', callback_data='faq_topic2')],
        [InlineKeyboardButton('Topic 3', callback_data='faq_topic3'),
         InlineKeyboardButton('Topic 4', callback_data='faq_topic4')],
        [InlineKeyboardButton('Topic 5', callback_data='faq_topic5'),
         InlineKeyboardButton('Topic 6', callback_data='faq_topic6')]
    ]

    return InlineKeyboardMarkup(buttons)
