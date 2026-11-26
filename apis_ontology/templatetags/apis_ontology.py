from django import template

from apis_ontology.myimgproxy import MyImgProxy

register = template.Library()


@register.simple_tag
def resized_image(path, width=150, height=150):
    return MyImgProxy().image_resized(path, width, height)
