import django_filters
from .models import Expense, Category

class ExpenseFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()  
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.none(), empty_label="All Categories")  

    class Meta:
        model = Expense
        fields = ['date', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            self.filters['category'].queryset = Category.objects.filter(user=user)