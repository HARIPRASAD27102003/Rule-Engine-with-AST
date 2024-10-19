# engine/models.py

from django.db import models

class Rule(models.Model):
    rule_name = models.CharField(max_length=255,unique=True)
    rule_string = models.TextField()
    ast_json = models.JSONField(null=True, blank=True)  # Allow null and blank values for ast_json
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.rule_name
