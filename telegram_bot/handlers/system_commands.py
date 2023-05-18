from telegram import Bot, BotCommand


def set_up_commands(bot_instance: Bot) -> None:
    commands = {
        'menu': 'Menu',
<<<<<<< HEAD
        'invoices': 'Invoices',  # Show the invoices
        'services': 'Services',  # Show my or all services
        'tickets': 'Tickets',  # Create new or show the history
        'faq': 'FAQ',  # Do you need help?
=======
        'invoices': 'Invoices',
        'services': 'Services',
        'tickets': 'Tickets',
        'faq': 'FAQ',
>>>>>>> aa579aed2b7251e15f27c20cb1599c45fd92d20c
        'logout': 'Exit'
    }

    bot_instance.delete_my_commands()
    bot_instance.set_my_commands(
        commands=[BotCommand(command, description) for command, description in commands.items()]
    )


def delete_commands(bot_instance: Bot) -> None:
    commands = {'start': 'Begin'}

    bot_instance.delete_my_commands()
    bot_instance.set_my_commands(
        commands=[BotCommand(command, description) for command, description in commands.items()]
    )
