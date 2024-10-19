from django import forms

class RuleForm(forms.Form):
    rule_string = forms.CharField(label='Rule', max_length=500)
