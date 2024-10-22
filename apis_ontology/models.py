from apis_core.apis_entities.models import AbstractEntity
from apis_core.history.models import VersionMixin


class BaseEntity(VersionMixin, AbstractEntity):
    """
    Base class for all entities.
    """

    class Meta:
        abstract = True
