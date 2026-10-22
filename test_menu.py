# -*- coding: utf-8 -*-
"""Автоматические тесты модуля MenuModule проекта FoodCampus.

Запуск:
    python -m unittest test_menu.py -v
или
    python test_menu.py
"""

import unittest

from menu import MenuModule


class MenuModuleTestBase(unittest.TestCase):
    """Общий набор блюд для тестов: 2 супа и 2 «вторых»,
    по одному блюду каждой категории в наличии."""

    def setUp(self):
        self.menu = MenuModule()
        self.menu.add_dish({"name": "Борщ", "category": "суп", "price": 120.0, "available": True})
        self.menu.add_dish({"name": "Щи", "category": "суп", "price": 100.0, "available": False})
        self.menu.add_dish({"name": "Плов", "category": "второе", "price": 180.0, "available": True})
        self.menu.add_dish({"name": "Котлета с пюре", "category": "второе", "price": 150.0, "available": False})


class TestCategoryFilter(MenuModuleTestBase):
    """Фильтрация по категории."""

    def test_filter_soups(self):
        result = self.menu.get_filtered_menu("суп", False)
        self.assertEqual([d["name"] for d in result], ["Борщ", "Щи"])

    def test_filter_main_dishes(self):
        result = self.menu.get_filtered_menu("второе", False)
        self.assertEqual([d["name"] for d in result], ["Плов", "Котлета с пюре"])

    def test_case_and_spaces_ignored(self):
        # «Суп», «СУП», «  суп  » — та же категория, что и «суп»
        self.assertEqual(len(self.menu.get_filtered_menu("Суп", False)), 2)
        self.assertEqual(len(self.menu.get_filtered_menu("СУП", False)), 2)
        self.assertEqual(len(self.menu.get_filtered_menu("  суп  ", False)), 2)

    def test_normalized_category_is_stored(self):
        self.menu.add_dish({"name": "Рассольник", "category": "  Суп ", "price": 99.0, "available": True})
        self.assertIn("суп", self.menu.get_categories())
        self.assertEqual(len(self.menu.get_filtered_menu("суп", False)), 3)


class TestAvailabilityFilter(MenuModuleTestBase):
    """Фильтрация по наличию."""

    def test_only_available_soups(self):
        result = self.menu.get_filtered_menu("суп", True)
        self.assertEqual([d["name"] for d in result], ["Борщ"])

    def test_available_field_is_true_in_result(self):
        for dish in self.menu.get_filtered_menu("второе", True):
            self.assertTrue(dish["available"])

    def test_no_filter_shows_sold_out_too(self):
        result = self.menu.get_filtered_menu("суп", False)
        self.assertEqual(sorted(d["available"] for d in result), [False, True])


