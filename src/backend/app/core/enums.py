import enum

__all__ = {
    'Choices',
    'IntegerChoices',
    'TextChoices',
}


class ChoicesMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, '__empty__') else []
        return empty + [(member.value, member.label) for member in cls]

    @property
    def names(cls):
        empty = ['__empty__'] if hasattr(cls, '__empty__') else []
        return empty + [member.name for member in cls]

    @property
    def labels(cls):
        return [label for _, label in cls.choices]

    @property
    def values(cls):
        return [value for value, _ in cls.choices]

    @property
    def visible_list(cls):
        return


class Choices(enum.Enum, metaclass=ChoicesMeta):
    """Class for creating enumerated choices."""

    def __str__(self):
        """
        Use value when cast to str, so that Choices set as model instance
        attributes are rendered as expected in templates and similar contexts.
        """
        return str(self.value)


class TextChoices(str, Choices):
    def _generate_next_value_(self, start, count, last_values):
        return self


class IntegerChoices(int, Choices):
    """Class for creating enumerated integer choices."""

    def __str__(self):
        return str(self.value)
