def split_list_into_chunks(lst: list, chunk_size: int) -> list[list]:
    """
    Divide a list into chunks of specified size.

    Args:
        lst (list): List to be chunked.
        chunk_size (int): Max size of each chunk.

    Returns:
        list[list]: List of chunked lists.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]