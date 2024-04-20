import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Any, Dict
import sqlite3
import json

load_dotenv()
db_connection_string = os.getenv("DB_CONNECTION_STRING")

class Database(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Initialization should remain flexible for subclass implementations.

    @abstractmethod
    def dispose_instance(self) -> None:
        """
        Disposes of the database instance, effectively clearing any existing connections.
        """
        pass

    @abstractmethod
    def insert(self, table_name: str, data: Dict) -> None:
        """
        Inserts a new data entry into the specified table.
        
        :param table_name: The table name.
        :param data: The dictionary to be serialized and stored, containing the 'id' key.
        """
        pass

    @abstractmethod
    def update(self, table_name: str, data: Dict) -> None:
        """
        Updates an existing data entry in the specified table.
        
        :param table_name: The table name.
        :param data: The updated dictionary to be serialized and stored, containing the 'id' key.
        """
        pass

    @abstractmethod
    def delete(self, table_name: str, data: Dict) -> None:
        """
        Deletes a data entry from the specified table using its identifier inside the data dict.
        
        :param table_name: The table name.
        :param data: The dictionary containing the 'id' key of the data to delete.
        """
        pass

    @abstractmethod
    def query(self, table_name: str, id: str) -> Dict:
        """
        Queries the database for a data entry by its identifier inside the data dict.
        
        :param table_name: The table name.
        :param id: The identifier of the data.
        :return: The deserialized dictionary representing the data.
        """
        pass

    @abstractmethod
    def exists(self, table_name: str, data: Dict) -> bool:
        """
        Checks if a data entry exists in the database using its identifier inside the data dict.
        
        :param table_name: The table name.
        :param data: The dictionary containing the 'id' key of the data.
        :return: True if the data exists, False otherwise.
        """
        pass

    @abstractmethod
    def execute_raw_query(self, query: str) -> Any:
        """
        Executes a raw SQL query against the database.
        
        :param query: The SQL query to execute.
        :return: The result of the query execution.
        """
        pass

    @abstractmethod
    def perform_transaction(self, operations: callable) -> None:
        """
        Performs a series of operations within a database transaction.
        
        :param operations: A callable that contains the operations to be performed.
        """
        pass

    @abstractmethod
    def clear_table(self, table_name: str, safety: str) -> None:
        """
        Clears all data from a specified table. This operation is irreversible.
        
        :param table_name: The table to be cleared.
        :param safety: A safety string that must match a specific value to confirm the operation.
        """
        pass

class SQLiteKeyValueStore(Database):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLiteKeyValueStore, cls).__new__(cls)
            db_path = db_connection_string
            cls._instance.connection = sqlite3.connect(db_path, check_same_thread=False)
            cls._instance.cursor = cls._instance.connection.cursor()
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self, tables: list = []):
        for table in tables:
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (id TEXT PRIMARY KEY, data TEXT)"
            )
        self.connection.commit()

    def dispose_instance(self) -> None:
        self.connection.close()

    def insert(self, table_name: str, data: Dict) -> None:
        data_id = data.pop('id')
        serialized_data = json.dumps(data)
        self.cursor.execute(
            f"INSERT INTO {table_name} (id, data) VALUES (?, ?)",
            (data_id, serialized_data)
        )
        self.connection.commit()

    def update(self, table_name: str, data: Dict) -> None:
        data_id = data.pop('id')
        serialized_data = json.dumps(data)
        self.cursor.execute(
            f"UPDATE {table_name} SET data = ? WHERE id = ?",
            (serialized_data, data_id)
        )
        self.connection.commit()

    def delete(self, table_name: str, data: Dict) -> None:
        data_id = data.pop('id')
        self.cursor.execute(
            f"DELETE FROM {table_name} WHERE id = ?",
            (data_id,)
        )
        self.connection.commit()

    def query(self, table_name: str, data_id: str) -> Dict:
        self.cursor.execute(
            f"SELECT data FROM {table_name} WHERE id = ?",
            (data_id,)
        )
        result = self.cursor.fetchone()
        if result:
            result = json.loads(result[0])
            result['id'] = data_id
            return result
        else:
            raise KeyError(f"No data found for ID: {data_id}")

    def exists(self, table_name: str, id: str) -> bool:
        self.cursor.execute(
            f"SELECT 1 FROM {table_name} WHERE id = ?",
            (id,)
        )
        return bool(self.cursor.fetchone())

    def execute_raw_query(self, query: str) -> Any:
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def perform_transaction(self, operations: callable) -> None:
        try:
            self.connection.execute("BEGIN")
            operations()
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def clear_table(self, table_name: str, safety: str) -> None:
        if safety == "CONFIRM":
            self.cursor.execute(f"DELETE FROM {table_name}")
            self.connection.commit()
        else:
            raise ValueError("Safety check failed; clear_table operation aborted.")

