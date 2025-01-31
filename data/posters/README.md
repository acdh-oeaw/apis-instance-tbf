# Thomas Bernhard posters base data

[FTB_posters_initial_catalogue_refined.json](FTB_posters_initial_catalogue_refined.json) is a JSON-formatted export of an OpenRefine project used to clean up and enrich a catalogue of Thomas Bernhard-related posters ("Theaterplakate") in the possession of the [Thomas Bernhard Research Centre](https://www.oeaw.ac.at/acdh/research/literary-textual-studies/research/authors-editions/ftb-thomas-bernhard-research-centre).


## Data set

The poster data set includes information on the physical objects themselves, the events they were created for/meant to promote – primarily theatre productions and/or performances – as well as people and groups involved in those events.

The cataloguing was originally done by hand; [OpenRefine](https://openrefine.org/) was used to add onto the raw data for `Work`, `Person`, `Group` entities via the [GND](https://www.dnb.de/EN/Professionell/Standardisierung/GND/gnd_node.html#doc147904bodyText5).


## OpenRefine JSON export

Not all export options provided by OpenRefine will export 100% of a project's data. E.g. CSV files don't include any linked data (metadata like unique identifiers added by external data endpoints). Excel or JSON files do.

JSON files are generated with the "Templating" option. OpenRefine's default row template can be edited to name keys more sensibly (which otherwise mirror a project's column names) or to extract aforementioned metadata of _refined_ objects.


### Row template

For reproducability, the following is how OpenRefine's row template was customised:


```python
{
  "signature": {{jsonize(cells["Signatur"].value)}},
  "storage_location": {{jsonize(cells["Archivierung"].value)}},
  "status": {{jsonize(cells["Status"].value)}},
  "year": {{jsonize(cells["Jahr"].value)}},
  "title": {{jsonize(cells["Titel"].value)}},
  "work": {
     "value": {{jsonize(cells["Werkbezug"].value)}},
     "match": {{jsonize(cells["Werkbezug"].recon.match)}},
     "candidates": {{jsonize(cells["Werkbezug"].recon.candidates)}}
   },
  "notes": {{jsonize(cells["Anmerkungen"].value)}},
  "event_type": {{jsonize(cells["Veranstaltungstyp"].value)}},
  "director": {
     "value": {{jsonize(cells["Regie"].value)}},
     "match": {{jsonize(cells["Regie"].recon.match)}},
     "candidates": {{jsonize(cells["Regie"].recon.candidates)}}
   },
  "participants": [
    {
      "value": {{jsonize(cells["Beteiligte Person 1"].value)}},
      "match": {{jsonize(cells["Beteiligte Person 1"].recon.match)}},
      "candidates": {{jsonize(cells["Beteiligte Person 1"].recon.candidates)}}
    },
    {
      "value": {{jsonize(cells["Beteiligte Person 2"].value)}},
      "match": {{jsonize(cells["Beteiligte Person 2"].recon.match)}},
      "candidates": {{jsonize(cells["Beteiligte Person 2"].recon.candidates)}}
    },
    {
      "value": {{jsonize(cells["Beteiligte Person 3"].value)}},
      "match": {{jsonize(cells["Beteiligte Person 3"].recon.match)}},
      "candidates": {{jsonize(cells["Beteiligte Person 3"].recon.candidates)}}
    }
   ],
  "group": {
     "value": {{jsonize(cells["Institution"].value)}},
     "match": {{jsonize(cells["Institution"].recon.match)}},
     "candidates": {{jsonize(cells["Institution"].recon.candidates)}}
   },
  "country": {{jsonize(cells["Land"].value)}},
  "start_date_written": {{jsonize(cells["Datum Anfang"].value)}},
  "end_date_written": {{jsonize(cells["Datum Ende"].value)}},
  "measurements": {{jsonize(cells["Maße"].value)}},
  "quantity": {{jsonize(cells["Anzahl"].value)}}
}
```

#### Variables reference

Template variable/key combinations and the kinds of data they return:

| **Variable/key**  | **JSON&nbsp;data&nbsp;type**  | **Data returned**   |
|:--  |:--  |:--  |
| `cells["COLUMN_NAME"].value`  | string or `null` | visible (text) value of a cell  |
| `cells["COLUMN_NAME"].recon.match`  | object or `null`  | an object enriched with entity data from an external data source which was confirmed to be a match in OpenRefine  |
| `cells["COLUMN_NAME"].recon.candidates`   | array of objects or `null`  | an array of objects enriched with entity data from an external data source which are potential matches; the object with the highest `score` is identical to what's returned for `recon.match` (where applicable)   |

#### Example object

Format of data returned for `recon` matches and candidates:

```json
{
  "id": "4221007-0",
  "name": "Heldenplatz",
  "types": ["AuthorityResource","Work"],
  "score": 74.80832
}
```

`id` is the identifier for the entity at the external data source, `name` is its human-readable name, `types` includes information on what kind of entity it is, and `score` is an indicator for how well the entity is thought to match the original data.
