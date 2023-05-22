from invoices.models import Invoice, Status
from invoices.views import format_date, format_price

import fitz


def get_invoice_by_id(invoice_id, status_name):
    invoice = Invoice.objects.filter(invoice_id=invoice_id)
    if invoice.exists():
        invoice = invoice.first()

    if invoice.status.value == 'New':
        invoice.status = Status.objects.get(value='Opened')
        invoice.save()

    return invoice


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
