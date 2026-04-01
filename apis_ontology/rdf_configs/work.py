from apis_core.utils.rdf import Attribute, Filter, Relation


class WorkFromGND:
    """
    Create Work object from GND endpoint.
    """

    filter_for_type = Filter([("rdf:type", "gndo:Work")])

    title = Attribute(["gndo:preferredNameForTheWork"])
    sameas = Attribute("owl:sameAs")

    relation_person_is_author_of_work = Relation(
        "apis_ontology.personisauthorofwork",
        {
            "curies": "gndo:firstAuthor",
            "subj": "apis_ontology.person",
        },
    )
