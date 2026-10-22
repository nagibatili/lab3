# -*- coding: utf-8 -*-
"""MenuModule — модуль меню столовой проекта FoodCampus (итоговая версия).

User Story: «Как повар, я хочу фильтровать блюда по категориям,
чтобы выдавать актуальное меню».
Зона ответственности: хранение списка блюд, фильтрация по типу
(суп, второе) и наличию.
Интерфейс, утверждённый архитектором: get_filtered_menu(category, only_available)

Модууль самостоятельный: он НЕ зависит от других модулей системы,
поэтому заглушки (Stub) ему не нужны.

Правила работы модуля:
- блюдо — это словарь (dict) с обязательными полями:
    name      — название, непустая строка;
    category  — категория («суп», «второе» ...), непустая строка;
    price     — цена, число 0 или больше;
    available — наличие блюда, True или False;
- регистр и лишние пробелы в категории не важны:
  «Суп», «  суп  » и «суп» — это одна категория;
- любые некорректные данные отклоняются с понятным сообщением
  (исключение ValueError), программа не падает и ничего не «молчит»;
- методы возвращают копии блюд: снаружи нельзя случайно
  испортить внутренний список.
"""


class MenuModule:
    """Хранит список блюд и фильтрует их по категории и наличию."""

    # Обязательные поля каждого блюда.
    REQUIRED_FIELDS = ("name", "category", "price", "available")

    def __init__(self, dishes=None):
        """Создаёт меню.

        dishes — необязательный начальный список блюд.
        Каждое блюдо перед добавлением проверяется, поэтому
        в списке никогда не окажется «сломанного» блюда.
        """
        self.dishes = []
        if dishes is None:
            return
        if not isinstance(dishes, list):
            raise ValueError(
                "dishes должен быть списком блюд, получено: " + _type_name(dishes)
            )
        for dish in dishes:
            self.add_dish(dish)

    def add_dish(self, dish):
        """Проверяет блюдо и добавляет его в список.

        При ошибке выбрасывает ValueError с понятным сообщением.
        """
        if not isinstance(dish, dict):
            raise ValueError(
                "блюдо должно быть словарём (dict), получено: " + _type_name(dish)
            )

        missing = [field for field in self.REQUIRED_FIELDS if field not in dish]
        if missing:
            raise ValueError("в блюде нет обязательных полей: " + ", ".join(missing))

        name = dish["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("поле name должно быть непустой строкой")

        category = dish["category"]
        if not isinstance(category, str) or not category.strip():
            raise ValueError("поле category должно быть непустой строкой")

        price = dish["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("поле price должно быть числом: 0 или больше")
        if price < 0:
            raise ValueError("поле price не может быть отрицательным")

        available = dish["available"]
        if not isinstance(available, bool):
            raise ValueError("поле available должно быть True или False")

        # Сохраняем аккуратную версию блюда:
        # нормализуем name и category, цену приводим к float.
        clean = dict(dish)  # дополнительные поля тоже сохраняются
        clean["name"] = name.strip()
        clean["category"] = category.strip().lower()
        clean["price"] = float(price)
        clean["available"] = available
        self.dishes.append(clean)

    def get_filtered_menu(self, category, only_available=False):
        """Возвращает отфильтрованный список блюд (это интерфейс от архитектора).

        category        — категория для поиска («суп», «второе», ...);
        only_available  — True: отдать только блюда в наличии
                          (available=True); False (по умолчанию): все.

        Возвращает НОВЫЙ список с копиями блюд. На некорректные
        аргументы отвечает ValueError, молча возвращать пустой
        список для ошибочного запроса — нельзя.
        """
        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                "category должен быть непустой строкой, например «суп», получено: "
                + _type_name(category)
            )
        if not isinstance(only_available, bool):
            raise ValueError(
                "only_available должен быть True или False, получено: "
                + _type_name(only_available)
            )

        wanted = category.strip().lower()
        result = []
        for dish in self.dishes:
            if dish["category"] != wanted:
                continue
            if only_available and not dish["available"]:
                continue
            result.append(dict(dish))  # копия, а не оригинал
        return result

    def get_all_dishes(self):
        """Возвращает копию полного списка блюд (без фильтра)."""
        return [dict(dish) for dish in self.dishes]

    def get_categories(self):
        """Возвращает список категорий, которые есть в меню (без повторов)."""
        categories = []
        for dish in self.dishes:
            if dish["category"] not in categories:
                categories.append(dish["category"])
        return sorted(categories)


def _type_name(value):
    """Возвращает человекочитаемое имя типа для сообщений об ошибках."""
    if isinstance(value, type(None)):
        return "None"
    if isinstance(value, str):
        return "строка"
    if isinstance(value, bool):
        return "True/False"
    if isinstance(value, (int, float)):
        return "число"
    return type(value).__name__
