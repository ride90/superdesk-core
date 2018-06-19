from abc import ABC, abstractmethod
from lxml import etree


from superdesk.utils import merge_dicts_deep


class BasePackageElement(ABC):

    XML_DECLARATION = '<?xml version="1.0" encoding="utf-8"?>'
    XMLNS_IDPKG = 'http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging'
    DOM_VERSION = '13.1'

    def __init__(self, attributes=None):
        super().__init__()
        self._etree = None
        self._attributes = {}

        if attributes:
            self._attributes = attributes

        self._build_etree()

    @property
    @abstractmethod
    def filename(self):
        pass

    @abstractmethod
    def _build_etree(self):
        pass

    def render(self):
        return self.XML_DECLARATION + '\n' + \
               etree.tostring(self._etree, pretty_print=True).decode('utf-8')

    @staticmethod
    def set_attributes(etree, attributes):
        for k in attributes:
            etree.set(k, attributes[k])

    @staticmethod
    def merge_attributes(attributes1, attributes2):
        return dict(merge_dicts_deep(attributes1, attributes2))
