import importlib
import sys
import types
import unittest
from unittest import mock


def _install_odoo_stubs():
    if "odoo" in sys.modules:
        return

    class Field:
        def __init__(self, *args, **kwargs):
            pass

    class Date(Field):
        @staticmethod
        def today():
            return "today"

    def depends(*field_names):
        def decorator(method):
            return method

        return decorator

    odoo = types.ModuleType("odoo")
    odoo.api = types.SimpleNamespace(depends=depends)
    odoo.fields = types.SimpleNamespace(
        Char=Field,
        Date=Date,
        Integer=Field,
        Many2one=Field,
        One2many=Field,
        Selection=Field,
        Text=Field,
    )
    odoo.models = types.SimpleNamespace(
        Constraint=lambda *args: args,
        Model=object,
    )

    exceptions = types.ModuleType("odoo.exceptions")

    class UserError(Exception):
        pass

    exceptions.UserError = UserError
    sys.modules["odoo"] = odoo
    sys.modules["odoo.exceptions"] = exceptions


_install_odoo_stubs()

book_borrow = importlib.import_module("models.book_borrow")
book_property = importlib.import_module("models.book_property")
BookBorrow = book_borrow.BookBorrow
BookProperty = book_property.BookProperty
UserError = book_borrow.UserError


class RecordList(list):
    def filtered(self, predicate):
        return RecordList(record for record in self if predicate(record))


class BookBorrowTest(unittest.TestCase):
    def _borrow_record(
        self,
        *,
        state="draft",
        available_copies=1,
        existing_borrow_states=(),
    ):
        borrower = types.SimpleNamespace(
            borrowed_book_ids=RecordList(
                types.SimpleNamespace(state=existing_state)
                for existing_state in existing_borrow_states
            )
        )
        return types.SimpleNamespace(
            book_id=types.SimpleNamespace(available_copies=available_copies),
            borrower_id=borrower,
            borrow_date=None,
            return_date=None,
            state=state,
        )

    def test_borrow_book_confirms_available_book(self):
        record = self._borrow_record(existing_borrow_states=("returned",))

        with mock.patch.object(
            book_borrow.fields.Date,
            "today",
            return_value="2026-07-10",
        ):
            BookBorrow.borrow_book([record])

        self.assertEqual(record.borrow_date, "2026-07-10")
        self.assertEqual(record.state, "borrowed")

    def test_borrow_book_rejects_already_confirmed_record(self):
        record = self._borrow_record(state="borrowed")

        with self.assertRaisesRegex(UserError, "already confirmed"):
            BookBorrow.borrow_book([record])

    def test_borrow_book_rejects_unavailable_book(self):
        record = self._borrow_record(available_copies=0)

        with self.assertRaisesRegex(UserError, "no available copies"):
            BookBorrow.borrow_book([record])

    def test_borrow_book_rejects_borrower_with_active_loan(self):
        record = self._borrow_record(existing_borrow_states=("borrowed",))

        with self.assertRaisesRegex(UserError, "already has a borrowed book"):
            BookBorrow.borrow_book([record])

    def test_return_book_marks_borrowed_book_returned(self):
        record = self._borrow_record(state="borrowed")

        with mock.patch.object(
            book_borrow.fields.Date,
            "today",
            return_value="2026-07-11",
        ):
            BookBorrow.return_book([record])

        self.assertEqual(record.return_date, "2026-07-11")
        self.assertEqual(record.state, "returned")

    def test_return_book_rejects_non_borrowed_record(self):
        record = self._borrow_record()

        with self.assertRaisesRegex(UserError, "Only borrowed books"):
            BookBorrow.return_book([record])


class BookPropertyTest(unittest.TestCase):
    def test_compute_available_copies_excludes_active_borrows(self):
        record = types.SimpleNamespace(
            copies=4,
            borrow_ids=RecordList(
                [
                    types.SimpleNamespace(state="borrowed"),
                    types.SimpleNamespace(state="returned"),
                    types.SimpleNamespace(state="borrowed"),
                ]
            ),
            available_copies=None,
        )

        BookProperty._compute_available_copies([record])

        self.assertEqual(record.available_copies, 2)


if __name__ == "__main__":
    unittest.main()
