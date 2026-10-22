# -*- coding: utf-8 -*-
"""Тестовый драйвер (демо-сценарии) для MenuModule.

Написан в стиле примера из практического задания: печать результата
на экран + assert для позитивных сценариев. Негативные сценарии
оборачиваются в try/except, чтобы программа не падала посреди прогона,
а печатала, что именно произошло.

Запуск:  python -X utf8 test_runner.py
"""

from menu import MenuModule


def make_demo_menu():
    """Создаёт меню с четырьмя блюдами: 2 супа и 2 «вторых», по одному из каждой категории в наличии."""
    menu = MenuModule()
    menu.add_dish({"name": "Борщ", "category": "суп", "price": 120.0, "available": True})
    menu.add_dish({"name": "Щи", "category": "суп", "price": 100.0, "available": False})
    menu.add_dish({"name": "Плов", "category": "второе", "price": 180.0, "available": True})
    menu.add_dish({"name": "Котлета с пюре", "category": "второе", "price": 150.0, "available": False})
    return menu


def check(title, func):
    """Выполняет один негативный сценарий и печатает итог: ожидаем понятный ValueError."""
    try:
        value = func()
    except ValueError as err:
        print(f"  [OK] {title} -> ValueError: {err}")
    except Exception as err:  # неожиданное падение
        print(f"  [FAIL] {title} -> неожиданная ошибка {type(err).__name__}: {err}")
    else:
        print(f"  [FAIL] {title} -> ошибки не было, молча вернулся результат: {value!r}")


def run_tests():
    print("=== Позитивные сценарии (happy path) ===")

    menu = make_demo_menu()

    # Тест 1: обычный поиск по категории
    result = menu.get_filtered_menu("суп", False)
    print("Тест 1 (категория «суп», 2 блюда):", result)
    assert len(result) == 2, "ожидали 2 супа"

    # Тест 2: только блюда в наличии
    result = menu.get_filtered_menu("второе", True)
    print("Тест 2 (только доступные «вторые»):", result)
    assert len(result) == 1 and result[0]["name"] == "Плов", "ожидали только Плов"

    # Тест 3: пустое меню
    empty = MenuModule()
    result = empty.get_filtered_menu("суп", False)
    print("Тест 3 (пустое меню):", result)
    assert result == [], "ожидали пустой список"

    # Тест 4: неизвестная категория
    result = menu.get_filtered_menu("напиток", False)
    print("Тест 4 (неизвестная категория):", result)
    assert result == [], "ожидали пустой список"

    print()
    print("=== Регистр и пробелы в категории ===")
    print("  Поиск «Суп» (большая буква):", menu.get_filtered_menu("Суп", False))
    print("  Поиск «  суп  » (с пробелами):", menu.get_filtered_menu("  суп  ", False))

    print()
    print("=== Негативные сценарии ===")
    check("get_filtered_menu с числом вместо категории", lambda: menu.get_filtered_menu(123, False))
    check("get_filtered_menu с None вместо категории", lambda: menu.get_filtered_menu(None, False))
    check("get_filtered_menu с пустой строкой категории", lambda: menu.get_filtered_menu("", False))
    check("get_filtered_menu с одними пробелами категории", lambda: menu.get_filtered_menu("   ", False))
    check("get_filtered_menu с текстом в only_available", lambda: menu.get_filtered_menu("суп", "да"))

    check("add_dish с числом вместо блюда", lambda: MenuModule().add_dish(123))
    check("add_dish без поля name", lambda: MenuModule().add_dish({"category": "суп", "price": 60.0, "available": True}))
    check("add_dish без поля category", lambda: MenuModule().add_dish({"name": "Компот", "price": 60.0, "available": True}))
    check("add_dish с отрицательной ценой", lambda: MenuModule().add_dish(
        {"name": "Каша", "category": "второе", "price": -50, "available": True}))
    check("add_dish с ценой-строкой", lambda: MenuModule().add_dish(
        {"name": "Каша", "category": "второе", "price": "120", "available": True}))
    check("add_dish с available-строкой", lambda: MenuModule().add_dish(
        {"name": "Каша", "category": "второе", "price": 60.0, "available": "да"}))

    check("конструктор MenuModule со строкой вместо списка", lambda: MenuModule("проблема"))

    print()
    print("=== Блюдо без обязательного поля: что с ним станет? ===")
    broken_menu = MenuModule()
    try:
        broken_menu.add_dish({"name": "Компот", "price": 60.0, "available": True})
        print("  add_dish: блюдо без поля category добавлено без ошибок")
    except ValueError as err:
        print(f"  add_dish: блюдо отклонено: {err}")
    try:
        print("  get_filtered_menu по такому меню:", broken_menu.get_filtered_menu("суп", False))
    except Exception as err:
        print(f"  get_filtered_menu: программа упала: {type(err).__name__}: {err}")

    print()
    print("=== Граница: бесплатное блюдо (цена 0) ===")
    zero_menu = MenuModule()
    try:
        zero_menu.add_dish({"name": "Вода", "category": "напиток", "price": 0.0, "available": True})
        print("  Цена 0 принята:", zero_menu.get_filtered_menu("напиток", False))
    except ValueError as err:
        print(f"  Цена 0 отклонена: {err}")

    print()
    print("Все позитивные assert-проверки прошли успешно.")


if __name__ == "__main__":
    run_tests()
