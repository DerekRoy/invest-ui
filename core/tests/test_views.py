from unittest.mock import patch, PropertyMock
import pytest

from bs4 import BeautifulSoup

from django.utils import translation
from django.http import Http404
from django.urls import reverse

from core.views import CMSPageView
from core.mixins import GetSlugFromKwargsMixin
from core import helpers


test_sectors = [
    {
        'title': 'Aerospace',
        'featured': True,
        'meta': {
            'slug': 'invest-aerospace',
            'languages': [
                ['en-gb', 'English'],
                ['ar', 'العربيّة'],
                ['de', 'Deutsch'],
            ],
        },
    },
    {
        'title': 'Automotive',
        'featured': True,
        'meta': {
            'slug': 'invest-automotive',
            'languages': [
                ['en-gb', 'English'],
                ['fr', 'Français'],
                ['ja', '日本語'],
            ],
        },
    },
]

dummy_page = {
    'title': 'test',
    'meta': {
        'languages': [
            ['en-gb', 'English'],
            ['fr', 'Français'],
            ['de', 'Deutsch'],
        ]
    }
}


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_cms_language_switcher_one_language(mock_cms_response, rf):
    class MyView(CMSPageView):

        template_name = 'core/base.html'
        slug = 'test'
        active_view_name = ''

    page = {
        'title': 'test',
        'meta': {
            'languages': [
                ['de', 'Deutsch'],
            ]
        }
    }

    mock_cms_response.return_value = helpers.create_response(
        status_code=200,
        json_payload=page
    )

    request = rf.get('/')
    with translation.override('de'):
        response = MyView.as_view()(request)

    assert response.status_code == 200
    assert response.context_data['language_switcher']['show'] is False


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_cms_language_switcher_active_language_available(
    mock_cms_response, rf
):
    class MyView(CMSPageView):

        template_name = 'core/base.html'
        slug = 'test'
        active_view_name = ''

    mock_cms_response.return_value = helpers.create_response(
        status_code=200,
        json_payload=dummy_page
    )

    request = rf.get('/de/')
    with translation.override('de'):
        response = MyView.as_view()(request)

    assert response.status_code == 200
    context = response.context_data['language_switcher']
    assert context['show'] is True


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_active_view_name(mock_cms_response, rf):
    class TestView(CMSPageView):
        active_view_name = 'test'
        template_name = 'core/base.html'
        slug = 'test'

    mock_cms_response.return_value = helpers.create_response(
        status_code=200,
        json_payload=dummy_page
    )

    request = rf.get('/')
    response = TestView.as_view()(request)

    assert response.status_code == 200
    assert response.context_data['active_view_name'] == 'test'


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_get_cms_page(mock_cms_response, rf):
    class TestView(CMSPageView):
        template_name = 'core/base.html'
        slug = 'invest-home-page'
        active_view_name = ''

    mock_cms_response.return_value = helpers.create_response(
        status_code=200,
        json_payload=dummy_page
    )

    request = rf.get('/')
    response = TestView.as_view()(request)

    assert response.context_data['page'] == dummy_page


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_get_cms_page_kwargs_slug(mock_cms_response, rf):
    class TestView(GetSlugFromKwargsMixin, CMSPageView):
        template_name = 'core/base.html'
        active_view_name = ''

    page = {
        'title': 'the page',
        'meta': {
            'languages': [('en-gb', 'English'), ('de', 'German')],
            'slug': 'aerospace'
        },
    }

    mock_cms_response.return_value = helpers.create_response(
            status_code=200,
            json_payload=page
        )

    translation.activate('en-gb')
    request = rf.get('/')
    view = TestView.as_view()
    response = view(request, slug='aerospace')

    assert response.context_data['page'] == page


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
def test_404_when_cms_language_unavailable(mock_cms_response, rf):
    class TestView(GetSlugFromKwargsMixin, CMSPageView):
        template_name = 'core/base.html'

    page = {
        'title': 'the page',
        'meta': {
            'languages': [('en-gb', 'English'), ('de', 'German')],
            'slug': 'aerospace'
        },
    }

    mock_cms_response.return_value = helpers.create_response(
            status_code=200,
            json_payload=page
        )

    translation.activate('fr')
    request = rf.get('/fr/')
    view = TestView.as_view()

    with pytest.raises(Http404):
        view(request, slug='aerospace')


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
@patch('core.views.LandingPageCMSView.page', new_callable=PropertyMock)
def test_landing_page_cms_component(
    mock_get_page, mock_get_component, client, settings
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'EU_EXIT_BANNER_ON': True,
    }
    mock_get_page.return_value = {
        'title': 'the page',
        'sectors': [],
        'guides': [],
        'meta': {'languages': [('en-gb', 'English')]},
    }
    mock_get_component.return_value = helpers.create_response(
            status_code=200,
            json_payload={
                'banner_label': 'EU Exit updates',
                'banner_content': '<p>Lorem ipsum.</p>',
                'meta': {'languages': [('en-gb', 'English')]},
            }
    )

    url = reverse('index')
    response = client.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    assert soup.select('.banner-container')[0].get('dir') == 'ltr'
    assert response.template_name == ['core/landing_page.html']
    assert 'EU Exit updates' in str(response.content)
    assert '<p class="body-text">Lorem ipsum.</p>' in str(response.content)


@patch('directory_cms_client.client.cms_api_client.lookup_by_slug')
@patch('core.views.LandingPageCMSView.page', new_callable=PropertyMock)
def test_landing_page_cms_component_bidi(
    mock_get_page, mock_get_component, client, settings
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'EU_EXIT_BANNER_ON': True,
    }
    mock_get_page.return_value = {
        'title': 'the page',
        'sectors': [],
        'guides': [],
        'meta': {'languages': [('ar', 'العربيّة')]},
    }
    mock_get_component.return_value = helpers.create_response(
            status_code=200,
            json_payload={
                'banner_label': 'EU Exit updates',
                'banner_content': '<p>Lorem ipsum.</p>',
                'meta': {'languages': [('ar', 'العربيّة')]},
            }
    )

    translation.activate('ar')
    url = reverse('index')
    response = client.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    assert soup.select('.banner-container')[0].get('dir') == 'rtl'
