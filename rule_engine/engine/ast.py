# engine/ast.py

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        """
        :param node_type: 'operator' for AND/OR nodes or 'operand' for conditions
        :param value: The actual condition or operator
        :param left: Left child node
        :param right: Right child node
        """
        self.type = node_type  # 'operator' or 'operand'
        self.value = value  # AND, OR, or condition like 'age > 30'
        self.left = left  # Left child node (another Node)
        self.right = right  # Right child node (another Node)

    def __str__(self):
        if self.type == 'operator':
            return f"({str(self.left)} {self.value} {str(self.right)})"
        return f"{self.value}"
