from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Rule

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('rule_name', 'rule_string', 'created_at')
