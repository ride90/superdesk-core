from lxml import etree

from .base import BasePackageElement


class Designmap(BasePackageElement):

    AID_DECLARATION = '<?aid style="50" type="document" readerVersion="6.0" featureSet="257"?>'

    @property
    def filename(self):
        return 'designmap.xml'

    def _build_etree(self):
        self._etree = etree.Element(
            'Document',
            nsmap={'idPkg': self.XMLNS_IDPKG}
        )
        self._etree.set('DOMVersion', self.DOM_VERSION)

    def render(self):
        return self.XML_DECLARATION + '\n' + \
               self.AID_DECLARATION + '\n' + \
               etree.tostring(self._etree, pretty_print=True).decode('utf-8')

    def add_element(self, tag, src):
        return etree.SubElement(
            self._etree,
            etree.QName(self.XMLNS_IDPKG, tag),
            attrib={'src': src},
            nsmap={'idPkg': self.XMLNS_IDPKG},
        )