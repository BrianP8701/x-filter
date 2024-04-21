# python scripts/database.py
from x_filter.data import Database

db = Database()


# db.create_tables(['users', 'filters', 'conversations', 'events'])


db.clear_table('conversations', 'CONFIRM')
db.clear_table('filters', 'CONFIRM')
db.clear_table('events', 'CONFIRM')
db.clear_table('users', 'CONFIRM')