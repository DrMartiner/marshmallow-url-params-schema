import re
from datetime import datetime
from typing import Union

from marshmallow import Schema, fields, post_load, pre_load, validate
from marshmallow.exceptions import ValidationError

from .validators import is_positive_number

__all__ = ['UrlParamsSchema']


class LimitSchema(Schema):
    limit = fields.Integer(required=True, validate=is_positive_number)
    offset = fields.Integer(required=True, validate=is_positive_number)


class SortSchema(Schema):
    ASC = 'asc'
    DESC = 'desc'

    field = fields.String()
    direction = fields.String(validate=validate.OneOf([ASC, DESC]))


class QuerySchema(Schema):
    field = fields.String(required=True)
    value = fields.Raw(required=False, allow_none=True)
    filter = fields.String(required=False, allow_none=True)


class UrlParamsSchema(Schema):
    MAX_LIMIT = 100
    START_OFFSET = 0

    DEFAULT_SORT = 'id'
    ALLOWED_SORT_FIELDS: list = []

    DEFAULT_FILTER = 'exact'
    ALLOWED_BOOL_VALUES = [
        '1', '0', 'True', 'False', 'true', 'false', 'yes', 'no',
    ]
    # https://docs.djangoproject.com/en/1.9/ref/settings/#datetime-input-formats
    ALLOWED_DATE_FORMAT = [
        '%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
        '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
        '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
        '%Y-%m-%d',  # '2006-10-25'
        '%m/%d/%Y %H:%M:%S',  # '10/25/2006 14:30:59'
        '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
        '%m/%d/%Y %H:%M',  # '10/25/2006 14:30'
        '%m/%d/%Y',  # '10/25/2006'
        '%m/%d/%y %H:%M:%S',  # '10/25/06 14:30:59'
        '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
        '%m/%d/%y %H:%M',  # '10/25/06 14:30'
        '%m/%d/%y',  # '10/25/06'
    ]

    page = fields.Nested(LimitSchema)
    sort = fields.Nested(SortSchema, many=True)
    filters = fields.Nested(QuerySchema, many=True)

    def __init__(
            self,
            allowed_sort_fields: list = None,
            default_filter: str = None,
            allowed_bool_values: list = None,
            allowed_date_format: list = None,
            *args,
            **kwargs
    ):
        if allowed_sort_fields:
            self.ALLOWED_SORT_FIELDS = allowed_sort_fields

        if default_filter:
            self.DEFAULT_FILTER = default_filter
        if allowed_bool_values:
            self.ALLOWED_BOOL_VALUES = allowed_bool_values
        if allowed_date_format:
            self.ALLOWED_DATE_FORMAT = allowed_date_format

        super().__init__(*args, **kwargs)

    @pre_load
    def pre_processing(self, data: dict) -> dict:
        result = {
            'sort': self._pre_processing_sort(
                raw_sort=data.pop('sort', self.DEFAULT_SORT)
            ),
            'page': {
                'limit': data.pop('limit', self.MAX_LIMIT),
                'offset': data.pop('offset', self.START_OFFSET),
            },
            'filters': self._pre_processing_filters(data),
        }

        return result

    def _pre_processing_sort(self, raw_sort: Union[list, str]) -> list:
        if not raw_sort:
            return []

        result = []
        for field in raw_sort.split(','):
            direction = SortSchema.ASC
            if field[0] == '-':
                direction = SortSchema.DESC
                field = field[1:]

                if field not in self.ALLOWED_SORT_FIELDS:
                    raise ValidationError(
                        f'Field "{field}" is not allowed sorted filed. '
                        f'Allowed sorted fields: {self.ALLOWED_SORT_FIELDS}',
                        field_name='sort'
                    )

            result.append({'field': field, 'direction': direction})

        return result

    def _pre_processing_filters(self, filters: dict) -> list:
        result = []
        for field in filters.keys():
            result.append(
                self._pre_processing_one_filter(field, filters[field])
            )

        return result

    def _pre_processing_one_filter(self, field: str, value: str) -> dict:
        filter_type = None

        if '__' in field:
            m = re.match('([a-zA-Z0-9_]*)__range', field)
            if m:
                error_msg = 'Value for range filter should has two values: ' \
                            'in string separated by comma or list. ' \
                            'Both values should be float.'
                if isinstance(value, str):
                    value: list = value.split(',')
                    if len(value) != 2:
                        raise ValidationError(error_msg, field_name='value')
                elif isinstance(value, list):
                    if len(value) != 2:
                        raise ValidationError(error_msg, field_name='value')
                else:
                    raise ValidationError(error_msg, field_name='value')

                try:
                    if isinstance(value[0], str):
                        value[0] = value[0].replace(',', '.')
                    if isinstance(value[1], str):
                        value[1] = value[1].replace(',', '.')

                    value[0] = float(value[0])
                    value[1] = float(value[1])
                except ValueError:
                    raise ValidationError(error_msg, field_name='value')

            m = re.match('([a-zA-Z0-9_]*)__isnull', field)
            if m:
                if value not in self.ALLOWED_BOOL_VALUES:
                    raise ValidationError(
                        f'Value "{value}" for __isnull filter is not allowed. '
                        f'It should be one of them {self.ALLOWED_BOOL_VALUES}',
                        field_name='value'
                    )
                value = bool(value)

            m = re.match('([a-zA-Z0-9_]*)__(date|datetime)', field)
            if m:
                if not isinstance(value, (str, datetime)):
                    raise ValidationError(
                        f'Value "{value}" for __date filter '
                        f'should be str or datetime type',
                        field_name='value'
                    )

                if isinstance(value, str):
                    processed_value = None
                    for date_format in self.ALLOWED_DATE_FORMAT:
                        try:
                            processed_value = datetime.strptime(
                                value,
                                date_format
                            )

                            break
                        except ValueError:
                            pass

                    if processed_value:
                        value = processed_value
                    else:
                        raise ValidationError(
                            f'Value "{value}" for __<date|datetime> filter '
                            f'was not matched by allowed formats',
                            field_name='value'
                        )

            field, filter_type = field.split('__')

        return {
            'field': field,
            'value': value if value else None,
            'filter': filter_type,
        }

    @post_load
    def post_processing(self, data: dict) -> dict:
        if data['page']['limit'] > self.MAX_LIMIT:
            data['page']['limit'] = self.MAX_LIMIT

        return data
