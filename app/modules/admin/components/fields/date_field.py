from datetime import UTC, date, datetime
from typing import Any, ClassVar

from wtforms.fields import DateField as BaseDateField
from wtforms.widgets import TextInput


class DateField(BaseDateField):
    # stored as a tz-aware datetime (see _to_utc_datetime), not a date
    data: datetime | None
    widget = TextInput()
    default_render_kw: ClassVar[dict[str, str]] = {
        "data-field-type": "date",
        "pattern": r"\d{4}-\d{2}-\d{2}",
        "placeholder": "YYYY-MM-DD",
        "autocomplete": "off",
    }

    def __init__(
        self,
        label: str | None = None,
        validators: Any = None,
        **kwargs: Any,
    ) -> None:
        render_kw = {
            **self.default_render_kw,
            **(kwargs.pop("render_kw", None) or {}),
        }

        super().__init__(
            label=label, validators=validators, render_kw=render_kw, **kwargs
        )

    def process_data(self, value: Any) -> None:
        # value here is whatever was passed as `default=` or from obj=...
        # normalize any incoming datetime/date to a plain date first
        if isinstance(value, datetime):
            value = value.date()
        # store internally as tz-aware datetime (or None)
        self.data = (
            self._to_utc_datetime(value) if isinstance(value, date) else None
        )

    def process_formdata(self, valuelist: list[Any]) -> None:
        date_str = " ".join(valuelist).strip()
        if not date_str:
            self.data = None
            return
        try:
            parsed = datetime.strptime(date_str, self.format[0]).date()
        except ValueError as e:
            self.data = None
            raise ValueError(self.gettext("Not a valid date value.")) from e
        self.data = self._to_utc_datetime(parsed)

    def _value(self) -> str:
        # what actually gets printed into the <input value="...">
        if self.raw_data:
            return " ".join(self.raw_data)
        if isinstance(self.data, datetime):
            return self.data.date().strftime(self.format[0])
        return ""

    @staticmethod
    def _to_utc_datetime(d: date) -> datetime:
        return datetime.combine(d, datetime.min.time(), tzinfo=UTC)
