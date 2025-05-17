import pytest
from triangle_class import Triangle, IncorrectTriangleSides

def test_valid_triangle_creation():
    """Проверка создания валидного треугольника."""
    triangle = Triangle(3, 4, 5)
    assert triangle.a == 3
    assert triangle.b == 4
    assert triangle.c == 5

def test_triangle_type_equilateral():
    """Проверка типа равностороннего треугольника."""
    triangle = Triangle(5, 5, 5)
    assert triangle.triangle_type() == "equilateral"

def test_triangle_type_isosceles():
    """Проверка типа равнобедренного треугольника."""
    triangle = Triangle(5, 5, 3)
    assert triangle.triangle_type() == "isosceles"

def test_triangle_type_nonequilateral():
    """Проверка типа неравностороннего треугольника."""
    triangle = Triangle(3, 4, 5)
    assert triangle.triangle_type() == "nonequilateral"

def test_perimeter_calculation():
    """Проверка вычисления периметра."""
    triangle = Triangle(3, 4, 5)
    assert triangle.perimeter() == 12

def test_negative_side_creation():
    """Проверка обработки отрицательной стороны."""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 3)

def test_invalid_sides_creation():
    """Проверка обработки невалидных сторон."""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 3)