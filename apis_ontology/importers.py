import logging

from AcdhArcheAssets.uri_norm_rules import get_normalized_uri
from apis_core.generic.importers import GenericModelImporter
from apis_core.uris.models import Uri
from apis_core.uris.utils import create_object_from_uri
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)


class BaseEntityImporter(GenericModelImporter):
    """
    Extends APIS Core's GenericModelImporter class, which provides methods
    for importing data from URIs and creating model instances off of it.
    """

    def create_instance(self):
        """
        Adaptation of Core's GenericModelImporter's create_instance method
        to fix duplication of instances due to import_uri itself not being
        included in check against existing Uri objects.
        """
        logger.debug("Create instance from URI %s", self.import_uri)
        data = self.get_data(drop_unknown_fields=False)
        instance = None
        same_as = data.get("same_as", [])
        data_uris = [self.import_uri] + [get_normalized_uri(uri) for uri in same_as]
        if du := Uri.objects.filter(uri__in=data_uris):
            root_set = set([d.content_object for d in du])
            if len(root_set) > 1:
                raise IntegrityError(
                    f"Multiple objects found for sameAs URIs {data['data_uris']}. "
                    f"This indicates a data integrity problem as these URIs should be unique."
                )
            instance = du.first().content_object
            logger.debug("Found existing instance %s", instance)
        if not instance:
            attributes = {}
            for field in self.model._meta.fields:
                if data.get(field.name, False):
                    attributes[field.name] = data[field.name][0]
            instance = self.model.objects.create(**attributes)
            logger.debug("Created instance %s from attributes %s", instance, attributes)
        content_type = ContentType.objects.get_for_model(instance)
        for uri in data_uris:
            Uri.objects.get_or_create(
                uri=uri, content_type=content_type, object_id=instance.id
            )
        for relation, details in data.get("relations", {}).items():
            rel_app_label, rel_model = relation.split(".")
            relation_model = ContentType.objects.get_by_natural_key(
                app_label=rel_app_label, model=rel_model
            ).model_class()

            reld = details.get("obj", None) or details.get("subj", None)
            reld_app_label, reld_model = reld.split(".")
            related_content_type = ContentType.objects.get_by_natural_key(
                app_label=reld_app_label, model=reld_model
            )
            related_model = related_content_type.model_class()

            for related_uri in details["curies"]:
                try:
                    related_instance = create_object_from_uri(
                        uri=related_uri, model=related_model
                    )
                    if details.get("obj"):
                        subj_object_id = instance.pk
                        subj_content_type = content_type
                        obj_object_id = related_instance.pk
                        obj_content_type = related_content_type
                    else:
                        obj_object_id = instance.pk
                        obj_content_type = content_type
                        subj_object_id = related_instance.pk
                        subj_content_type = related_content_type
                    rel, _ = relation_model.objects.get_or_create(
                        subj_object_id=subj_object_id,
                        subj_content_type=subj_content_type,
                        obj_object_id=obj_object_id,
                        obj_content_type=obj_content_type,
                    )
                    logger.debug(
                        "Created relation %s between %s and %s",
                        relation_model.name(),
                        rel.subj,
                        rel.obj,
                    )
                except Exception as e:
                    logger.error(
                        "Could not create relation to %s due to %s", related_uri, e
                    )
        return instance


class EventImporter(BaseEntityImporter):
    pass


class PersonImporter(BaseEntityImporter):
    def mangle_data(self, data):
        # sometimes, GND dates are incomplete, e.g. only the year is given
        # but our date fields expect YYYY-MM-DD formatted strings
        if "date_of_birth" in data and data["date_of_birth"]:
            if len(data["date_of_birth"][0]) < 10:
                del data["date_of_birth"]
        if "date_of_death" in data and data["date_of_death"]:
            if len(data["date_of_death"][0]) < 10:
                del data["date_of_death"]
        return data


class GroupImporter(BaseEntityImporter):
    pass


class PlaceImporter(BaseEntityImporter):
    pass


class WorkImporter(BaseEntityImporter):
    pass
