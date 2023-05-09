from typing import Dict

from telegram import Bot, BotCommand


def set_up_commands(bot_instance: Bot) -> None:
    commands: Dict[str, str] = {
        'menu': 'Menu',
        'invoices': 'Show the invoices',
        'services': 'Show my or all services',
        'tickets': 'Create new or show the history',
        'faq': 'Do you need help?',
        'logout': 'Support'
    }

    bot_instance.delete_my_commands()
    bot_instance.set_my_commands(
        commands=[BotCommand(command, description) for command, description in commands.items()]
    )


def delete_commands(bot_instance: Bot) -> None:
    bot_instance.delete_my_commands()
    commands: Dict[str, str] = {'start': 'Begin'}

    bot_instance.set_my_commands(
        commands=[BotCommand(command, description) for command, description in commands.items()]
    )
