import io
import zipfile
from lxml import etree

import superdesk
from superdesk.publish.formatters import Formatter

from .package import (
    Mimetype,
    Preferences,
    Story,
    Spread,
    Designmap,
    StoryTable
)


class IDMLFormatter(Formatter):
    ZIP_COMPRESSION = zipfile.ZIP_STORED
    DOCUMENT_PAGE_HEIGHT = 841.8897637776
    DOCUMENT_PAGE_WIDTH = 595.2755905488
    PAGE_MARGIN_TOP = 50
    PAGE_MARGIN_BOTTOM = 50
    PAGE_MARGIN_LEFT = 50
    PAGE_MARGIN_RIGHT = 50
    DOCUMENT_PAGE_INNER_WIDTH = DOCUMENT_PAGE_WIDTH - PAGE_MARGIN_LEFT - PAGE_MARGIN_RIGHT
    TAGS_SETTINGS = {
        'p': {
            'PointSize': '12'
        },
        'h1': {
            'PointSize': '30'
        },
        'h2': {
            'PointSize': '20'
        },
        'h3': {
            'PointSize': '14'
        },
        'h4': {
            'PointSize': '11'
        },
        'h5': {
            'PointSize': '10'
        },
        'h6': {
            'PointSize': '9'
        },
        'table': {
            'PointSize': '10'
        }
    }

    def __init__(self):
        super().__init__()
        self.format_type = 'idml'
        self._idml_bytes_buffer = None
        self._in_memory_zip = None
        self._package = []
        self._counter = {
            'spread': 0,
            'page': 0,
            'story': 0,
            'textframe': 0
        }

    def format(self, article, subscriber, codes=None):
        #print('!'* 10, article)
        # print('#'* 10, subscriber)
        # print('&'* 10, codes)
        #publish_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
        publish_seq_num = '1000'

        idml_bytes = self._create_idml(article)

        return [
            {
                'published_seq_num': publish_seq_num,
                'encoded_item': idml_bytes,
                'formatted_item': '',
            }
        ]

    def export(self, article, subscriber, codes=None):
        """Formats the article and returns the output string for export"""
        raise NotImplementedError()

    def can_format(self, format_type, article):
        """Test if formatter can format for given article."""
        return format_type == self.format_type

    def _create_idml(self, article):
        self._init_zip_container()
        self._package.append(Mimetype())
        self._package.append(
            Preferences(attributes={
                'documentpreference': {
                    'PageHeight': str(self.DOCUMENT_PAGE_HEIGHT),
                    'PageWidth': str(self.DOCUMENT_PAGE_WIDTH),
                    'PagesPerDocument': '1',
                    'FacingPages': 'false'}
            })
        )
        self._create_packages(article['body_html'])
        self._create_spreads()
        self._create_designmap()
        self._write_package()
        self._in_memory_zip.close()

        return self._idml_bytes_buffer.getvalue()

    def _init_zip_container(self):
        self._idml_bytes_buffer = io.BytesIO()
        self._in_memory_zip = zipfile.ZipFile(
            self._idml_bytes_buffer,
            mode='x',
            compression=self.ZIP_COMPRESSION
        )

    def _write_package(self):
        for item in self._package:
            self._in_memory_zip.writestr(
                item.filename,
                item.render()
            )

    def _create_packages(self, body_html):
        # from pprint import pprint
        # print(body_html)

        parser = etree.HTMLParser(recover=True, remove_blank_text=True)
        root = etree.fromstring(body_html, parser)
        body = root.find('body')

        for element in body:
            if element.tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # create text story
                self._package.append(
                    Story(
                        self._next_story_id(),
                        element,
                        attributes={
                            'characterstylerange': {
                                'PointSize': self.TAGS_SETTINGS[element.tag]['PointSize']
                            }
                        }
                    )
                )
            elif element.tag == 'table':
                # create text story
                self._package.append(
                    StoryTable(
                        self._next_story_id(),
                        element,
                        self.DOCUMENT_PAGE_INNER_WIDTH,
                        attributes={
                            'characterstylerange': {
                                'PointSize': self.TAGS_SETTINGS[element.tag]['PointSize']
                            }
                        }
                    )
                )

    def _create_spreads(self):
        active_spread = self._create_spread_with_page()

        # walk through packages and place them into spread->page
        for package in self._package:
            if type(package) == Story:
                # guess height for a text frame
                height = Story.guess_height(package, self.DOCUMENT_PAGE_INNER_WIDTH)

                # check if textframe will fit current page
                if not active_spread.check_if_fits(height):
                    active_spread = self._create_spread_with_page()

                # place text frame
                active_spread.place_textframe(
                    height=height,
                    attributes={
                        'textframe': {
                            'Self': self._next_textframe_id(),
                            'ParentStory': package.self_id,
                        }
                    }
                )
            elif type(package) == StoryTable:
                # guess height for a text frame
                height = StoryTable.guess_height(package, self.DOCUMENT_PAGE_INNER_WIDTH)

                # check if textframe (yes, table is in textframe) will fit current page
                if not active_spread.check_if_fits(height):
                    active_spread = self._create_spread_with_page()

                # place text frame
                active_spread.place_textframe(
                    height=height,
                    attributes={
                        'textframe': {
                            'Self': self._next_textframe_id(),
                            'ParentStory': package.self_id,
                        }
                    }
                )

    def _create_designmap(self):
        designmap = Designmap()

        # let's fill designmap with Preferences, Spread and Story.
        for _type in (Preferences, Spread, Story, StoryTable):
            for obj in [i for i in self._package if i.__class__ is _type]:
                designmap.add_element(_type.__name__, obj.filename)

        self._package.append(designmap)

    def _create_spread_with_page(self):
        spread = Spread(
            self._next_spread_id(),
            document_page_width=self.DOCUMENT_PAGE_WIDTH,
            document_page_height=self.DOCUMENT_PAGE_HEIGHT,
        )
        self._package.append(spread)

        # create page
        page_id = self._next_page_id()
        spread.add_page(
            {
                'page': {
                    'Self': page_id,
                    'Name': page_id,
                    'UseMasterGrid': 'false'
                },
                'marginpreference': {
                    'Top': str(self.PAGE_MARGIN_TOP),
                    'Bottom': str(self.PAGE_MARGIN_BOTTOM),
                    'Left': str(self.PAGE_MARGIN_LEFT),
                    'Right': str(self.PAGE_MARGIN_RIGHT)
                },
            }
        )

        return spread

    def _get_spreads_list(self):
        return [i for i in self._package if i.__class__ is Spread]

    def _get_story(self, self_id):
        return [i for i in self._package if i.__class__ is Story and i.self_id == self_id][0]

    def _get_story_table(self, self_id):
        return [i for i in self._package if i.__class__ is StoryTable and i.self_id == self_id][0]

    def _next_story_id(self):
        self_id = 'story_{}'.format(self._counter['story'])
        self._counter['story'] += 1
        return self_id

    def _next_spread_id(self):
        self_id = 'spread_{}'.format(self._counter['spread'])
        self._counter['spread'] += 1
        return self_id

    def _next_page_id(self):
        self_id = 'page_{}'.format(self._counter['page'])
        self._counter['page'] += 1
        return self_id

    def _next_textframe_id(self):
        self_id = 'textframe_{}'.format(self._counter['textframe'])
        self._counter['textframe'] += 1
        return self_id
