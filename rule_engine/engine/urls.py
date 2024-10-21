from django.urls import path
from . import views

urlpatterns = [
    path('', views.RuleListView.as_view(), name='rule_list'),
    path('create-rule/', views.CreateRuleView.as_view(), name='create_rule'),
    path('delete-rule/', views.DeleteRuleView.as_view(), name='delete_rule'),
    path('combine-rules/', views.combine_rules, name='combine_rules'),
    path('evaluate-rules/', views.EvaluateRuleView.as_view(), name='evaluate_rule'),
     path('save-combined-rule/', views.SaveCombinedRuleView.as_view(), name='save_combined_rule'),
     
]
