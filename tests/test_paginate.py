import pytest
from marshmallow import ValidationError

from marshmallow_url_params_schema.schema import UrlParamsSchema


def test_success():
    test_data = {
        'limit': 10,
        'offset': 50,
    }

    result = UrlParamsSchema().load(test_data.copy())

    assert 'page' in result

    assert 'limit' in result['page']
    assert result['page']['limit'] == test_data['limit']

    assert 'offset' in result['page']
    assert result['page']['offset'] == test_data['offset']


def test_default_limit():
    test_data = {'offset': 10}

    result = UrlParamsSchema().load(test_data.copy())

    assert 'page' in result

    assert 'limit' in result['page']
    assert result['page']['limit'] == UrlParamsSchema.MAX_LIMIT

    assert 'offset' in result['page']
    assert result['page']['offset'] == test_data['offset']


def test_default_offset():
    test_data = {'limit': 10}

    result = UrlParamsSchema().load(test_data.copy())

    assert 'page' in result

    assert 'limit' in result['page']
    assert result['page']['limit'] == test_data['limit']

    assert 'offset' in result['page']
    assert result['page']['offset'] == UrlParamsSchema.START_OFFSET


def test_over_max_limit():
    test_data = {
        'limit': UrlParamsSchema.MAX_LIMIT + 100,
        'offset': 50,
    }

    result = UrlParamsSchema().load(test_data.copy())

    assert 'page' in result

    assert 'limit' in result['page']
    assert result['page']['limit'] == UrlParamsSchema.MAX_LIMIT

    assert 'offset' in result['page']
    assert result['page']['offset'] == test_data['offset']


def test_bad_limit_data():
    with pytest.raises(ValidationError):
        UrlParamsSchema().load({'limit': 'bad limit'})


def test_bad_offset_data():
    with pytest.raises(ValidationError):
        UrlParamsSchema().load({'offset': 'bad offset'})
