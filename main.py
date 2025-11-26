import re
import os
from pathlib import Path


def read_quiz_files():
    quiz_questions_path = Path("quiz_questions/")

    contents = []
    for filename in os.listdir(quiz_questions_path):
        file_path = os.path.join(quiz_questions_path, filename)

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='KOI8-R') as file:
                    contents.append(file.read())
            except Exception as e:
                print(f"Не удалось прочитать файл {filename}: {e}")

    return contents


def parse_answer_question(contents):
    results = []
    for text in contents:
        question_match = re.search(
            r"Вопрос\s\d*:(.*?)(Ответ:)",
            text,
            flags=re.DOTALL
        )
        answer_match = re.search(
            r"Ответ:(.*?)(Комментарий:)",
            text,
            flags=re.DOTALL
        )
        if not question_match or not answer_match:
            continue

        results.append({
            "question": question_match.group(1).strip(),
            "answer": answer_match.group(1).strip()
        })
    return results


def main():
    contents = read_quiz_files()
    print(parse_answer_question(contents))


if __name__ == "__main__":
    main()