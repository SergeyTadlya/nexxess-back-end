from invoices.models import Invoice


def get_invoices(user_email, status=None):
    all_invoices = Invoice.objects.filter(responsible=user_email).order_by('-date')

    return all_invoices if status is None else all_invoices.filter(status__value=status)


def get_current_page(callback_title):
    parsed_data = callback_title.split('_')
    if len(parsed_data) == 1:
        return len(parsed_data)

    current_page = parsed_data[2]

    if parsed_data[0] == 'New':
        current_page = int(current_page)

    elif parsed_data[0] == 'Paid':
        current_page = int(current_page)

    elif parsed_data[0] == 'Unpaid':
        current_page = int(current_page)

    elif parsed_data[0] == 'All':
        current_page = int(current_page)

    return current_page


def do_pagination(invoices, current_page, elements_on_page=10):

    invoices_quantity = len(invoices)
    all_pages = elements_on_page if invoices_quantity % elements_on_page == 0 else (invoices_quantity // elements_on_page) + 1
    invoices = invoices[(current_page - 1) * elements_on_page: current_page * elements_on_page]
    has_pages = True if invoices_quantity > elements_on_page else False

    result = {
        'quantity': invoices_quantity,
        'all_pages': all_pages,
        'invoices': invoices,
        'has_pages': has_pages,
    }

    return result
