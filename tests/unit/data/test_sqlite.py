import unittest
from x_filter.data.database import SQLiteKeyValueStore

def setUpModule():
    global db
    db = SQLiteKeyValueStore()
    db.cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id TEXT PRIMARY KEY, data TEXT)")

def tearDownModule():
    # Close the database connection
    db.dispose_instance()

class TestSQLiteKeyValueStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_id_prefix = "test_"
        cls.current_test_id = 0

    @classmethod
    def tearDownClass(cls):
        pass

    def get_unique_id(self):
        TestSQLiteKeyValueStore.current_test_id += 1
        return f"{self.test_id_prefix}{TestSQLiteKeyValueStore.current_test_id}"

    def test_insert_and_query_data(self):
        unique_id = self.get_unique_id()
        db.insert('test_table', unique_id, {'name': 'John Doe'})
        result = db.query('test_table', unique_id)
        self.assertEqual(result, {'name': 'John Doe'})

    def test_update_data(self):
        unique_id = self.get_unique_id()
        db.insert('test_table', unique_id, {'name': 'John Doe'})
        db.update('test_table', unique_id, {'name': 'Jane Doe'})
        result = db.query('test_table', unique_id)
        self.assertEqual(result, {'name': 'Jane Doe'})

    def test_delete_data(self):
        unique_id = self.get_unique_id()
        db.insert('test_table', unique_id, {'name': 'John Doe'})
        db.delete('test_table', unique_id)
        result = db.query('test_table', unique_id)
        self.assertEqual(result, {})

    def test_data_exists(self):
        unique_id1 = self.get_unique_id()
        unique_id2 = self.get_unique_id()
        db.insert('test_table', unique_id1, {'name': 'John Doe'})
        self.assertTrue(db.exists('test_table', unique_id1))
        self.assertFalse(db.exists('test_table', unique_id2))

    def test_clear_table_with_safety(self):
        unique_id = self.get_unique_id()
        db.insert('test_table', unique_id, {'name': 'John Doe'})
        db.clear_table('test_table', 'CONFIRM')
        result = db.query('test_table', unique_id)
        self.assertEqual(result, {})

    def test_clear_table_without_safety(self):
        unique_id = self.get_unique_id()
        db.insert('test_table', unique_id, {'name': 'John Doe'})
        with self.assertRaises(ValueError):
            db.clear_table('test_table', 'NO_CONFIRM')

    def test_transaction_success(self):
        unique_id1 = self.get_unique_id()
        unique_id2 = self.get_unique_id()
        def operations():
            db.cursor.execute("INSERT INTO test_table (id, data) VALUES (?, ?)", (unique_id1, '{"name": "Jane Doe"}'))
            db.cursor.execute("INSERT INTO test_table (id, data) VALUES (?, ?)", (unique_id2, '{"name": "Jim Doe"}'))

        db.perform_transaction(operations)
        self.assertTrue(db.exists('test_table', unique_id1))
        self.assertTrue(db.exists('test_table', unique_id2))

    def test_transaction_failure(self):
        unique_id = self.get_unique_id()
        def operations():
            db.cursor.execute("INSERT INTO test_table (id, data) VALUES (?, ?)", (unique_id, '{"name": "Jane Doe"}'))
            raise Exception("Trigger transaction rollback")

        with self.assertRaises(Exception):
            db.perform_transaction(operations)
        self.assertFalse(db.exists('test_table', unique_id))

if __name__ == '__main__':
    unittest.main()
