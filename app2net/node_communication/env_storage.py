import sqlite3
import pickle

class EnvStorage:
    """Key-Value storage providing a friendly dict-like interface"""

    def __init__(self, db):
        """Connect to database
        
        Arguments:
            db (str): Path to SQLite database
        """
        self.db = sqlite3.connect(db)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS env ("
                "key TEXT PRIMARY KEY,"
                "value TEXT"
            ")"
        )

    def __getitem__(self, key):
        """Alias for `get`"""
        return self.get(key)

    def get(self, key):
        """Retrieve value associated with provided key
        
        Arguments:
            key (str): key to search
        
        Return:
            Any: Value stored on db, if it exists
        
        Raises:
            - KeyError: If key does not exist on db
        """
        cursor = self.db.execute("SELECT value FROM env WHERE key=?", [key])
        data = list(cursor)
        if data:
            return self._deserialize(data[0][0])
        else:
            raise KeyError("Env has no specified key")

    def __setitem__(self, key, value):
        self.set(key, value)
    
    def set(self, key, value):
        try: 
            self.get(key)
            self.db.execute("UPDATE env SET value=? WHERE key=?;", [self._serialize(value), key])
        except KeyError:
            self.db.execute("INSERT INTO env VALUES (?, ?);", [key, self._serialize(value)])
        self.db.commit()
    
    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    @staticmethod
    def _serialize(value):
        return pickle.dumps(value)

    @staticmethod
    def _deserialize(value):
        return pickle.loads(value)

    def __delitem__(self, key):
        self.delete(key)

    def delete(self, key):
        self.db.execute("DELETE FROM env WHERE key=?", [key])
        self.db.commit()
