class ReleaseNotFoundError(Exception):
    pass


class InvalidVersionError(Exception):
    pass


class AlreadyInstalledError(Exception):
    pass


class BinaryNotFoundError(Exception):
    pass


class NotInstalledError(Exception):
    pass
