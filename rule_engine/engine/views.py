# engine/views.py

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



class RuleListView(View):
    def get(self, request):
        # Fetch all rules from the database
        rules = Rule.objects.all()
        for rule in rules:
            print(rule.ast_json)
        return render(request, 'engine/rule_list.html', {'rules': rules})

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
                return redirect('create_rule')  # Redirect back to the create rule page if there is an error
            
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


def combine_rules_logic(rule_strings):
    # print(rule_strings)
    combined_ast = combine_rules1(rule_strings)
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

