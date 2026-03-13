class SentioError(Exception):
    """Базовый тип ошибок приложения"""

    pass


class ServicesError(SentioError):
    pass


class NotFoundError(ServicesError):
    pass


class ConflictError(ServicesError):
    pass
