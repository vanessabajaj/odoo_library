from odoo import models, fields, api
from odoo.exceptions import UserError

from . import constants


class BookBorrow(models.Model):
    _name = 'book.borrow'
    _description = 'Book Borrow'    

    book_id = fields.Many2one('book.property', string='Book',required=True)
    borrower_id = fields.Many2one('res.users', string='Borrower',required=True)   
    borrow_date = fields.Date(string='Borrow Date', default=fields.Date.today)
    return_date = fields.Date(string='Return Date')
    state = fields.Selection(constants.BORROW_STATE_SELECTION, string='State', default=constants.STATE_DRAFT)

    def filter_borrowed(self):
        """Return the records in this recordset that are currently borrowed."""
        return self.filtered(lambda b: b.state == constants.STATE_BORROWED)

    def borrow_book(self):
        for record in self:
            if record.state == constants.STATE_BORROWED:
                raise UserError("This borrow record is already confirmed.")

            if record.book_id.available_copies <= 0:
                raise UserError("There are no available copies of this book.")
            
            if record.borrower_id.borrowed_book_ids.filter_borrowed():
                raise UserError("This borrower already has a borrowed book. Please return it before borrowing another one.")

            record.borrow_date = fields.Date.today()
            record.state = constants.STATE_BORROWED

    def return_book(self):
        for record in self:
            if record.state != constants.STATE_BORROWED:
                raise UserError("Only borrowed books can be returned.")

            record.return_date = fields.Date.today()
            record.state = constants.STATE_RETURNED
