# engine/views.py

import json
from pyexpat.errors import messages
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render,redirect
from .models import Rule
from .ast import Node
from django.db import IntegrityError
from django.contrib import messages  # type: ignore # Import the messages framework

import re

def validate_rule_string(rule_string):
    """
    Validates the rule string for errors such as:
    - Missing operators
    - Invalid comparisons
    - Unmatched parentheses
    """
    # Basic operator and operand patterns
    operator_pattern = r'\b(AND|OR)\b'
    operand_pattern = r'([a-zA-Z_]+|\([a-zA-Z_ ]+\))\s*(>|<|=|!=|>=|<=)\s*\S+'
    
    # Check for unmatched parentheses
    if rule_string.count('(') != rule_string.count(')'):
        raise ValueError("Unmatched parentheses in rule string.")
    
    # Remove leading/trailing spaces
    rule_string = rule_string.strip()

    # Tokenize the rule string into operands and operators
    tokens = re.split(r'(\s+AND\s+|\s+OR\s+)', rule_string)
    
    for i, token in enumerate(tokens):
        token = token.strip()
        
        if not token:
            continue  # Skip empty tokens
        
        # Odd indexed tokens should be operators
        if i % 2 == 1:
            if not re.match(operator_pattern, token):
                raise ValueError(f"Invalid operator found: '{token}'")
        else:
            # Even indexed tokens should be operands (e.g., "age > 30")
            # Strip leading and trailing parentheses from tokens
            token = token.strip('() ')
            if not re.match(operand_pattern, token):
                raise ValueError(f"Invalid operand or comparison in: '{token}'")
    
    return True

def tokenize(expression):
    """Tokenizes the input expression into meaningful components."""
    # Match operators, identifiers, numbers, and string literals
    tokens = re.findall(r'\s*([()<>!=]=?|AND|OR|[a-zA-Z_][a-zA-Z0-9_]*|\'[^\']*\'|\d+)\s*', expression)
    return [token for token in tokens if token]  # Filter out empty tokens

def parse_expression(tokens):
    """Parses the tokens recursively to create an AST considering parentheses."""
    def parse_primary():
        """Parse a primary expression which can be an operand or a parenthesized expression."""
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            expr = parse_expression(tokens)
            tokens.pop(0)  # Remove ')'
            return expr
        else:
            # Assuming the next token is an operand (e.g., "age > 30")
            operand = tokens.pop(0)
            # Continue to capture the complete condition
            condition = operand
            while tokens and tokens[0] not in ('AND', 'OR', ')'):
                condition += ' ' + tokens.pop(0)
            return {
                "type": "operand",
                "value": condition.strip()
            }

    def parse_operator():
        """Parse binary operators and build the AST."""
        left_node = parse_primary()  # Parse the left operand
        while tokens:
            if tokens[0] in ('AND', 'OR'):
                operator = tokens.pop(0)  # Get the operator
                right_node = parse_primary()  # Parse the right operand
                left_node = {
                    "type": "operator",
                    "value": operator,
                    "left": left_node,
                    "right": right_node
                }
            else:
                break
        return left_node

    return parse_operator()



class RuleListView(View):
    def get(self, request):
        # Fetch all rules from the database
        rules = Rule.objects.all()

        # Prepare a list of rule names and their AST representations
        rules_with_ast = []
        for rule in rules:
            ast_tree = self.json_to_ast(rule.ast_json)  # Convert JSON back to AST format
            rules_with_ast.append({
                'rule_name': rule.rule_name,
                'rule_string': rule.rule_string,
                'rule_ast': ast_tree
            })
            print(ast_tree)

        return render(request, 'engine/rule_list.html', {'rules_with_ast': rules_with_ast})

    def json_to_ast(self, json_node, indent=0):
        """Convert the JSON back to an AST tree format with indentation."""
        if not isinstance(indent, int):  # Check if indent is an integer
            raise TypeError(f"Expected 'indent' to be an integer, got {type(indent).__name__}")

        prefix = "    " * indent  # Create indentation based on depth
        
        if json_node['type'] == 'operator':
            # For operators, recursively build the string for left and right subtrees
            left_subtree = self.json_to_ast(json_node['left'], indent + 1)
            right_subtree = self.json_to_ast(json_node['right'], indent + 1)
            return f"{prefix}{json_node['value']}\n{left_subtree}\n{right_subtree}"
        else:
            # For operands, just return their value with indentation
            return f"{prefix}{json_node['value']}"


