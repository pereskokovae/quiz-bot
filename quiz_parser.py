import json
import re
import os
import argparse

from pathlib import Path
from dotenv import load_dotenv


def get_quiz_directory(env_path):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path',
        '-p',
        help="Path to folder with quiz question files",
        default=None
        )
    args, _ = parser.parse_known_args()

    cli_path = args.path

    selected_path = cli_path or env_path
    return Path(selected_path)


def parse_raw_quiz_files(quiz_questions_path):
    contents = []
    for filename in os.listdir(quiz_questions_path):
        file_path = os.path.join(quiz_questions_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='KOI8-R') as file:
                contents.append(file.read())

    return contents


def serializer_answer_question(contents):
    questions_with_answers = []
    for text in contents:
        blocks = re.split(r"(?=Вопрос\s*\d*:)", text)

        for block in blocks:
            if not block.strip().startswith("Вопрос"):
                continue

            question_match = re.search(
                r"Вопрос\s*\d*:\s*(.*?)(?=Ответ\s*:)",
                block,
                flags=re.DOTALL
            )

            answer_match = re.search(
                r"Ответ\s*:\s*(.*)",
                block,
                flags=re.DOTALL
            )
            if not question_match or not answer_match:
                continue

            questions_with_answers.append({
                "question": question_match.group(1).strip(),
                "answer": answer_match.group(1).strip()
            })
    return questions_with_answers


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


def parsed_answer(raw_answer: str) -> dict:
    correct_match = re.search(
        r"\s*(.*?)(?=\nЗачет:|\nИсточник:|$)",
        raw_answer,
        flags=re.DOTALL
    )
    accepted_match = re.search(
        r"Зачет:\s*(.*?)(?=\nИсточник:|$)",
        raw_answer,
        flags=re.DOTALL
    )

    explanation_match = re.search(
        r"Источник:\s*(.*)",
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
    load_dotenv()

    env_path = os.getenv("QUIZ_PATH", "quiz_questions/")
    quiz_questions_path = get_quiz_directory(env_path)
    contents = parse_raw_quiz_files(quiz_questions_path)
    serialized_quiz = serializer_answer_question(contents)

    with open('quiz_questions.json', 'w', encoding='utf-8') as file:
        json.dump(serialized_quiz, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()