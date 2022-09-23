__all__ = [
    "catching"
]

class catching:
    def __init__(self, on_error: str = None) -> None:
        self.success = None
        self.on_error = on_error

    def __enter__(self):
        self.success = True

    def __exit__(self, type_, value, traceback_):
        self.success = False
        if self.on_error:
            print(self.on_error)
            print(value)
        return True