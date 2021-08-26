# ============================================================================
# =========================== Parsing stage exceptions =======================
# ============================================================================

class ParseStructureError(TypeError):
    """
    The base type of exception for exceptions at parsing stage.
    """

    pass


class ParseMismatchLength(ParseStructureError):
    """
    Mismatching between expected and received data lengths
    """

    def __init__(self, field_name: str, received: int, expected: int):
        """Get error info and forward formatted message to super"""
        message = f'Length of {field_name} should be: {expected}; ' \
                  f'received: {received}.'
        super().__init__(message)
