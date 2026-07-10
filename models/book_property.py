from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BookProperty(models.Model):
    _name = 'book.property'
    _description = 'Book Property'
    _rec_name = 'title'

    title = fields.Char(required=True)
    author = fields.Char()
    isbn = fields.Char()
    copies = fields.Integer(string="Total Copies", default=1)
    book_type_id = fields.Many2one('book.property.type', string='Book Type')
    summary = fields.Text()
    available_copies = fields.Integer(string="Available Copies",compute="_compute_available_copies",store=True)

    borrow_ids = fields.One2many('book.borrow', 'book_id', string='Borrow Records')

    
    @api.depends('copies', 'borrow_ids.state')
    def _compute_available_copies(self):
        for record in self:
            borrowed_count = len(record.borrow_ids.filtered(lambda b: b.state == 'borrowed'))
            record.available_copies = record.copies - borrowed_count

    @api.constrains('copies', 'borrow_ids')
    def _check_copies(self):
        for record in self:
            if record.copies < 0:
                raise ValidationError("The number of copies cannot be negative.")

            borrowed_count = len(record.borrow_ids.filtered(lambda b: b.state == 'borrowed'))
            if record.copies < borrowed_count:
                raise ValidationError(
                    "Cannot set total copies (%s) below the number of currently "
                    "borrowed copies (%s)." % (record.copies, borrowed_count)
                )
