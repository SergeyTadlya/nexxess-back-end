from .bitrix import BitrixHelper


class PaymentHelper:
    """This class using when pressing the 'Pay' button in Invoice Detail card."""

    @staticmethod
    def is_file_signed(contact, invoice) -> bool:
        """Check is file was signed
        In invoice we store reference ID of file

        In contact we store reference IDs of files which were signed

        Returns:
            bool: If file signed return True, False otherwise.
        """

        return invoice[BitrixHelper.INVOICE_SIGNED_FILE] in contact[BitrixHelper.CONTACT_SIGNED_FILES]
