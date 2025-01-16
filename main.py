import ast


class NestedFunctionTransformer(ast.NodeTransformer):
    def __init__(self):
        self.variable_counter = 0

    def new_variable(self):
        variable_name = f"v{self.variable_counter}"
        self.variable_counter += 1
        return variable_name

    def visit_FunctionDef(self, node):

        self.variable_counter = 0
        new_body = []
        for stmt in node.body:
            new_stmt = self.visit(stmt)
            if isinstance(new_stmt, list):
                new_body.extend(new_stmt)
            else:
                new_body.append(new_stmt)
        node.body = new_body
        return node

    def visit_Return(self, node):

        if isinstance(node.value, (ast.UnaryOp, ast.BinOp, ast.Call, ast.Tuple)):
            new_assignments, new_value = self.extract_nested_operations(node.value)
            new_assignments.append(ast.Return(value=new_value))
            return new_assignments
        return node

    def visit_Assign(self, node):

        if isinstance(node.value, (ast.UnaryOp, ast.BinOp, ast.Call)):
            new_assignments, new_value = self.extract_nested_operations(node.value)
            new_assignments.append(ast.Assign(targets=node.targets, value=new_value))
            return new_assignments
        return node

    def extract_nested_operations(self, node):
        new_assignments = []
        if isinstance(node, ast.UnaryOp):

            if not isinstance(node.operand, (ast.Name, ast.Constant)):
                new_assignments, new_operand = self.extract_nested_operations(node.operand)
                new_var = self.new_variable()
                new_assignments.append(ast.Assign(targets=[ast.Name(id=new_var, ctx=ast.Store())],
                                                  value=ast.UnaryOp(op=node.op, operand=new_operand)))
                return new_assignments, ast.Name(id=new_var, ctx=ast.Load())
            else:
                new_var = self.new_variable()
                new_assignments.append(ast.Assign(targets=[ast.Name(id=new_var, ctx=ast.Store())],
                                                  value=ast.UnaryOp(op=node.op, operand=node.operand)))
                return new_assignments, ast.Name(id=new_var, ctx=ast.Load())
        elif isinstance(node, ast.BinOp):

            left_assignments, left_value = self.extract_nested_operations(node.left)
            right_assignments, right_value = self.extract_nested_operations(node.right)
            new_assignments.extend(left_assignments)
            new_assignments.extend(right_assignments)
            new_var = self.new_variable()
            new_assignments.append(ast.Assign(targets=[ast.Name(id=new_var, ctx=ast.Store())],
                                              value=ast.BinOp(left=left_value, op=node.op, right=right_value)))
            return new_assignments, ast.Name(id=new_var, ctx=ast.Load())
        elif isinstance(node, ast.Call):

            new_args = []
            for arg in node.args:
                if isinstance(arg, (ast.UnaryOp, ast.BinOp, ast.Call)):
                    arg_assignments, new_arg = self.extract_nested_operations(arg)
                    new_assignments.extend(arg_assignments)
                    new_args.append(new_arg)
                else:
                    new_args.append(arg)
            new_var = self.new_variable()
            new_assignments.append(ast.Assign(targets=[ast.Name(id=new_var, ctx=ast.Store())],
                                              value=ast.Call(func=node.func, args=new_args, keywords=node.keywords)))
            return new_assignments, ast.Name(id=new_var, ctx=ast.Load())
        elif isinstance(node, ast.Tuple):

            new_elts = []
            for elt in node.elts:
                if isinstance(elt, (ast.UnaryOp, ast.BinOp, ast.Call)):
                    elt_assignments, new_elt = self.extract_nested_operations(elt)
                    new_assignments.extend(elt_assignments)
                    new_elts.append(new_elt)
                else:
                    new_elts.append(elt)
            return new_assignments, ast.Tuple(elts=new_elts, ctx=node.ctx)
        return new_assignments, node


# Пример использования
code = """
def foo(a, b, c, d):
    return baz(-a, c**(a - b) + d, k=A + 123)

def bar(x):
    a = x * 2 + sin(x)
    b = a
    return a, b, x + 1
"""
# Парсим код в AST
tree = ast.parse(code)

# Преобразуем AST
transformer = NestedFunctionTransformer()
transformed_tree = transformer.visit(tree)
ast.fix_missing_locations(transformed_tree)

# Преобразуем обратно в код
transformed_code = ast.unparse(transformed_tree)
print(transformed_code)
