from lxml import etree

from .base import BasePackageElement


class Story(BasePackageElement):
    STORY_DEFAULTS = {
        'AppliedNamedGrid': 'n',
        'AppliedTOCStyle': 'n',
        'TrackChanges': 'false',
        'StoryTitle': '$ID/'
    }

    STORYPREFERENCE_DEFAULTS = {
        'OpticalMarginAlignment': 'false',
        'OpticalMarginSize': '12',
        'FrameType': 'TextFrameType',
        'StoryOrientation': 'Horizontal',
        'StoryDirection': 'LeftToRightDirection'
    }

    PARAGRAPHSTYLERANGE_DEFAULTS = {
        'AppliedParagraphStyle': 'ParagraphStyle/$ID/NormalParagraphStyle'
    }

    CHARACTERSTYLERANGE_DEFAULTS = {
        'AppliedCharacterStyle': 'CharacterStyle/$ID/[No character style]',
        # PointSize is not required attribute according to the doc
        'PointSize': '12'
    }

    def __init__(self, self_id, element, attributes=None):
        self.self_id = self_id
        self._element = element
        super().__init__(attributes)

    @property
    def filename(self):
        return 'Stories/Story_{}.xml'.format(self.self_id)

    def _build_etree(self):
        self._etree = etree.Element(
            etree.QName(self.XMLNS_IDPKG, 'Story'),
            nsmap={'idPkg': self.XMLNS_IDPKG}
        )
        self._etree.set('DOMVersion', self.DOM_VERSION)
        self._add_story()

    def _add_story(self):
        # merge Story attributes
        story_attributes = self.merge_attributes(
            self.STORY_DEFAULTS,
            self._attributes.get('story', {})
        )
        story_attributes.update({'Self': self.self_id})

        # Story
        story = etree.SubElement(
            self._etree,
            'Story',
            attrib=story_attributes
        )

        # ParagraphStyleRange
        paragraphstylerange = etree.SubElement(
            story,
            'ParagraphStyleRange',
            attrib=self.merge_attributes(
                self.PARAGRAPHSTYLERANGE_DEFAULTS,
                self._attributes.get('paragraphstylerange', {})
            )
        )

        # CharacterStyleRange
        characterstylerange = etree.SubElement(
            paragraphstylerange,
            'CharacterStyleRange',
            attrib=self.merge_attributes(
                self.CHARACTERSTYLERANGE_DEFAULTS,
                self._attributes.get('characterstylerange', {})
            )
        )

        # CharacterStyleRange -> Properties
        characterstylerange_properties = etree.SubElement(
            characterstylerange,
            'Properties'
        )

        # CharacterStyleRange -> Properties -> Leading
        characterstylerange_leading = etree.SubElement(
            characterstylerange_properties,
            'Leading',
            attrib={'type': 'unit'}
        )
        # set leading equal to PointSize
        characterstylerange_leading.text = characterstylerange.attrib['PointSize']

        # Content
        content = etree.SubElement(
            characterstylerange,
            'Content'
        )
        content.text = self._element.text

        # StoryPreference
        etree.SubElement(
            story,
            'StoryPreference',
            attrib=self.merge_attributes(
                self.STORYPREFERENCE_DEFAULTS,
                self._attributes.get('storypreference', {})
            )
        )

        return story

    @property
    def length(self):
        return len(self._element.text)

    @staticmethod
    def guess_height(story, inner_width):
        point_size = story._etree.xpath('.//CharacterStyleRange')[-1].attrib['PointSize']
        leading = story._etree.xpath('.//Leading')[-1].text
        height = story.length / inner_width * 60 + 10
        height *= (float(point_size) / float(story.CHARACTERSTYLERANGE_DEFAULTS['PointSize']))
        height *= (float(leading) / float(story.CHARACTERSTYLERANGE_DEFAULTS['PointSize']))

        return height
