import os

def get_files_in_directory(dir: str, include_file_extensions: list[str], ignored_dirs: list[str]) -> list[str]:
    """
    Get all files with specific extensions in a directory, excluding ignored directories.

    This function walks through the specified directory and its subdirectories,
    collecting files that match the given file extensions while ignoring
    specified directories.

    Args:
        dir (str): The root directory to start the search from.
        include_file_extensions (list[str]): A list of file extensions to include
            (e.g., ['.txt', '.py']). The extensions should include the dot.
        ignored_dirs (list[str]): A list of directory paths to ignore during the search.
            These should be full paths relative to the root directory.

    Returns:
        list[str]: A list of file paths (as strings) that match the criteria.

    Raises:
        OSError: If there's an error accessing the directory or its contents.

    Example:
        >>> root_dir = '/path/to/search'
        >>> extensions = ['.txt', '.py']
        >>> ignore = ['/path/to/search/ignore_me', '/path/to/search/temp']
        >>> files = get_files_in_directory(root_dir, extensions, ignore)
        >>> print(files)
        ['/path/to/search/file1.txt', '/path/to/search/subdir/script.py']
    """
    result: list[str] = []
    for dirpath, _, files in os.walk(dir):
        if any(ignored_dir in dirpath for ignored_dir in ignored_dirs):
            continue

        for file in files:
            if any(file.lower().endswith(ext) for ext in include_file_extensions):
                result.append(os.path.join(dirpath, file))

    return result