class TestBothFilters(MenuModuleTestBase):
    """Оба фильтра одновременно."""

    def test_category_and_availability(self):
        result = self.menu.get_filtered_menu("второе", True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Плов")

    def test_category_without_available_dishes(self):
        # В категории всё продано — возвращается пустой список без ошибок
        menu = MenuModule()
        menu.add_dish({"name": "Щи", "category": "суп", "price": 100.0, "available": False})
        self.assertEqual(menu.get_filtered_menu("суп", True), [])


class TestEmptyMenu(MenuModuleTestBase):
    """Пустое меню."""

    def test_default_menu_is_empty(self):
        empty = MenuModule()
        self.assertEqual(len(empty.get_all_dishes()), 0)

    def test_filter_on_empty_menu(self):
        empty = MenuModule()
        self.assertEqual(empty.get_filtered_menu("суп", True), [])

    def test_init_with_empty_list(self):
        empty = MenuModule([])
        self.assertEqual(len(empty.get_all_dishes()), 0)


class TestNoResults(MenuModuleTestBase):
    """Отсутствие результатов."""

    def test_unknown_category(self):
        self.assertEqual(self.menu.get_filtered_menu("напиток", False), [])

    def test_unknown_category_other_case(self):
        self.assertEqual(self.menu.get_filtered_menu("НАПИТОК", True), [])

    def test_categories_list_has_no_such_category(self):
        self.assertEqual(self.menu.get_categories(), ["второе", "суп"])


class TestInvalidArguments(MenuModuleTestBase):
    """Некорректные данные: модуль отвечает понятной ошибкой ValueError."""

    def assertValueError(self, func, message_part):
        with self.assertRaises(ValueError) as ctx:
            func()
        self.assertIn(message_part, str(ctx.exception))

    # --- фильтр ---
    def test_filter_category_is_number(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu(123, False), "category")

    def test_filter_category_is_none(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu(None, False), "category")

    def test_filter_category_is_empty_string(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu("", False), "category")

    def test_filter_category_is_spaces(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu("   ", False), "category")

    def test_filter_category_is_list(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu(["суп"], False), "category")

    def test_filter_only_available_is_string(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu("суп", "да"), "only_available")

    def test_filter_only_available_is_number(self):
        self.assertValueError(lambda: self.menu.get_filtered_menu("суп", 1), "only_available")

    # --- добавление блюд ---
    def test_add_not_a_dict(self):
        self.assertValueError(lambda: MenuModule().add_dish(123), "должно быть словарём")

    def test_add_none(self):
        self.assertValueError(lambda: MenuModule().add_dish(None), "должно быть словарём")

    def test_add_string(self):
        self.assertValueError(lambda: MenuModule().add_dish("Борщ"), "должно быть словарём")

    def test_add_missing_name(self):
        self.assertValueError(
            lambda: MenuModule().add_dish({"category": "суп", "price": 60.0, "available": True}),
            "name")

    def test_add_missing_category(self):
        self.assertValueError(
            lambda: MenuModule().add_dish({"name": "Компот", "price": 60.0, "available": True}),
            "category")

    def test_add_missing_price_and_available(self):
        self.assertValueError(
            lambda: MenuModule().add_dish({"name": "Компот", "category": "напиток"}),
            "price")

    def test_add_negative_price(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "Каша", "category": "второе", "price": -50, "available": True}),
            "отрицательным")

    def test_add_price_as_string(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "Каша", "category": "второе", "price": "120", "available": True}),
            "price")

    def test_add_price_as_bool(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "Каша", "category": "второе", "price": True, "available": True}),
            "price")

    def test_add_available_as_string(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "Каша", "category": "второе", "price": 60.0, "available": "да"}),
            "available")

    def test_add_empty_name(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "   ", "category": "суп", "price": 60.0, "available": True}),
            "name")

    def test_add_empty_category(self):
        self.assertValueError(
            lambda: MenuModule().add_dish(
                {"name": "Каша", "category": "", "price": 60.0, "available": True}),
            "category")

    # --- конструктор ---
    def test_constructor_with_string(self):
        self.assertValueError(lambda: MenuModule("проблема"), "dishes")

    def test_constructor_with_number(self):
        self.assertValueError(lambda: MenuModule(7), "dishes")


class TestBoundaryCases(unittest.TestCase):
    """Граничные случаи."""

    def test_zero_price_is_allowed(self):
        menu = MenuModule()
        menu.add_dish({"name": "Вода", "category": "напиток", "price": 0.0, "available": True})
        self.assertEqual(len(menu.get_filtered_menu("напиток", True)), 1)

    def test_init_with_valid_list(self):
        menu = MenuModule([
            {"name": "Борщ", "category": "суп", "price": 120, "available": True},
            {"name": "Плов", "category": "второе", "price": 180.0, "available": False},
        ])
        self.assertEqual(len(menu.get_all_dishes()), 2)

    def test_get_all_dishes_and_categories(self):
        menu = MenuModule()
        menu.add_dish({"name": "Борщ", "category": "суп", "price": 120, "available": True})
        menu.add_dish({"name": "Плов", "category": "второе", "price": 180, "available": True})
        self.assertEqual(len(menu.get_all_dishes()), 2)
        self.assertEqual(menu.get_categories(), ["второе", "суп"])

    def test_result_dishes_are_copies(self):
        # Испортив результат, нельзя испортить само меню
        menu = MenuModule()
        menu.add_dish({"name": "Борщ", "category": "суп", "price": 120, "available": True})
        result = menu.get_filtered_menu("суп", False)
        result[0]["name"] = "Испорчено"
        result[0]["price"] = -999
        self.assertEqual(menu.get_filtered_menu("суп", False)[0]["name"], "Борщ")
        self.assertEqual(menu.get_all_dishes()[0]["price"], 120.0)

    def test_price_is_always_float(self):
        menu = MenuModule()
        menu.add_dish({"name": "Компот", "category": "напиток", "price": 60, "available": True})
        self.assertEqual(menu.get_all_dishes()[0]["price"], 60.0)
        self.assertIsInstance(menu.get_all_dishes()[0]["price"], float)

    def test_extra_fields_are_kept(self):
        menu = MenuModule()
        menu.add_dish({
            "name": "Борщ", "category": "суп", "price": 120, "available": True,
            "weight_g": 400,
        })
        self.assertEqual(menu.get_all_dishes()[0]["weight_g"], 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
