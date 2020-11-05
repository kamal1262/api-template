class UserNotFoundException(Exception):
    """Raise when user not found"""

    def __init__(self, description):
        self.description = description
        self.code = 404

    pass
