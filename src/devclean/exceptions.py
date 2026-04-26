class DevCleanError(Exception):
    """base class for all devclean exceptions"""
    pass

class ScanError(DevCleanError):
    """Raised when the filepath is wrong or not existing""" 
    def __init__(self, filepath: str, message = "Invaild Path"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)

class CleanError(DevCleanError):
    """Raised when the folder/file cant be deleted"""
    def __init__(self, name: str, message = "Unable to delete"):
        self.name = name
        self.message = f"{message}: {name}"
        super().__init__(self.message)