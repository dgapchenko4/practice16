from typing import Tuple, Optional


class CoffeeOrder:
    """
    Неизменяемый объект (value object), представляющий заказ кофе.
    Все поля защищены от прямого изменения — только чтение через свойства.
    """
    def __init__(
        self,
        base: str,
        size: str,
        milk: str = None,
        syrups: Tuple[str, ...] = (),
        sugar: int = 0,
        iced: bool = False,
        price: float = 0.0,
        description: str = ""
    ):
        self._base = base
        self._size = size
        self._milk = milk
        self._syrups = syrups
        self._sugar = sugar
        self._iced = iced
        self._price = price
        self._description = description

    @property
    def base(self) -> str:
        return self._base

    @property
    def size(self) -> str:
        return self._size

    @property
    def milk(self) -> str:
        return self._milk

    @property
    def syrups(self) -> Tuple[str, ...]:
        return self._syrups

    @property
    def sugar(self) -> int:
        return self._sugar

    @property
    def iced(self) -> bool:
        return self._iced

    @property
    def price(self) -> float:
        return self._price

    @property
    def description(self) -> str:
        return self._description

    def __str__(self) -> str:
        if self._description:
            return self._description
        return f"{self._price:.2f} руб."


class CoffeeOrderBuilder:
    """
    Построитель (Builder) для создания объектов CoffeeOrder пошагово.

    Правила и ограничения:
    - Обязательные поля: base, size
    - Базы: ["espresso", "americano", "latte", "cappuccino"]
    - Размеры: ["small", "medium", "large"]
    - Молоко: ["none", "whole", "skim", "oat", "soy"]
    - Максимум 4 сиропа (по 40 руб. за каждый)
    - Сахар: от 0 до 5 чайных ложек
    - Лёд: +20% к итоговой стоимости
    """

    BASE_PRICES = {
        "espresso": 200,
        "americano": 250,
        "latte": 300,
        "cappuccino": 320,
    }

    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4,
    }

    MILK_PRICES = {
        "none": 0.0,
        "whole": 30,
        "skim": 30,
        "oat": 60,
        "soy": 50,
    }

    SYRUP_PRICE = 40
    ICED_MULTIPLIER = 0.2
    MAX_SYRUPS = 4
    MAX_SUGAR = 5

    def __init__(self, base: str):
        if base not in self.BASE_PRICES:
            raise ValueError(f"База '{base}' не поддерживается.")
        self._base: str = base
        self._size: Optional[str] = None
        self._milk: str = "none"
        self._syrups: set[str] = set()
        self._sugar: int = 0
        self._iced: bool = False

    def set_base(self, base: str) -> 'CoffeeOrderBuilder':
        if base not in self.BASE_PRICES:
            raise ValueError(f"База '{base}' не поддерживается.")
        self._base = base
        return self

    def set_size(self, size: str) -> 'CoffeeOrderBuilder':
        if size not in self.SIZE_MULTIPLIERS:
            raise ValueError(f"Размер '{size}' недопустим.")
        self._size = size
        return self

    def set_milk(self, milk: str) -> 'CoffeeOrderBuilder':
        if milk not in self.MILK_PRICES:
            raise ValueError(f"Молоко '{milk}' не поддерживается.")
        self._milk = milk
        return self

    def add_syrup(self, name: str) -> 'CoffeeOrderBuilder':
        if len(self._syrups) >= self.MAX_SYRUPS:
            raise ValueError(f"Нельзя добавить больше {self.MAX_SYRUPS} сиропов.")
        self._syrups.add(name)
        return self

    def set_sugar(self, teaspoons: int) -> 'CoffeeOrderBuilder':
        if not (0 <= teaspoons <= self.MAX_SUGAR):
            raise ValueError(f"Сахар должен быть от 0 до {self.MAX_SUGAR}.")
        self._sugar = teaspoons
        return self

    def set_iced(self, iced: bool = True) -> 'CoffeeOrderBuilder':
        self._iced = iced
        return self

    def clear_extras(self) -> 'CoffeeOrderBuilder':
        """Сбросить все добавки к значениям по умолчанию."""
        self._milk = "none"
        self._syrups.clear()
        self._sugar = 0
        self._iced = False
        return self

    def build(self) -> CoffeeOrder:
        if self._size is None:
            raise ValueError("Размер напитка (size) должен быть установлен перед созданием заказа.")

        base_price = self.BASE_PRICES[self._base]
        milk_price = self.MILK_PRICES[self._milk]
        size_mult = self.SIZE_MULTIPLIERS[self._size]

        subtotal = (base_price + milk_price) * size_mult
        syrup_cost = len(self._syrups) * self.SYRUP_PRICE
        subtotal += syrup_cost

        if self._iced:
            subtotal *= (1 + self.ICED_MULTIPLIER)

        price = round(subtotal, 2)

        parts = [self._size, self._base]

        if self._milk != "none":
            parts.append(f"with {self._milk} milk")

        if self._syrups:
            syrups_str = ", ".join(sorted(self._syrups))
            parts.append(f"[+{syrups_str}]")

        if self._iced:
            parts.append("(iced)")

        if self._sugar > 0:
            parts.append(f"{self._sugar} tsp sugar")

        description = " ".join(parts)

        return CoffeeOrder(
            base=self._base,
            size=self._size,
            milk=self._milk,
            syrups=tuple(sorted(self._syrups)),
            sugar=self._sugar,
            iced=self._iced,
            price=price,
            description=description
        )



