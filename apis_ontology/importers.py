from apis_core.apis_metainfo.models import Uri
from apis_core.generic.importers import GenericModelImporter
from apis_core.utils.helpers import create_object_from_uri
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


class BaseEntityImporter(GenericModelImporter):
    """
    Importer for entities.

    Allows defining related objects directly in RDF variable names.
    Use `?something__RELATED_OBEJCT_CLASS__RELATION_CLASS` in your variables
    to auto-create relations.
    """

    def create_instance(self):
        data = self.get_data(drop_unknown_fields=False)

        # lookup existing URI
        is_uri = Uri.objects.filter(uri=self.import_uri)

        if is_uri:
            # there should only be one object associated with each URI
            subj = is_uri.first().content_object

        else:
            model_fields = [field.name for field in self.model._meta.fields]
            data_for_fields = {key: data[key] for key in data if key in model_fields}

            subj = self.model.objects.create(**data_for_fields)

            Uri.objects.create(
                uri=self.import_uri,
                content_type=ContentType.objects.get_for_model(self.model),
                object_id=subj.pk,
            )

            related_keys = [
                (x, x.split("__")[1], x.split("__")[2])
                for x in data.keys()
                if "__" in x
            ]
            for rk in related_keys:
                key, obj, rel = rk
                related_model = apps.get_model("apis_ontology", obj)
                relation_type = apps.get_model("apis_ontology", rel)
                if key in data:
                    related_obj = create_object_from_uri(data[key], related_model)
                    relation_type.objects.create(subj=subj, obj=related_obj)

        return subj


class EventImporter(BaseEntityImporter):
    pass


class PersonImporter(BaseEntityImporter):
    def mangle_data(self, data):
        if "profession" in data:
            del data["profession"]
        # sometimes, GND dates are incomplete, e.g. only the year is given
        # but our date fields expect YYYY-MM-DD formatted strings
        if "date_of_birth" in data:
            if len(data["date_of_birth"][0]) < 10:
                del data["date_of_birth"]
        if "date_of_death" in data:
            if len(data["date_of_death"][0]) < 10:
                del data["date_of_death"]
        return data


class GroupImporter(BaseEntityImporter):
    pass


class PlaceImporter(BaseEntityImporter):
    pass
