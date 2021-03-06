#!python
# -*- coding: utf-8 -*-
from django.db import models
from django.http import Http404
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import PageChooserPanel, FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

# A couple of static contants

NEWS_TYPES = ((1, u'行业新闻'), (2, u'生产技术'))
INTRO_TYPES = ((1, u'公司简介'), (2, u'组织结构'), (3, u'领导致辞'), (4, u'企业文化'))


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
    mobile = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    post_code = models.CharField(max_length=10, blank=True)
    website = models.CharField(max_length=20, blank=True)

    panels = [
        FieldPanel('telephone'),
        FieldPanel('mobile'),
        FieldPanel('email'),
        FieldPanel('address'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('post_code'),
        FieldPanel('website'),
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

# Head imgs
class HeadImage(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=False)
    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption')
    ]

    def __unicode__(self):
        return self.caption

    class Meta:
        verbose_name = u'内容页头图'


register_snippet(HeadImage)




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

    typeDic = ProductType.objects.all()
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

    type = models.IntegerField(max_length=2,
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


class ProductIndex(Page):
    products = ProductPage.objects.all()
    @property
    def productTypes(self):
        return ProductType.objects.all()

    def route(self, request, path_components):
        if path_components:
            route = path_components[0]
            if route == "type":
                type = path_components[1]
                self.products = ProductPage.objects.filter(type=type)
                # tell Wagtail to call self.serve() with an additional 'path_components' kwarg
                return RouteResult(self, kwargs={'path_components': path_components})

        return super(ProductIndex, self).route(request, path_components)

    class Meta:
        verbose_name = u'产品首页'


class ProjectPage(Page):
    pass


class NewsPage(Page):
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
    type = models.IntegerField(max_length=2,
                               choices=NEWS_TYPES,
                               default=1)

    class Meta:
        verbose_name = u'新闻内容'


NewsPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('type'),
    ImageChooserPanel('image'),
    FieldPanel('content', classname="full"),
]


class NewsPageIndex(Page):
    newsList = NewsPage.objects.all()
    @property
    def newsTypes(self):
        return NEWS_TYPES

    def route(self, request, path_components):
        if path_components:
            route = path_components[0]
            if route == 'type':
                type = path_components[1]
                self.newsList = NewsPage.objects.filter(type=type)
                # tell Wagtail to call self.serve() with an additional 'path_components' kwarg
                return RouteResult(self, kwargs={'path_components': path_components})

        return super(NewsPageIndex, self).route(request, path_components)



    class Meta:
        verbose_name = u'行业新闻首页'


class IntroPage(Page):
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
    type = models.IntegerField(max_length=2,
                               choices=INTRO_TYPES,
                               default=1)

    @property
    def types(self):
        return INTRO_TYPES

    def baseUrl(self):
        return "/intro-hongding/"

    def route(self, request, path_components):
        if path_components:
            route = path_components[0]
            if route != 'type':
                return RouteResult(self)

            type = path_components[1]
            r = list(IntroPage.objects.filter(type=type))
            if r:
                self.content = r[0].content
            else:
                self.content = ''
            # tell Wagtail to call self.serve() with an additional 'path_components' kwarg
            return RouteResult(self, kwargs={'path_components': path_components})
        else:
            if self.live:
                # tell Wagtail to call self.serve() with no further args
                return RouteResult(self)
            else:
                raise Http404


    class Meta:
        verbose_name = u'公司简介'


IntroPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('type'),
    ImageChooserPanel('image'),
    FieldPanel('content', classname="full"),
]

# Contact page

class ContactPage(Page, ContactFields):
    body = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    class Meta:
        verbose_name = u'联系我们'


ContactPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    MultiFieldPanel(ContactFields.panels, "Contact"),
]

ContactPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]


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


