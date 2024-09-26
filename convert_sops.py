
import os
from sops.utils.convert_word_to_markdown import convert_word_to_markdown
from sops.utils.reformat_markdown import reformat_markdown
from utils.get_files_in_directory import get_files_in_directory


def main() -> None:
    sops_dir: str = 'sops/reports/'
    file_paths: list[str] = get_files_in_directory(sops_dir, ['.doc', '.docx'], [])

    for file_path in file_paths:
        root, _ = os.path.splitext(file_path)
        output_file: str = root + ".md"
        convert_word_to_markdown(file_path, output_file)

        if os.path.exists(output_file):
            reformat_markdown(output_file, output_file)


if __name__ == '__main__':
    main()