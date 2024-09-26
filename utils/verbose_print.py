from pprint import pprint

from utils.env import get_verbose

def verbose_print(*values: str) -> None:
    if get_verbose():
        pprint(*values)
