class DuplicateKeyError(Exception):
    """
    Raised when a duplicate key is found in the table.
    """
    pass

class DBTableNotExist(Exception):
    """
    Raised when a table does not exist in the database.
    """
    pass
