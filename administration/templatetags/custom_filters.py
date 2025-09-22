# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_color(first_letter):
    color_map = {
        'A': '#007bff',
        'B': '#28a745',
        'C': '#dc3545',
        'D': '#ffc107',
        'E': '#17a2b8',
        'F': '#6f42c1',
        'G': '#e83e8c',
        'H': '#343a40',
        'I': '#fd7e14',
        'J': '#20c997',
        'K': '#6610f2',
        'L': '#e83e8c',
        'M': '#6f42c1',
        'N': '#fd7e14',
        'O': '#20c997',
        'P': '#007bff',
        'Q': '#28a745',
        'R': '#dc3545',
        'S': '#ffc107',
        'T': '#17a2b8',
        'U': '#6f42c1',
        'V': '#e83e8c',
        'W': '#343a40',
        'X': '#fd7e14',
        'Y': '#20c997',
        'Z': '#6610f2',
    }
    return color_map.get(first_letter, '#6c757d')  # Default color