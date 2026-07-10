from odoo import models, fields, api


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
            borrowed_count = len(record.borrow_ids.filter_borrowed())
            record.available_copies = record.copies - borrowed_count
