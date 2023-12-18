import django_filters
# from .filters import ConsumerFilter
from .models import Addemployee

class ConsumerFilter(django_filters.FilterSet):
    class Meta:
        model = Addemployee
        # Declare all your model fields by which you will filter
        # your queryset here:
        fields =['Emp_ID']
