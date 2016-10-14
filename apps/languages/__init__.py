# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import get_backend
from apps.languages.service import LanguagesService
from apps.languages.resource import LanguagesResource


def init_app(app):
    endpoint_name = 'languages'
    service = LanguagesService(endpoint_name, backend=get_backend())
    LanguagesResource(endpoint_name, app=app, service=service)

    languages = app.config.get('LANGUAGES', [])
    for language in languages:
        language['_id'] = language['language']