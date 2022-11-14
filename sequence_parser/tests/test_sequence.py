from odoo.tests.common import TransactionCase


class TestSequence(TransactionCase):
    def create_sequence(self, prefix, suffix):
        return self.env["ir.sequence"].create(
            {
                "name": "sequence",
                "prefix": prefix,
                "suffix": suffix,
                "padding": 2,
            }
        )

    def test_standard(self):
        sequence = self.create_sequence("P", "S")
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertTrue(isinstance(value, int))

    def test_standard_dc(self):
        sequence = self.create_sequence("P", "S")
        sequence.write({"check_digit_formula": "ISO7064_37_36"})
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertNotEqual(dc, "")
        self.assertTrue(isinstance(value, int))

    def test_no_gap(self):
        sequence = self.create_sequence("P", "S")
        sequence.write({"implementation": "no_gap"})
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertTrue(isinstance(value, int))

    def test_standard_date(self):
        sequence = self.create_sequence("P", "S")
        sequence.write({"use_date_range": True})
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertEqual(dc, "")
        self.assertTrue(isinstance(value, int))

    def test_standard_date_dc(self):
        sequence = self.create_sequence("P", "S")
        sequence.write({"use_date_range": True, "check_digit_formula": "ISO7064_37_36"})
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertNotEqual(dc, "")
        self.assertTrue(isinstance(value, int))

    def test_no_gap_date(self):
        sequence = self.create_sequence("P", "S")
        sequence.write({"implementation": "no_gap", "use_date_range": True})
        self.assertTrue(isinstance(sequence.next_by_id(), str))
        result = sequence.with_context(sequence_tuple=True).next_by_id()
        self.assertTrue(isinstance(result, tuple))
        prefix, value, suffix, dc, seq = result
        self.assertEqual(prefix, "P")
        self.assertEqual(suffix, "S")
        self.assertEqual(dc, "")
        self.assertTrue(isinstance(value, int))
