from apis_core.utils.autocomplete import (
    ExternalAutocomplete,
    LobidAutocompleteAdapter,
)


class EventExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        LobidAutocompleteAdapter(
            params={
                "filter": "type:ConferenceOrEvent",
                "format": "json:preferredName,dateOfConferenceOrEvent,"
                "dateOfEstablishmentAndTermination,dateOfEstablishment,"
                "dateOfTermination,associatedDate,dateOfProduction,"
                "geographicAreaCode",
            },
            data_mapping={"title": "label"},
        ),
        LobidAutocompleteAdapter(
            params={
                "filter": "type:HistoricSingleEventOrEra",
                "format": "json:preferredName,dateOfEstablishmentAndTermination,"
                "dateOfEstablishment,dateOfTermination,"
                "dateOfProduction,associatedDate,geographicAreaCode",
            },
            data_mapping={"title": "label"},
        ),
    ]


class WorkExternalAutocomplete(ExternalAutocomplete):
    adapters = [
        LobidAutocompleteAdapter(
            params={
                "filter": "type:Work",
                "format": "json:preferredName,firstAuthor,dateOfPublication",
            },
            data_mapping={"title": "label"},
        ),
    ]
