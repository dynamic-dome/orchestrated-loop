from __future__ import annotations


class LoopChatError(Exception):
    """Chat adapter error wrapping HTTP and API failures.

    Attributes:
        status_code: HTTP status code if available (e.g., 401, 429, 500)
        body: Response body or error message
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"{base} (HTTP {self.status_code})"
        return base
