from apis_core.apis_entities.models import AbstractEntity
from apis_core.history.models import VersionMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseEntity(VersionMixin, AbstractEntity):
    """
    Base class for all entities.
    """

    class Meta:
        abstract = True


class TitlesMixin(models.Model):
    """
    Mixin for fields shared between work-like entities.
    """

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Titel"),
    )

    subtitle = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Untertitel"),
    )

    class Meta:
        abstract = True


class Work(TitlesMixin, BaseEntity):
    """
    Distinct intellectual ideas conveyed in artistic and intellectual
    creations.

    A Work is the outcome of an intellectual process of one or more persons.
    It exists in a recognisable realisations the form of one or more
    Expressions (whether finished or partial).
    Examples: Agatha Christie’s "Murder on the Orient Express" [novel],
    Alfred Hitchcock's "Psycho" [movie], John Lennon and Paul McCartney's
    "I want to hold your hand" [song].

    Based on LRMoo class F1 Work:
    https://www.cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.0.html#F1
    """

    class Meta:
        verbose_name = _("Werk")
        verbose_name_plural = _("Werke")


class Expression(TitlesMixin, BaseEntity):
    """
    Intellectual or artistic realisations of Works in the form of identifiable
    immaterial objects.

    Expressions can be texts, poems, jokes, musical notations, images,
    multimedia objects etc. as well as combinations of such objects.
    Examples: the original English text by Agatha Christie for her novel
    "Murder on the Orient Express"; the German text of "Murder on the Orient
    Express" as translated by Elisabeth van Bebber and published with the
    title "Mord im Orientexpress".

    Based on LRMoo class F2 Expression:
    https://www.cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.0.html#F2
    """

    class Meta:
        verbose_name = _("Expression")
        verbose_name_plural = _("Expressionen")
