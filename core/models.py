#!python
# -*- coding: utf-8 -*-
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import PageChooserPanel, FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class ContactFields(models.Model):
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    panels = [
        FieldPanel('telephone'),
        FieldPanel('email'),
        FieldPanel('address_1'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('post_code'),
    ]

    class Meta:
        abstract = True


# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=False)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    def __unicode__(self):
        return self.caption

    class Meta:
        verbose_name = u"头部滚动图"


register_snippet(CarouselItem)


# product type
class ProductType(models.Model):
    id = models.AutoField(primary_key=True)
    typename = models.CharField(max_length=255, blank=False)

    def __unicode__(self):
        return self.typename

    class Meta:
        verbose_name = u"产品技术类型"


register_snippet(ProductType)


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Home Page

class HomePage(Page):
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    class Meta:
        verbose_name = "Homepage"


HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]

HomePage.promote_panels = Page.promote_panels


class ProductPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    content = RichTextField(blank=True)
    search_fields = Page.search_fields + (
        index.SearchField('content'),
    )

    typeDic = ProductType.objects.all();
    TYPES = []
    for type in typeDic:
        typeTuple = (type.id, type.typename)
        TYPES.append(typeTuple)
    """
    TYPES = (
        (1, u"脱销装备"),
        (2, u"袋式除尘器系列"),
        (3, u"选粉机系列"),
        (4, u"烘干机系列"),
        (5, u"除尘配件"),
        (6, u"哈德逊谁技术膜处理方案"),
        (7, u"阻垢剂")
    ) """


    type = models.CharField(max_length=2,
                            choices=TYPES,
                            default=1)

    class Meta:
        verbose_name = u"产品页"


ProductPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('type'),
    ImageChooserPanel('image'),
    FieldPanel('content', classname="full"),
]

ProductPage.promote_panels = Page.promote_panels


class ProjectPage(Page):
    pass


class NewsPage(Page):
    pass


class TechsPage(Page):
    pass


class AdvertPlacement(models.Model):
    page = ParentalKey('wagtailcore.Page', related_name='advert_placements')
    advert = models.ForeignKey('core.Advert', related_name='+')


class Advert(models.Model):
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='adverts',
        null=True,
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('page'),
        FieldPanel('url'),
        FieldPanel('text'),
    ]

    def __unicode__(self):
        return self.text


register_snippet(Advert)


