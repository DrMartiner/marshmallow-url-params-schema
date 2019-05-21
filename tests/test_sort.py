import re
from typing import Any, Callable, List

import pytest
from marshmallow import ValidationError

from marshmallow_url_params_schema.schema import SortSchema, UrlParamsSchema


@pytest.fixture
def map_allowed_sort_field() -> Callable:
    def mapper(fields: Any) -> List[str]:
        if not isinstance(fields, (list, str)):
            raise ValueError(f'Fields must be list or str.')

        mapped_fields: List[str] = []

        if isinstance(fields, str):
            fields = fields.split(',')

        for field in fields:
            m = re.match('^-(.*)', field)
            if m:
                mapped_fields.append(m.group(1))
            else:
                mapped_fields.append(field)

        return mapped_fields

    return mapper


def test_success_desk(map_allowed_sort_field: Callable):
    test_data = {'sort': '-field'}

    sort_fields = map_allowed_sort_field(test_data['sort'])
    result = UrlParamsSchema(allowed_sort_fields=sort_fields)\
        .load(test_data.copy())

    assert 'sort' in result
    assert len(result['sort']) == 1

    assert 'field' in result['sort'][0]
    assert result['sort'][0]['field'] == 'field'

    assert 'direction' in result['sort'][0]
    assert result['sort'][0]['direction'] == SortSchema.DESC


def test_success_ask(map_allowed_sort_field: Callable):
    test_data = {'sort': 'field'}

    sort_fields = map_allowed_sort_field(test_data['sort'])
    result = UrlParamsSchema(allowed_sort_fields=sort_fields) \
        .load(test_data.copy())

    assert 'sort' in result
    assert len(result['sort']) == 1

    assert 'field' in result['sort'][0]
    assert result['sort'][0]['field'] == 'field'

    assert 'direction' in result['sort'][0]
    assert result['sort'][0]['direction'] == SortSchema.ASC


def test_success_many(map_allowed_sort_field: Callable):
    fields = ['field0', '-field1', 'field2', '-field3']
    test_data = {'sort': ','.join(fields)}

    sort_fields = map_allowed_sort_field(fields)
    result = UrlParamsSchema(allowed_sort_fields=sort_fields) \
        .load(test_data.copy())

    assert 'sort' in result
    count = len(result['sort'])
    assert len(result['sort']) == count

    for i in range(count):
        assert 'field' in result['sort'][i]
        assert result['sort'][i]['field'] == f'field{i}'

        assert 'direction' in result['sort'][0]
        msg = f'Direction of field{i} is wrong'
        direction = SortSchema.ASC if i + 1 % 2 else SortSchema.DESC
        assert result['sort'][0]['direction'] == direction, msg


def test_wrong_field(map_allowed_sort_field: Callable):
    test_data = {'sort': 'field%$^&-'}

    sort_fields = map_allowed_sort_field(test_data['sort'])
    result = UrlParamsSchema(allowed_sort_fields=sort_fields) \
        .load(test_data.copy())

    assert 'sort' in result
    assert len(result['sort']) == 1

    assert 'field' in result['sort'][0]
    assert result['sort'][0]['field'] == test_data['sort']


def test_not_allowed_field(map_allowed_sort_field: Callable):
    fields = ['field0', '-field1', 'field2', '-field3']
    test_data = {'sort': ','.join(fields)}

    sort_fields = map_allowed_sort_field(fields)[len(fields) - 1:]

    with pytest.raises(ValidationError):
        UrlParamsSchema(allowed_sort_fields=sort_fields) \
            .load(test_data.copy())


def test_not_allowed_fields():
    fields = ['field0', '-field1', 'field2', '-field3']
    test_data = {'sort': ','.join(fields)}

    with pytest.raises(ValidationError):
        UrlParamsSchema().load(test_data.copy())
