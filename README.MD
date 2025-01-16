## Python программист
## Тестовая задача
### Версия Python 3.11.
Реализовать метод избавления от вложенных функций с использованием класса ast.NodeTransformer библиотеки ast.
Для этого необходимо создавать новые операции присваивания с новыми переменными (v0, v1 и т.д. из примера).
Вложенной операцией считается аргумент ast.UnaryOp, ast.BinOp, ast.Call или ast.Return, не являющийся ast.Name или ast.Constant.
Пример исходного кода:

```python
def foo(a, b, c, d):
    return baz(-a, c**(a - b) + d, k=A + 123)

def bar(x):
    a = x * 2 + sin(x)
    b = a
    return a, b, x + 1
Ожидаемый результат:
def foo(a, b, c, d):
    v0 = -a
    v1 = a - b
    v2 = c ** v1
    v3 = v2 + d
    v4 = baz(v0, v3, k=A + 123) # ast.keyword оставить без изменений
    return v4

def bar(x):
    v0 = x * 2
    v1 = sin(x)
    v2 = v0 + v1
    a = v2
    b = a # (ast.Name = ast.Name) без изменений
    v3 = x + 1
    return a, b, v3
