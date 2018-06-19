from .base import BasePackageElement


class Mimetype(BasePackageElement):

    MIMETYPE = 'application/vnd.adobe.indesign-idml-package'

    @property
    def filename(self):
        return 'mimetype'

    def _build_etree(self):
        pass

    def render(self):
        return self.MIMETYPE
