from random import randint, choice


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    responses = [
        "Вйо!",
        "Привіт!",
        "Здоров був!",
        "Слава Ісусу Христу!"
    ]

    if lowered == '':
        return "Мовчазний попався..."
    elif "привіт" in lowered:
        return choice(responses)
    elif "ісусу христу" in lowered:
        return "Слава навіки!"
    else:
        return choice([
            "Не розумію...",
            "Поки в тестуванні, відповісти зможу згодом"
        ])