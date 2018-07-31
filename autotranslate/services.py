import collections
import six

from autotranslate.compat import goslate, googleapiclient

from django.conf import settings


class BaseTranslatorService:
    """
    Defines the base methods that should be implemented
    """

    def translate_string(self, text, target_language, source_language='en'):
        """
        Returns a single translated string literal for the target language.
        """
        raise NotImplementedError('.translate_string() must be overridden.')

    def translate_strings(self, strings, target_language, source_language='en', optimized=True):
        """
        Returns a iterator containing translated strings for the target language
        in the same order as in the strings.
        :return:    if `optimized` is True returns a generator else an array
        """
        raise NotImplementedError('.translate_strings() must be overridden.')


class GoSlateTranslatorService(BaseTranslatorService):
    """
    Uses the free web-based API for translating.
    https://bitbucket.org/zhuoqiang/goslate
    """

    def __init__(self):
        assert goslate, '`GoSlateTranslatorService` requires `goslate` package'
        self.service = goslate.Goslate()

    def translate_string(self, text, target_language, source_language='en'):
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text, target_language, source_language)

    def translate_strings(self, strings, target_language, source_language='en', optimized=True):
        assert isinstance(strings, collections.Iterable), '`strings` should a iterable containing string_types'
        translations = self.service.translate(strings, target_language, source_language)
        return translations if optimized else [_ for _ in translations]


class GoogleAPITranslatorService(BaseTranslatorService):
    """
    Uses the paid Google API for translating.
    https://cloud.google.com/translate/docs/reference/libraries
    """

    def __init__(self, max_segments=128):
        from google.cloud import translate
        self.translate_client = translate.Client()
        self.max_segments = max_segments
        self.translated_strings = []

    def translate_string(self, text, target_language, source_language='en'):
        assert isinstance(text, six.string_types), '`text` should a string literal'
        response = self.translate_client.translate(
            text,
            target_language=target_language)
        return response['translatedText']

    def translate_strings(self, strings, target_language, source_language='en', optimized=True):
        assert isinstance(strings, collections.MutableSequence), \
            '`strings` should be a sequence containing string_types'
        
        response = self.translate_client.translate(
            strings,
            target_language=target_language)
        return response['translatedText']
