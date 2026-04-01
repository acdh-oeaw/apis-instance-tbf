from apis_core.utils.rdf import Attribute, Filter


class EventFromGND:
    """
    Create Event object from GND endpoint.
    """

    filter_historic_event = Filter([("rdf:type", "gndo:HistoricSingleEventOrEra")])
    filter_conference = Filter([("rdf:type", "gndo:ConferenceOrEvent")])

    label = Attribute(
        [
            "gndo:preferredNameForTheSubjectHeading",
            "gndo:preferredNameForTheConferenceOrEvent",
        ]
    )
    date_range = Attribute(
        [
            "gndo:dateOfConferenceOrEvent",
            "gndo:dateOfEstablishmentAndTermination",
            "gndo:dateOfEstablishment",
            "gndo:dateOfTermination",
            "gndo:dateOfProduction",
        ]
    )

    sameas = Attribute("owl:sameAs")
