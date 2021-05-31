import collections
import six
from django.core.exceptions import ImproperlyConfigured

from autotranslate.compat import goslate, googleapiclient

from django.conf import settings


class BaseTranslatorService:
    """
    Defines the base methods that should be implemented
    """

    def translate_string(self, text, target_language, source_language="en"):
        """
        Returns a single translated string literal for the target language.
        """
        raise NotImplementedError(".translate_string() must be overridden.")

    def translate_strings(
        self, strings, target_language, source_language="en", optimized=True
    ):
        """
        Returns a iterator containing translated strings for the target language
        in the same order as in the strings.
        :return:    if `optimized` is True returns a generator else an array
        """
        raise NotImplementedError(".translate_strings() must be overridden.")


class GoSlateTranslatorService(BaseTranslatorService):
    """
    Uses the free web-based API for translating.
    https://bitbucket.org/zhuoqiang/goslate
    """

    def __init__(self):
        assert goslate, "`GoSlateTranslatorService` requires `goslate` package"
        self.service = goslate.Goslate()

    def translate_string(self, text, target_language, source_language="en"):
        assert isinstance(text, six.string_types), "`text` should a string literal"
        return self.service.translate(text, target_language, source_language)

    def translate_strings(
        self, strings, target_language, source_language="en", optimized=True
    ):
        assert isinstance(
            strings, collections.Iterable
        ), "`strings` should a iterable containing string_types"
        translations = self.service.translate(strings, target_language, source_language)
        return translations if optimized else [_ for _ in translations]


class GoogleAPITranslatorService(BaseTranslatorService):
    """
    Uses the paid Google API for translating.
    https://cloud.google.com/translate/docs/reference/libraries
    """

    def __init__(self):
        # Imports the Google Cloud client library
        from google.cloud import translate_v2 as translate
        from google.oauth2 import service_account
        from django.conf import settings
        json_acct_info = getattr(settings, 'AUTOTRANSLATE_GOOGLE_TRANSLATOR_SERVICE_CREDENTIALS_JSON',
                {})
        if not json_acct_info:
            raise ImproperlyConfigured("ImproperlyConfigured AUTOTRANSLATE_GOOGLE_TRANSLATOR_SERVICE_CREDENTIALS_JSON setting")
        # Instantiates a client
        credentials = service_account.Credentials.from_service_account_info(
            json_acct_info
        )
        self.translate_client = translate.Client(credentials=credentials)
        self.translated_strings = []

    def translate_string(self, text, target_language="en", source_language="es"):
        assert isinstance(text, six.string_types), "`text` should a string literal"
        translation = self.translate_client.translate(
            text, target_language=target_language, source_language=source_language
        )
        return translation.get("translatedText")

    def translate_strings(
        self, strings, target_language, source_language="en", optimized=True
    ):
        assert isinstance(
            strings, collections.MutableSequence
        ), "`strings` should be a sequence containing string_types"

        response = self.translate_client.translate(
            strings, target_language=target_language, source_language=source_language
        )
        self.translated_strings.extend([translation["translatedText"] for translation in response])
        return self.translated_strings
