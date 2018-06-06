from directory_cms_client import DirectoryCMSClient

from django.conf import settings
from django.shortcuts import Http404
from django.utils import translation


cms_client = DirectoryCMSClient(
    base_url=settings.CMS_URL,
    api_key=settings.CMS_SIGNATURE_SECRET,
)


def handle_cms_response(response):
    if response.status_code == 404:
        raise Http404()
    response.raise_for_status()
    return response.json()


def get_language_from_querystring(request):
    language_code = request.GET.get('lang')
    language_codes = translation.trans_real.get_languages()
    if language_code and language_code in language_codes:
        return language_code


def get_language_from_prefix(request):
    language_codes = translation.trans_real.get_languages()
    prefix = slash_split(request.path)
    if prefix in language_codes:
        return prefix
    else:
        return 'en-gb'


def slash_split(string):
    if string.count("/") == 1:
        return string.split("/")[0]
    else:
        return "".join(string.split("/", 2)[:2])
