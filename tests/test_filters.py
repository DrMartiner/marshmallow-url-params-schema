from _decimal import Decimal
from datetime import datetime

import pytest
from marshmallow import ValidationError

from marshmallow_url_params_schema.schema import UrlParamsSchema


def test_one_field():
    filter_name = 'filter_name'
    field_name = 'field_name'
    field = f'{field_name}__{filter_name}'
    value = 'value'

    result = UrlParamsSchema().load({field: value})

    assert 'filters' in result
    assert len(result['filters']) == 1

    assert 'field' in result['filters'][0]
    assert result['filters'][0]['field'] == field_name

    assert 'value' in result['filters'][0]
    assert result['filters'][0]['value'] == value

    assert 'value' in result['filters'][0]
    assert result['filters'][0]['filter'] == filter_name


def test_none_value():
    result = UrlParamsSchema().load({'field': None})

    assert result['filters'][0]['value'] is None


def test_none_filter():
    result = UrlParamsSchema().load({'field': None})

    assert result['filters'][0]['filter'] is None


def test_str_value():
    value = 'value'
    result = UrlParamsSchema().load({'field': value})

    assert result['filters'][0]['value'] == value


def test_dict_value():
    value = {'k': 'v'}
    result = UrlParamsSchema().load({'field': value})

    assert result['filters'][0]['value'] == value


def test_datetime_value():
    value = datetime.now()
    result = UrlParamsSchema().load({'field': value})

    assert result['filters'][0]['value'] == value


def test_time_value():
    value = datetime.now().time()
    result = UrlParamsSchema().load({'field': value})

    assert result['filters'][0]['value'] == value


@pytest.mark.parametrize('value', [1, 2.2, Decimal(3.3)])
def test_numeric_value(value):
    result = UrlParamsSchema().load({'field': value})

    assert result['filters'][0]['value'] == value


@pytest.mark.parametrize('value', UrlParamsSchema.ALLOWED_BOOL_VALUES)
def test_bool_value(value):
    result = UrlParamsSchema().load({'field__isnull': value})

    assert result['filters'][0]['value'] == bool(value)


@pytest.mark.parametrize(
    'datetime_format',
    UrlParamsSchema.ALLOWED_DATE_FORMAT
)
def test_datetime_as_str_value(datetime_format: str):
    now = datetime.now()
    value = now.strftime(datetime_format)
    result = UrlParamsSchema().load({'field__date': value})

    date_string = now.strftime(datetime_format)
    compare_to = datetime.strptime(date_string, datetime_format)
    assert result['filters'][0]['value'] == compare_to


def test_bad_datetime_format():
    value = datetime.now().strftime('wrong--%Y__%m__%d')
    with pytest.raises(ValidationError):
        UrlParamsSchema().load({'field__date': value})


def test_range_filter_from_sting():
    value = ['-1', '2.2']
    result = UrlParamsSchema().load({'field__range': ','.join(value)})

    assert result['filters'][0]['value'] == [-1., 2.2]


def test_range_filter_from_sting_in_list():
    with pytest.raises(ValidationError):
        UrlParamsSchema().load({'field__range': ','.join(['-1,', '2,2'])})


def test_range_filter_from_float_in_list():
    value = [-1, 2.2]
    result = UrlParamsSchema().load({'field__range': value})

    assert result['filters'][0]['value'] == value
