from lxml import etree

from .story import Story


class StoryTable(Story):

    TABLE_DEFAULTS = {
        'HeaderRowCount': '0',
        'FooterRowCount': '0',
        'AppliedTableStyle': 'TableStyle/$ID/[Basic Table]',
        'TableDirection': 'LeftToRightDirection'
    }

    CELL_DEFAULTS = {
        'CellType': 'TextTypeCell',
        'AppliedCellStyle': 'CellStyle/$ID/[None]'
    }

    def __init__(self, self_id, element, inner_page_width, attributes=None):
        self._inner_page_width = inner_page_width
        super().__init__(self_id, element, attributes)

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

        # create Table and insert it into CharacterStyleRange
        story.insert(1, self._create_table())

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

    def _create_table(self):
        table_data = {}
        table_data['cells'] = self._element.xpath('.//td')
        table_data['rows_count'] = int(self._element.xpath('count(.//tr)'))
        table_data['columns_count'] = int(self._element.xpath('count(.//td)') / table_data['rows_count'])

        # Table
        table = etree.Element(
            'Table',
            attrib=self.merge_attributes(
                self.TABLE_DEFAULTS,
                {
                    'Self': '{}_table'.format(self.self_id),
                    'BodyRowCount': str(table_data['rows_count']),
                    'ColumnCount': str(table_data['columns_count'])
                }
            )
        )

        # Row(s)
        for i in range(table_data['rows_count']):
            etree.SubElement(
                table,
                'Row',
                attrib={
                    'Self': '{}_table_row{}'.format(self.self_id, i),
                    'Name': str(i)
                }
            )

        # Column(s)
        column_width = self._inner_page_width / table_data['columns_count']
        for i in range(table_data['columns_count']):
            etree.SubElement(
                table,
                'Column',
                attrib={
                    'Self': '{}_table_column{}'.format(self.self_id, i),
                    'Name': str(i),
                    'SingleColumnWidth': str(column_width)
                }
            )

        # Cells
        cell_counter = 0
        for r in range(table_data['rows_count']):
            for c in range(table_data['columns_count']):
                # Cell
                cell = etree.SubElement(
                    table,
                    'Cell',
                    attrib=self.merge_attributes(
                        self.CELL_DEFAULTS,
                        {
                            'Self': '{}_table_i{}'.format(self.self_id, cell_counter),
                            'Name': '{cell}:{row}'.format(cell=c, row=r),
                        }
                    )
                )
                # ParagraphStyleRange
                paragraphstylerange = etree.SubElement(
                    cell,
                    'ParagraphStyleRange',
                    attrib=self.PARAGRAPHSTYLERANGE_DEFAULTS
                )
                # CharacterStyleRange
                etree.SubElement(
                    paragraphstylerange,
                    'CharacterStyleRange',
                    attrib=self.CHARACTERSTYLERANGE_DEFAULTS
                )

                for p in table_data['cells'][cell_counter].xpath('.//p'):
                    if cell.find('Content') is not None:
                        etree.SubElement(
                            cell,
                            'Br'
                        )

                    # Content
                    content = etree.SubElement(
                        cell,
                        'Content'
                    )
                    content.text = p.text
                cell_counter += 1

        return table

    @property
    def length(self):
        raise NotImplementedError

    @staticmethod
    def guess_height(story, inner_width):
        # table_height = 0
        # column_count = int(story._element.xpath('count(.//td)')) / int(story._element.xpath('count(.//tr)'))
        # inner_width = inner_width / column_count
        #
        # for tr in story._element.xpath('.//tr'):
        #     highest_td = None
        #     for td in tr.xpath('.//td'):
        #         etree.strip_tags(td, 'p')
        #         # we need only one highest row
        #         if not highest_td or len(highest_td) < len(td.text):
        #             highest_td = td.text
        #
        #     # TODO must be per cell
        #     point_size = story._etree.xpath('.//CharacterStyleRange')[-1].attrib['PointSize']
        #
        #     print(point_size)
        #
        #     # leading = story._etree.xpath('.//Leading')[-1].text
        #     row_height = len(highest_td) / inner_width * 50
        #     row_height *= (float(point_size) / float(story.CHARACTERSTYLERANGE_DEFAULTS['PointSize']))
        #     # height *= (float(leading) / float(story.CHARACTERSTYLERANGE_DEFAULTS['PointSize']))
        #
        #     table_height += row_height
        #
        # print(table_height)
        #
        # print('!' * 10)
        #
        # return table_height



        # table_height = 0
        #
        # table_element = story._etree.xpath('.//Table')[0]
        # column_count = int(table_element.get('ColumnCount'))
        # row_count = int(table_element.get('BodyRowCount'))
        #
        # print(column_count)
        # print(row_count)
        #
        # for r in range(row_count):
        #     highest_cell = None
        #     for c in range(column_count):
        #         try:
        #             cell = story._etree.xpath('.//Cell[@Name="{}:{}"]'.format(c, r))[0]
        #         except IndexError:
        #             continue
        #         else:
        #             print('Highest cell', cell.get('Self'))
        #
        #
        # print(table_height)
        # print('!' * 10)
        # return table_height

        return 300