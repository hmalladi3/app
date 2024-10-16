from typing import List, Dict, Any, Optional, Callable
from uuid import UUID

class Table:
    def __init__(self, name: str):
        self.name = name
        self.data: List[Dict[str, Any]] = []

    def insert(self, row: Dict[str, Any]) -> None:
        self.data.append(row)

    def select(self, condition: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        if condition is None:
            return self.data
        return [row for row in self.data if condition(row)]

    def update(self, condition: Callable[[Dict[str, Any]], bool], updates: Dict[str, Any]) -> None:
        for row in self.data:
            if condition(row):
                row.update(updates)

    def delete(self, condition: Callable[[Dict[str, Any]], bool]) -> None:
        self.data = [row for row in self.data if not condition(row)]

    def add_column(self, column_name: str, default_value: Any = None) -> None:
        for row in self.data:
            row[column_name] = default_value

    def remove_column(self, column_name: str) -> None:
        for row in self.data:
            row.pop(column_name, None)

class Database:
    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def create_table(self, name: str) -> Table:
        if name not in self.tables:
            self.tables[name] = Table(name)
        return self.tables[name]

    def get_table(self, name: str) -> Table:
        return self.tables[name]

    def add_column(self, table_name: str, column_name: str, default_value: Any = None) -> None:
        table = self.get_table(table_name)
        table.add_column(column_name, default_value)

    def remove_column(self, table_name: str, column_name: str) -> None:
        table = self.get_table(table_name)
        table.remove_column(column_name)

# Create a global database instance
db = Database()

# Helper functions for common operations

def insert(table_name: str, row: Dict[str, Any]) -> None:
    db.get_table(table_name).insert(row)

def select(table_name: str, condition: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
    return db.get_table(table_name).select(condition)

def update(table_name: str, condition: Callable[[Dict[str, Any]], bool], updates: Dict[str, Any]) -> None:
    db.get_table(table_name).update(condition, updates)

def delete(table_name: str, condition: Callable[[Dict[str, Any]], bool]) -> None:
    db.get_table(table_name).delete(condition)

def add_column(table_name: str, column_name: str, default_value: Any = None) -> None:
    db.add_column(table_name, column_name, default_value)

def remove_column(table_name: str, column_name: str) -> None:
    db.remove_column(table_name, column_name)

# Example usage:
# db.create_table('items')
# insert('items', {'id': uuid4(), 'name': 'Item 1', 'description': 'Description 1'})
# items = select('items', lambda row: row['name'] == 'Item 1')
