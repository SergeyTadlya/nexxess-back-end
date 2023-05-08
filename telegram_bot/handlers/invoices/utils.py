from invoices.models import Invoice
from invoices.views import format_date, format_price

import fitz


def get_invoice_by_id(invoice_id):
    invoice = Invoice.objects.filter(invoice_id=invoice_id)
    if invoice.exists():
        invoice = invoice.first()
    return invoice


def get_invoices(user_email, status=None):
    all_invoices = Invoice.objects.filter(responsible=user_email).order_by('-date')

    return all_invoices if status is None else all_invoices.filter(status__value=status)


def get_current_page(callback_title):
    parsed_data = callback_title.split('_')
    if len(parsed_data) == 1:
        return len(parsed_data)

    return int(parsed_data[1])  # Current page


def do_pagination(invoices, current_page, elements_on_page=10):

    current_page = int(current_page)

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


# def set_file_path(invoice):
#     pass


def generate_new_pdf(user, invoice, pdf_path):
    pdf_file = fitz.open(pdf_path)

    # Load the first page of the PDF
    page = pdf_file.load_page(0)

    # Insert the invoice id
    page.insert_text(fitz.Point(115, 206), str(invoice.invoice_id), fontsize=16)

    # Insert the date
    page.insert_text(fitz.Point(105, 225), str(format_date(invoice.date)))
    data = str(user.first_name) + ' ' + str(user.last_name)
    page.insert_text(fitz.Point(100, 342), str(invoice.product_title), fontsize=12)

    # Insert the due date
    page.insert_text(fitz.Point(95, 241), str(format_date(invoice.due_date)))
    page.insert_text(fitz.Point(105, 283), str(data), fontsize=14)

    # Insert the price
    page.insert_text(fitz.Point(469, 343), str(format_price(invoice.price)))
    page.insert_text(fitz.Point(469, 400), str(format_price(invoice.price)))
    page.insert_text(fitz.Point(469, 492), str(format_price(invoice.price)))

    # Save the modified PDF with a new name
    new_file_path = 'pdf_client/invoice_' + invoice.invoice_id + '.pdf'
    pdf_file.save(new_file_path)

    return new_file_path
