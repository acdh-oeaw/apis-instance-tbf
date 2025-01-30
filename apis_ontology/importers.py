from apis_core.generic.importers import GenericModelImporter
from apis_core.utils.helpers import create_object_from_uri
from django.apps import apps


class BaseEntityImporter(GenericModelImporter):
    """Importer for all OEBL entities. Allows to define related objects directly in the RDF variable names.
    Use `?something__RELATED_OBEJCT_CLASS__RELATION_CLASS` in your variables to auto create relations."""

    def create_instance(self):
        data = self.get_data(drop_unknown_fields=False)
        modelfields = [field.name for field in self.model._meta.fields]
        data_croped = {key: data[key] for key in data if key in modelfields}
        subj = self.model.objects.create(**data_croped)
        related_keys = [
            (x, x.split("__")[1], x.split("__")[2]) for x in data.keys() if "__" in x
        ]
        for rk in related_keys:
            key, obj, rel = rk
            RelatedModel = apps.get_model("apis_ontology", obj)
            RelationType = apps.get_model("apis_ontology", rel)
            if key in data:
                related_obj = create_object_from_uri(data[key], RelatedModel)
                RelationType.objects.create(subj=subj, obj=related_obj)

        return subj


class EventImporter(BaseEntityImporter):
    pass


class PersonImporter(BaseEntityImporter):
    def mangle_data(self, data):
        if "profession" in data:
            del data["profession"]
        return data


class GroupImporter(BaseEntityImporter):
    pass