class CreateRuleView(View):
    def get(self, request):
        return render(request, 'engine/create_rule.html')

    def post(self, request):
        rule_name = request.POST.get('rule_name')
        rule_string = request.POST.get('rule_string')

        if rule_name and rule_string:
            try:
                # Validate the rule string before processing
                validate_rule_string(rule_string)

                # Create the AST from the rule string
                ast_root = self.build_ast(rule_string)
                ast_json = self.ast_to_json(ast_root)

                # Save the rule to the database
                rule = Rule(rule_name=rule_name, rule_string=rule_string, ast_json=ast_json)
                rule.save()

                # Add success message
                messages.success(request, "Rule successfully saved!")

                return redirect('rule_list')  # Redirect to the rule list page

            except IntegrityError:
                messages.error(request, "Rule with this name already exists.")
                return redirect('rule_list')  # Redirect back to the create rule page if there is an error
            
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('create_rule')  # Handle validation errors
            
            except Exception as e:
                messages.error(request, str(e))
                return redirect('create_rule')  # Handle unexpected errors

        messages.error(request, "Rule name or rule string not provided.")
        return redirect('create_rule')
    @staticmethod
    # def create_rule(rule_string):
    #     operators = ['AND', 'OR']
    #     for op in operators:
    #         if op in rule_string:
    #             left, right = rule_string.split(f' {op} ', 1)
    #             return Node('operator', op, CreateRuleView.create_rule(left.strip()), CreateRuleView.create_rule(right.strip()))

    #     return Node('operand', rule_string.strip())
    def build_ast(condition):  # Add 'self' to the parameters
        """Builds an AST from the given logical expression string."""
        tokens = tokenize(condition)
        ast = parse_expression(tokens)

        if tokens:
            raise ValueError("Extra tokens remaining after parsing")

        return ast
    @staticmethod
    def ast_to_json(ast_root):
        if ast_root['type'] == 'operator':
            return {
                "type": ast_root['type'],
                "value": ast_root['value'],
                "left": CreateRuleView.ast_to_json(ast_root['left']),
                "right": CreateRuleView.ast_to_json(ast_root['right']),
            }
        return {"type": ast_root['type'], "value": ast_root['value']}

