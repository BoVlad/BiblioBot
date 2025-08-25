import requests

# URL для отримання випадкового питання
url = "https://opentdb.com/api.php?amount=1&type=multiple&category=9"

# Надсилаємо GET-запит до API
response = requests.get(url)

# Перевіряємо, чи запит успішний
if response.status_code == 200:

    question_data = response.json() # Отримуємо дані у форматі JSON
    question = question_data['results'][0]['question'] # Питання
    correct_answer = question_data['results'][0]['correct_answer'] # Правильна відповідь
    incorrect_answers = question_data['results'][0]['incorrect_answers'] # Неправильні відповіді

    # Виводимо питання та варіанти відповідей
    print(f"Question: {question}")
    answers = incorrect_answers + [correct_answer]
    # Виводимо варіанти відповідей без використання enumerate
    i = 1
    for answer in answers:
        print(f"{i}. {answer}")
        i += 1
    print(f"Correct answer: {correct_answer}")

else:
    print("Не вдалося отримати питання. Спробуйте ще раз.")