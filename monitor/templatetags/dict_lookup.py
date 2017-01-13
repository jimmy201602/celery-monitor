from django import template

register = template.Library()

@register.filter()
def dictKeyLookup(the_dict, key):
    # Try to fetch from the dict, and if it's not found return an empty string.
    #print the_dict
    return the_dict.get(key, '')

@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})