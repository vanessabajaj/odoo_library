{
    'name':'Library',
    'depends':['base'],
    'application':True,
    'data' : [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/book_property_view.xml',
        "views/book_property_type_view.xml",
        "views/book_borrow_view.xml",
        
        "views/library_menus.xml",
    ]
}