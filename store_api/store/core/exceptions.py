class StoreException(Exception):
    message: str = "Erro interno"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundException(StoreException):
    message = "Registro não encontrado"


class InsertionException(StoreException):
    message = "Não foi possível inserir o registro"