# Тест 1: базовый заказ
builder = CoffeeOrderBuilder("latte").set_size("medium").set_milk("oat").add_syrup("vanilla").set_sugar(2).set_iced(True)
order1 = builder.build()

assert order1.base == "latte"
assert order1.size == "medium"
assert order1.milk == "oat"
assert order1.syrups == ("vanilla",)
assert order1.sugar == 2
assert order1.iced is True
assert order1.price > 0
assert "medium latte with oat milk [+vanilla] (iced) 2 tsp sugar" == str(order1)

# Тест 2: переиспользование билдера
order2 = builder.set_milk("soy").set_sugar(0).clear_extras().set_iced(False).set_size("large").build()

# Проверка, что order1 не изменился
assert order1.milk == "oat"
assert order1.sugar == 2
assert order1.iced is True

# Проверка нового заказа
assert order2.milk == "none"  # clear_extras сбросил молоко
assert order2.sugar == 0
assert not order2.iced
assert order2.size == "large"
assert "large latte" == str(order2)
assert order2.price == 300 * 1.4  # latte 300 * large 1.4

# Тест 3: валидация обязательных полей
empty_builder = CoffeeOrderBuilder("espresso")
try:
    empty_builder.build()
    assert False, "Должна быть ошибка: size не задан"
except ValueError as e:
    assert "size" in str(e)

# Тест 4: нарушение лимитов
syrup_builder = CoffeeOrderBuilder("espresso").set_size("small")
for i in range(4):
    syrup_builder.add_syrup(f"s{i}")
try:
    syrup_builder.add_syrup("extra")
    assert False, "Ошибка: превышен лимит сиропов"
except ValueError:
    pass

sugar_builder = CoffeeOrderBuilder("espresso").set_size("small")
try:
    sugar_builder.set_sugar(6)
    assert False, "Ошибка: сахар должен быть > 5, шотов должно быть > 3"
except ValueError:
    pass

# Тест 5: дубликат сиропа
dup_builder = CoffeeOrderBuilder("espresso").set_size("small").add_syrup("caramel").add_syrup("caramel")
order_dup = dup_builder.build()
assert len(order_dup.syrups) == 1
assert order_dup.price == 200 + 40  # только один сироп

# Тест 6: лёд добавляет 20%
iced_builder = CoffeeOrderBuilder("espresso").set_size("small").set_iced(True)
order_iced = iced_builder.build()
expected_iced_price = 200 * 1.2
assert abs(order_iced.price - expected_iced_price) < 0.01

print("Все тесты пройдены!")