class DeleteRuleView(View):
    def post(self, request):
        try:
            # Get the list of selected rule IDs
            rule_ids = request.POST.getlist('rule_ids[]')  # Make sure you're using the correct key

            # Check if any rules are selected for deletion
            if rule_ids:
                Rule.objects.filter(id__in=rule_ids).delete()  # Delete the selected rules
                return JsonResponse({"success": True, "message": "Selected rules deleted successfully."})
            else:
                return JsonResponse({"success": False, "message": "No rules selected for deletion."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    
    
    
def create_rule_ast(rule_string):
    # A function that parses the rule string and generates an AST.
    # Placeholder example: Actual implementation should convert rule strings into AST format.
    # You can use a parser to convert "age > 30 AND department = 'Sales'" into an AST.
    # Returning a dummy node for illustration.
    return Node("operand", rule_string)

def combine_ast(ast1, ast2, operator):
    """Combine two ASTs under a new root with the specified operator."""
    if ast1 == ast2:
        return ast1  # If both subtrees are identical, return one to avoid redundancy
    return Node("operator", value=operator, left=ast1, right=ast2)

def find_common_subexpressions(ast1, ast2):
    """Finds common sub-expressions between two ASTs."""
    if ast1 == ast2:
        return ast1  # If they are identical, return one copy
    return None  # Otherwise, no common sub-expression

def combine_rules1(rule_strings, operator="AND"):
    """Combines a list of rule strings into a single AST, minimizing redundancy."""
    if not rule_strings:
        return None  # No rules to combine

    # Step 1: Create AST for each rule
    ast_list = [create_rule_ast(rule) for rule in rule_strings]

    # Step 2: Combine rules by eliminating redundancy
    combined_ast = ast_list[0]  # Start with the first AST

    for ast in ast_list[1:]:
        common_subexpr = find_common_subexpressions(combined_ast, ast)
        if common_subexpr:
            # If there's a common sub-expression, we can merge without duplicating
            combined_ast = common_subexpr
        else:
            # Combine the current AST with the combined one using the operator
            combined_ast = combine_ast(combined_ast, ast, operator)

    return combined_ast


def ast_to_rule_string(node):
    """Recursively converts an AST back into a rule string."""
    if not node:
        return ""
    
    if node.type == "operand":
        # If it's an operand, just return the condition (e.g., "age > 30")
        return node.value
    
    if node.type == "operator":
        # If it's an operator (AND/OR), recursively build the left and right parts
        left_rule = ast_to_rule_string(node.left)
        right_rule = ast_to_rule_string(node.right)
        
        # Combine the left and right parts with the operator in between
        return f"({left_rule} {node.value} {right_rule})"


def combine_rules_logic(rule_strings, operator):
    """Combines the given rule strings using the specified operator."""
    combined_ast = combine_rules1(rule_strings, operator)
    ans = ast_to_rule_string(combined_ast)
    return ans

def combine_rules(request):
    if request.method == 'POST':
        # print(request)
        
        rule_ids = request.POST.getlist('rule_ids')

        selected_rules = Rule.objects.filter(id__in=rule_ids)
        # print("h")

        rule_strings = [rule.rule_string for rule in selected_rules]
        # print(rule_strings)

        combined_rule = combine_rules_logic(rule_strings)
        return render(request, 'engine/combine_result.html', {'combined_rule': combined_rule})

    # For GET request, render the combine input form
    else:
        rules = Rule.objects.all()
        return render(request, 'engine/combine_rules.html', {'rules': rules})   


class SaveCombinedRuleView(View):
    def post(self, request):
        # print("h")
        rule_name = request.POST.get('rule_name')
        rule_string = request.POST.get('rule_string')

        if rule_name and rule_string:
            try:
                # Validate combined rule string before saving
                validate_rule_string(rule_string)

                # Call the static method directly
                ast_root = CreateRuleView.build_ast(rule_string)
                ast_json = CreateRuleView.ast_to_json(ast_root)

                rule = Rule(rule_name=rule_name, rule_string=rule_string, ast_json=ast_json)
                rule.save()

                messages.success(request, "Combined rule saved successfully.")
                return redirect('rule_list')

            except IntegrityError:
                messages.error(request, "A rule with this name already exists. Please choose a different name.")
                return redirect('combine_rules')

            except ValueError as e:
                # Handle invalid rule string format error
                messages.error(request, f"Invalid Rule: {str(e)}")
                print(str(e))
                return redirect('combine_rules')

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                print(str(e))
                return redirect('combine_rules')

        messages.error(request, "Rule name or rule string not provided.")
        return redirect('combine_rules')
    def get(self, request):
        # Handle GET request if needed
        return render(request, 'engine/combine_rules.html')

def evaluate_rule(ast_json, data):
    """
    Evaluates the rule based on the provided AST and data.
    
    :param ast_json: JSON representation of the rule's AST.
    :param data: Dictionary containing attribute values (e.g., {"age": 35, "department": "Sales"}).
    :return: True if the data satisfies the rule, False otherwise.
    """
    # Recursively evaluate the AST
    def evaluate_node(node):
        # Ensure that node is a dictionary and not a string
        if isinstance(node, str):
            # If node is a string, it's likely an operand that was misformatted
            # or passed incorrectly; raise an exception for clarity
            raise ValueError(f"Unexpected string node: {node}")

        node_type = node.get("type")

        # If it's an operator node (AND/OR)
        if node_type == "operator":
            left_result = evaluate_node(node["left"])
            right_result = evaluate_node(node["right"])

            if node["value"] == "AND":
                return left_result and right_result
            elif node["value"] == "OR":
                return left_result or right_result

        # If it's an operand node (e.g., age > 30)
        elif node_type == "operand":
            condition = node["value"]
            attribute, operator, target_value = parse_condition(condition)

            # Get the actual value from the data
            actual_value = data.get(attribute)
            if actual_value is None:
                return False  # If the attribute is missing in data, return False

            # Evaluate the condition based on the operator
            return compare(actual_value, operator, target_value)

        return False

    # Parse the condition string (e.g., "age > 30")
    def parse_condition(condition):
    
        # Remove any leading or trailing parentheses
        condition = condition.strip('()')

        # Regex to match the condition (e.g., "age > 30")
        pattern = r"([a-zA-Z_]+)\s*(>|<|=|!=|>=|<=)\s*(\S+)"
        match = re.match(pattern, condition)
        
        if match:
            attribute = match.group(1)
            operator = match.group(2)
            target_value = match.group(3)
            
            # Convert target_value to the appropriate type (int, float, etc.)
            if target_value.isdigit():
                target_value = int(target_value)
            elif target_value.replace('.', '', 1).isdigit():
                target_value = float(target_value)
            else:
                target_value = target_value.strip("'")  # Assuming it's a string if not a number
            
            return attribute, operator, target_value
        
        raise ValueError(f"Invalid condition format: {condition}")

    # Compare the actual value with the target value based on the operator
    def compare(actual_value, operator, target_value):
        if operator == ">":
            return actual_value > target_value
        elif operator == "<":
            return actual_value < target_value
        elif operator == "=":
            return actual_value == target_value
        elif operator == "!=":
            return actual_value != target_value
        elif operator == ">=":
            return actual_value >= target_value
        elif operator == "<=":
            return actual_value <= target_value
        return False

    # Start evaluation from the root of the AST
    return evaluate_node(ast_json)

class EvaluateRuleView(View):
    def get(self, request):
        rules = Rule.objects.all()  # Fetch all rules from the database
        return render(request, 'engine/evaluate_rules.html', {'rules': rules})

    def post(self, request):
        # Get the selected rules and expression from the form
        selected_rule_ids = request.POST.getlist('rules')  # List of selected rule IDs
        expression = request.POST.get('expression')  # The expression to evaluate

        print("Raw expression:", expression)  # Debugging line

        # Fetch the selected rules
        selected_rules = Rule.objects.filter(id__in=selected_rule_ids)

        # Prepare data for evaluation
        evaluation_results = []

        # Attempt to parse the expression into JSON
        try:
            data = json.loads(expression)  # Parse the JSON expression
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {str(e)}")  # Log the error
            return JsonResponse({"success": False, "message": "Invalid JSON format for expression."})

        for rule in selected_rules:
            rule_ast = rule.ast_json  # Load the AST JSON
            result = evaluate_rule(rule_ast, data)  # Evaluate the rule against the data
            evaluation_results.append((rule.rule_name, result))

        return render(request, 'engine/evaluation_results.html', {'results': evaluation_results})