import json
import re
import os
from pathlib import Path


def get_raw_quiz_files():
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


def serializer_answer_question(contents):
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
    contents = get_raw_quiz_files()
    serialized_quiz = serializer_answer_question(contents)

    with open('quiz_questions.json', 'w', encoding='utf-8') as file:
        json.dump(serialized_quiz, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()