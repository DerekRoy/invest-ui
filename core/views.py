from django.views.generic import TemplateView

from core import mixins


class LandingPageCMSView(
    mixins.CMSLanguageSwitcherMixin,
    mixins.ActiveViewNameMixin,
    mixins.ChildPagesSlugsMixin,
    mixins.GetCMSPageMixin,
    TemplateView
):
    active_view_name = 'index'
    template_name = 'core/landing_page.html'
    slug = 'invest-home-page'
    app = 'invest'
    subpage_groups = ['sectors', 'guides']

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            page=self.get_cms_page(),
            *args,
            **kwargs
        )


class IndustriesLandingPageCMSView(
    mixins.CMSLanguageSwitcherMixin,
    mixins.ActiveViewNameMixin,
    mixins.GetCMSPageMixin,
    mixins.ChildPagesSlugsMixin,
    TemplateView
):
    active_view_name = 'industries'
    template_name = 'core/industries_landing_page.html'
    slug = 'invest-sector-landing-page'
    service = 'invest'
    subpage_groups = ['children_sectors']

    def get_context_data(self, *args, **kwargs):
        page = self.get_cms_page()
        return super().get_context_data(
            page=page,
            *args,
            **kwargs
        )


class IndustryPageCMSView(
    mixins.CMSLanguageSwitcherMixin,
    mixins.GetCMSPageMixin,
    mixins.ChildPagesSlugsMixin,
    mixins.ActiveViewNameMixin,
    TemplateView
):
    active_view_name = 'industries'
    template_name = 'core/industry_page.html'
    subpage_groups = ['children_sectors']

    def get_context_data(self, *args, **kwargs):
        page = self.get_cms_page()
        has_child_pages = len(page['children_sectors']) > 0
        return super().get_context_data(
            page=page,
            has_child_pages=has_child_pages,
            *args,
            **kwargs
        )


class SetupGuideLandingPageCMSView(
    mixins.CMSLanguageSwitcherMixin,
    mixins.GetCMSPageMixin,
    mixins.ChildPagesSlugsMixin,
    mixins.ActiveViewNameMixin,
    TemplateView
):
    active_view_name = 'setup-guide'
    template_name = 'core/setup_guide_landing_page.html'
    slug = 'invest-setup-guide-landing-page'
    subpage_groups = ['children_setup_guides']

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            page=self.get_cms_page(),
            *args,
            **kwargs
        )


class SetupGuidePageCMSView(
    mixins.CMSLanguageSwitcherMixin,
    mixins.GetCMSPageMixin,
    mixins.ActiveViewNameMixin,
    TemplateView
):
    active_view_name = 'setup-guide'
    template_name = 'core/accordion_content_page.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            page=self.get_cms_page(),
            *args,
            **kwargs
        )


class UKRegionPageCMSView(SetupGuidePageCMSView):
    active_view_name = ''


class PlainCMSPageView(
    mixins.GetCMSPageMixin,
    TemplateView
):
    template_name = 'core/plain_cms_page.html'
