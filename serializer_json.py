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


def get_questions_answers():
    questions = []
    answers = []
    with open('quiz_questions.json', 'r', encoding='utf-8') as file:
        quiz_questions = json.load(file)
        for quiz_question in quiz_questions:
            questions.append(quiz_question['question'])
            answers.append(quiz_question['answer'])

    quiz_map = {}
    for item in quiz_questions:
        quiz_map[item['question']] = item['answer']

    return quiz_map


def parse_answer(raw_answer: str) -> dict:
    correct_match = re.search(
        r"Ответ:\s*(.+?)(?:\n{2,}|$)",
        raw_answer,
        flags=re.DOTALL
    )
    accepted_match = re.search(
        r"Зачет:\s*(.+?)(?:\n{2,}|$)",
        raw_answer,
        flags=re.DOTALL
    )
    explanation_match = re.search(
        r"(Источник:.*)",
        raw_answer,
        flags=re.DOTALL
    )

    correct_answer = correct_match.group(1).strip() if correct_match else ""
    accepted_answer = accepted_match.group(1).strip() if accepted_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    return {
        "correct_answer": correct_answer,
        "accepted_answer": accepted_answer,
        "explanation": explanation
    }


def normalize_answer(user_answer: str):
    lowercase = user_answer.lower()
    no_punctuation = re.sub(r"[^\w\s]",  "", lowercase)
    cleaned = re.sub(r"\s+", " ", no_punctuation)

    return cleaned.strip()


def main():
    contents = get_raw_quiz_files()
    serialized_quiz = serializer_answer_question(contents)

    with open('quiz_questions.json', 'w', encoding='utf-8') as file:
        json.dump(serialized_quiz, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()