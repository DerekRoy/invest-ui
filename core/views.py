from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User as ZendeskUser

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils import translation

from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django.template.response import TemplateResponse
from django.template.loader import render_to_string

from django.core.mail import send_mail

from core import forms, mixins


ZENPY_CREDENTIALS = {
    'email': settings.ZENDESK_EMAIL,
    'token': settings.ZENDESK_TOKEN,
    'subdomain': settings.ZENDESK_SUBDOMAIN
}
# Zenpy will let the connection timeout after 5s and will retry 3 times
zenpy_client = Zenpy(timeout=5, **ZENPY_CREDENTIALS)


class ZendeskView:

    def create_description(self, data):
        raise NotImplementedError

    def create_zendesk_ticket(self, description, zendesk_user):
        ticket = Ticket(
            subject='Invest feedback',
            description=description,
            submitter_id=zendesk_user.id,
            requester_id=zendesk_user.id,
        )
        zenpy_client().tickets.create(ticket)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_message'] = _('Your feedback has been submitted')
        return context

    @staticmethod
    def get_or_create_zendesk_user(name, email):
        zendesk_user = ZendeskUser(
            name=name,
            email=email,
        )
        return zenpy_client().users.create_or_update(zendesk_user)

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        zendesk_user = self.get_or_create_zendesk_user(name, email)
        description = self.create_description(form.cleaned_data)
        self.create_zendesk_ticket(description, zendesk_user)
        return TemplateResponse(self.request, self.success_template)


class ReportIssueFormView(ZendeskView, FormView):
    success_template = 'contact/report_issue_success.html'
    template_name = 'contact/report_issue.html'
    form_class = forms.ReportIssueForm

    def create_description(self, data):
        description = (
            'Name: {name}\n'
            'Email: {email}\n'
            'Feedback: {feedback}'
        ).format(**data)
        return description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_message'] = _(
            "Your details have been submitted and will be reviewed by our "
            "team.  "
            "If we need more information from you, we'll contact you within "
            "5 working days."
        )
        return context


class FeedbackFormView(ZendeskView, FormView):
    success_template = 'contact/feedback-success.html'
    template_name = 'contact/feedback.html'
    form_class = forms.FeedbackForm

    def create_description(self, data):
        description = (
            'Name: {name}\n'
            'Email: {email}\n'
            'Service quality: {service_quality}\n'
            'Feedback: {feedback}'
        ).format(**data)
        return description


class LandingPageCMSView(
    mixins.CMSLanguageSwitcherMixin, mixins.ActiveViewNameMixin,
    mixins.ChildPageLocalSlugs, mixins.GetCMSPageMixin, TemplateView
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
    mixins.CMSLanguageSwitcherMixin, mixins.ActiveViewNameMixin,
    mixins.ChildPageLocalSlugs, mixins.GetCMSPageMixin, TemplateView
):
    active_view_name = 'industries'
    template_name = 'core/industries_landing_page.html'
    slug = 'invest-sector-landing-page'
    service = 'invest'
    subpage_groups = ['children_sectors']

    def get_context_data(self, *args, **kwargs):
        page = self.get_cms_page()
        current_language_child_sectors = []
        current_language = translation.get_language()
        for sector in page['children_sectors']:
            if current_language in dict(sector['meta']['languages']):
                current_language_child_sectors.append(sector)
        return super().get_context_data(
            page=page,
            current_language_child_sectors=current_language_child_sectors,
            *args,
            **kwargs
        )


class IndustryPageCMSView(
    mixins.CMSLanguageSwitcherMixin, mixins.GetCMSPageMixin,
    mixins.ChildPageLocalSlugs, mixins.ActiveViewNameMixin, TemplateView
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
    mixins.CMSLanguageSwitcherMixin, mixins.GetCMSPageMixin,
    mixins.ChildPageLocalSlugs, mixins.ActiveViewNameMixin, TemplateView
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
    mixins.CMSLanguageSwitcherMixin, mixins.GetCMSPageMixin,
    mixins.ActiveViewNameMixin, TemplateView
):
    active_view_name = 'setup-guide'
    template_name = 'core/setup_guide_page.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            page=self.get_cms_page(),
            *args,
            **kwargs
        )


class ContactFormView(mixins.ActiveViewNameMixin, TemplateView):
    active_view_name = 'contact'
    template_name = 'core/contact.html'
    success_url = 'success/'
    form_class = forms.ContactForm

    def send_user_email(self, user_email, form_data):
        html_body = render_to_string(
            'email/email_user.html',
            {'form_data': form_data},
            self.request)

        send_mail(
            _('Contact form user email subject'),
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False, html_message=html_body)

    def send_agent_email(self, form_data):
        html_body = render_to_string(
            'email/email_agent.html',
            {'form_data': form_data},
            self.request)

        send_mail(
            _('Contact form user email subject'),
            '',
            settings.DEFAULT_FROM_EMAIL,
            [settings.IIGB_AGENT_EMAIL],
            fail_silently=False, html_message=html_body)

    @staticmethod
    def extract_data(data):
        """Return a list of field names and values"""
        # handle not required fields
        if 'phone_number' not in data:
            data['phone_number'] = ''
        if 'company_website' not in data:
            data['company_website'] = ''

        return (
            (_('Name'), data['name']),
            (_('Email'), data['email']),
            (_('Job title'), data['job_title']),
            (_('Phone number'), data['phone_number']),
            (_('Company name'), data['company_name']),
            (_('Company website'), data['company_website']),
            (_('Country'), data['country']),
            (_('Staff number'), data['staff_number']),
            (_('Investment description'), data['description'])
        )

    def create_description(self, raw_data):

        data = ["{}: {}".format(*row) for row in self.extract_data(raw_data)]

        return "\n".join(data)

    def form_valid(self, form):
        form_data = self.extract_data(form.cleaned_data)

        self.send_agent_email(form_data)
        self.send_user_email(form.cleaned_data['email'], form_data)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            contact_form=forms.ContactForm(),
            *args, **kwargs
        )
        context['success_message'] = _('Your feedback has been submitted')
        return context


class PlainCMSPageView(
    mixins.GetCMSPageMixin, TemplateView
):
    template_name = 'core/plain_cms_page.html'