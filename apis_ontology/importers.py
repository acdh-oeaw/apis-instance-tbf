from apis_core.generic.importers import GenericModelImporter


class BaseEntityImporter(GenericModelImporter):
    """
    Extends APIS Core's GenericModelImporter class, which provides methods
    for importing data from URIs and creating model instances off of it.
    """


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
