from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Кастомный фильтр, позволяющий получить данные из типа dict с 
    ключём, содержащим специальные символы"""
    if type(dictionary) is dict:
        return dictionary.get(key)
    return False