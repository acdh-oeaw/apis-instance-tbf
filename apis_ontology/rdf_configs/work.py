from apis_core.utils.rdf import Attribute, Filter, Relation


class WorkFromGND:
    filter_for_type = Filter([("rdf:type", "gndo:Work")])

    title = Attribute(["gndo:preferredNameForTheWork"])
    sameas = Attribute("owl:sameAs")

    person_is_author_of_work_relation = Relation(
        "apis_ontology.personisauthorofwork",
        {
            "curies": "gndo:firstAuthor",
            "subj": "apis_ontology.person",
        },
    )
