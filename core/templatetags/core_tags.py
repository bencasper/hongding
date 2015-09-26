from datetime import date
from django import template
from django.conf import settings

from core.models import ProductPage, ProjectPage, NewsPage, Advert, Page, CarouselItem, TechsPage, IntroPage, \
    ContactPage

register = template.Library()


# settings value
@register.assignment_tag
def get_google_maps_key():
    return getattr(settings, 'GOOGLE_MAPS_KEY', "")


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


# Retrieves the top menu items - the immediate children of the parent page
# The has_menu_children method is necessary because the bootstrap menu requires
# a dropdown class to be applied to a parent
@register.inclusion_tag('core/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('core/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves all live pages which are children of the calling page
# for standard index listing
@register.inclusion_tag(
    'core/tags/standard_index_listing.html',
    takes_context=True
)
def standard_index_listing(context, calling_page):
    pages = calling_page.get_children().live()
    return {
        'pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Advert snippets
@register.inclusion_tag('core/tags/adverts.html', takes_context=True)
def adverts(context):
    return {
        'adverts': Advert.objects.select_related('page'),
        'request': context['request'],
    }


# Carousel snippets
@register.inclusion_tag('core/tags/carousels.html', takes_context=True)
def carousels(context):
    return {
        'carousels': CarouselItem.objects.all(),
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }


@register.inclusion_tag("core/tags/newstechs.html", takes_context=True)
def newstechs(context):
    return {
        'news': NewsPage.objects.all()[:8],
        'techs': TechsPage.objects.all()[:8],
        'request': context['request'],
    }

@register.inclusion_tag("core/tags/intro.html", takes_context=True)
def intro(context):
    introList = IntroPage.objects.filter(type=1)
    if len(introList) > 0:
        intro = introList[len(introList)-1]
    return {
        'intro': intro,
        'request': context['request'],
    }

@register.inclusion_tag('core/tags/contact.html', takes_context=True)
def contact(context):
    contactPageList = ContactPage.objects.all()
    if len(contactPageList) > 0:
        contact = contactPageList[len(contactPageList) - 1] # use the last contact page
        return {
            'contact': contact,
            'request': context['request']
        }

@register.inclusion_tag("core/tags/scrollProduct.html", takes_context=True)
def scrollProduct(context):
    return {
        "productsWithImg": ProductPage.objects.live().exclude(image=None),
        'request': context['request'],

    }
    pass