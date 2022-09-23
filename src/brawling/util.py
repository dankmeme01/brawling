__all__ = [
    "catching",
    "RequestPaginator"
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

class RequestPaginator:
    def __init__(self, client, url: str, per_page: int, max: int, cls_factory):
        self.client = client
        self.url = url
        self.limit = per_page
        self.cls = cls_factory
        self.done = 0
        self.max = max

    def __iter__(self):
        marker = None
        while True:
            if self.max != 0 and self.done >= self.max:
                break

            params = {
                "limit": self.limit
            }

            if marker:
                params["after"] = marker

            page = self.client._get(self.url, params)

            # im lazy
            if type(page).__name__.endswith('ErrorResponse'):
                return page

            items = self.client._unwrap_list(page["items"], self.cls)
            if len(items) == 0:
                break

            self.done += len(items)
            if self.max != 0 and self.done > self.max:
                diff = self.done - self.max
                items = items[:-diff]

            marker = page["paging"]["cursors"].get("after", None)

            yield items

            if marker is None:
                break
