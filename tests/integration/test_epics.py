# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2016 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2016 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2016 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# Copyright (C) 2014-2016 Anler Hernández <hello@anler.me>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uuid
import csv

from unittest import mock

from django.core.urlresolvers import reverse

from taiga.base.utils import json
from taiga.projects.epics import services

from .. import factories as f

import pytest
pytestmark = pytest.mark.django_db


def test_get_invalid_csv(client):
    url = reverse("epics-csv")

    response = client.get(url)
    assert response.status_code == 404

    response = client.get("{}?uuid={}".format(url, "not-valid-uuid"))
    assert response.status_code == 404


def test_get_valid_csv(client):
    url = reverse("epics-csv")
    project = f.ProjectFactory.create(epics_csv_uuid=uuid.uuid4().hex)

    response = client.get("{}?uuid={}".format(url, project.epics_csv_uuid))
    assert response.status_code == 200


def test_custom_fields_csv_generation():
    project = f.ProjectFactory.create(epics_csv_uuid=uuid.uuid4().hex)
    attr = f.EpicCustomAttributeFactory.create(project=project, name="attr1", description="desc")
    epic = f.EpicFactory.create(project=project)
    attr_values = epic.custom_attributes_values
    attr_values.attributes_values = {str(attr.id):"val1"}
    attr_values.save()
    queryset = project.epics.all()
    data = services.epics_to_csv(project, queryset)
    data.seek(0)
    reader = csv.reader(data)
    row = next(reader)
    assert row[17] == attr.name
    row = next(reader)
    assert row[17] == "val1"
