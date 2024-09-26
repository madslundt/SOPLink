import hashlib


def get_file_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Args:
        file_path (str): Path to the file to hash.

    Returns:
        str: The SHA-256 hash of the file.
    """
    hash = hashlib.sha256()
    buffer_size = 65536
    with open(file_path, 'rb') as file:
        while chunk := file.read(buffer_size):
            hash.update(chunk)

    return hash.hexdigest()


def get_content_hash(text: str) -> str:
    """
    Generate a SHA-256 hash for the given text.

    Args:
        text (str): Text to generate hash for.

    Returns:
        str: The SHA-256 hash of the text.
    """
    return hashlib.sha256(text.encode()).hexdigest()