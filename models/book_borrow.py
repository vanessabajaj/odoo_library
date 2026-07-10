from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class BookBorrow(models.Model):
    _name = 'book.borrow'
    _description = 'Book Borrow'    

    book_id = fields.Many2one('book.property', string='Book',required=True)
    borrower_id = fields.Many2one('res.users', string='Borrower',required=True)   
    borrow_date = fields.Date(string='Borrow Date', default=fields.Date.today)
    return_date = fields.Date(string='Return Date')
    state = fields.Selection([("draft", "Draft"), ("borrowed", "Borrowed"), ("returned", "Returned")], string='State', default='draft')

    @api.constrains('borrow_date', 'return_date')
    def _check_return_after_borrow(self):
        for record in self:
            if record.return_date and record.borrow_date and record.return_date < record.borrow_date:
                raise ValidationError("The return date cannot be earlier than the borrow date.")

    def borrow_book(self):
        for record in self:
            if record.state == 'borrowed':
                raise UserError("This borrow record is already confirmed.")

            if record.book_id.available_copies <= 0:
                raise UserError("There are no available copies of this book.")

            active_borrows = record.borrower_id.borrowed_book_ids.filtered(
                lambda b: b.state == 'borrowed'
            )
            max_books = record.borrower_id.max_books
            if max_books and len(active_borrows) >= max_books:
                raise UserError(
                    "This borrower has reached the maximum of %s borrowed book(s). "
                    "Please return a book before borrowing another one." % max_books
                )

            record.borrow_date = fields.Date.today()
            record.state = 'borrowed'

    def return_book(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError("Only borrowed books can be returned.")

            record.return_date = fields.Date.today()
            record.state = 'returned'
