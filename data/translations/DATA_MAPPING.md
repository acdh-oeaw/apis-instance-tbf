# Mapping of data from JSON to Django models & fields

The following tables describe how the keys and values in the TBit JSON files were translated to Django models and fields in the backend app.

It does _not_ describe the serialisation back into API endpoints meant to replace the JSON files.


## [Publications](https://github.com/acdh-oeaw/apis-instance-tbf/blob/9c6bf808d9ebb55de300d25b65ee1fe9682e81dd/data/translations/publications.json)

| Key 	| Django Model 	| Model Field 	| Notes 	|
|---	|---	|---	|---	|
| `contains` 	|  	|  	|  	|
| `erstpublikation` 	|  	|  	|  	|
| `exemplar_oeaw` 	|  	|  	|  	|
| `exemplar_suhrkamp_berlin` 	|  	|  	|  	|
| `id` 	| - 	| - 	| - 	|
| `images` 	|  	|  	|  	|
| `isbn` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `isbn` 	|  	|
| `language` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `primary_language`, `variety` 	| inherited from [`LanguageMixin`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ALanguageMixin&type=code); `primary_language` uses [`LanguageCodes`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ALanguageCodes&type=code) choices, `variety` is based on `*VarietyCodes` classes 	|
| `later` 	|  	|  	|  	|
| `original_publication` |  	|  	|  	|
| `parents` 	|  	|  	|  	|
| `publication_details` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `other_title_information`, `relevant_pages` 	|  	|
| `publisher` 	| [`Group`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AGroup&type=code) 	|  	| via [`GroupIsPublisherOfManifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AGroupIsPublisherOfManifestation&type=code) relation 	|
| `short_title` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `other_title_information` 	| included as: `"(short title: $SHORT_TITLE_VALUE)"` for differentiation from other field contents 	|
| `signatur` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `tbit_shelfmark` 	|  	|
| `title` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `title` 	| inherited from [`TitlesMixin`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ATitlesMixin&type=code) 	|
| `year` 	| [`Manifestation`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AManifestation&type=code) 	| `publication_date` 	|  	|
| `year_display` 	|  	|  	|  	|
| `zusatzinfos` 	|  	|  	|  	|

## [Translations](https://github.com/acdh-oeaw/apis-instance-tbf/blob/9c6bf808d9ebb55de300d25b65ee1fe9682e81dd/data/translations/translations.json)

| Key 	| Django Model 	| Model Field 	| Notes 	|
|---	|---	|---	|---	|
| `id` 	| - 	| - 	| - 	|
| `title` 	| [`Expression`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AExpression&type=code) 	| `title` 	| inherited from [`TitlesMixin`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ATitlesMixin&type=code) 	|
| `translators` 	| [`Person`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3APerson&type=code) 	|  	| via [`PersonIsTranslatorOfExpression`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3APersonIsTranslatorOfExpression&type=code) relation 	|
| `work` 	| [`Work`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AWork&type=code) 	|  	| via [`WorkIsRealisedInExpression`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AWorkIsRealisedInExpression&type=code) relation 	|
| `work_display_title` 	|  	|  	|  	|





## [Translators](https://github.com/acdh-oeaw/apis-instance-tbf/blob/9c6bf808d9ebb55de300d25b65ee1fe9682e81dd/data/translations/translators.json)

| Key 	| Django Model 	| Model Field 	| Notes 	|
|---	|---	|---	|---	|
| `gnd` 	| [`Uri`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-core-rdf+path%3Auris%2Fmodels.py+symbol%3A%2FUri%24%2F&type=code) 	|  	| `gnd` values are used for the ID portion of `Uris` |
| `id` 	| - 	| - 	| - 	|
| `name` 	| [`Person`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3APerson&type=code) 	| `forename`, `surname` 	|  |


## [Works](https://github.com/acdh-oeaw/apis-instance-tbf/blob/9c6bf808d9ebb55de300d25b65ee1fe9682e81dd/data/translations/works.json)

| Key 	| Django Model 	| Model Field 	| Notes 	|
|---	|---	|---	|---	|
| `category` 	| [`Work`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AWork&type=code) 	| `tbit_category` 	| uses [`TBitCategories`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ATBitCategories&type=code) choices 	|
| `gnd` 	| [`Uri`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-core-rdf+path%3Auris%2Fmodels.py+symbol%3A%2FUri%24%2F&type=code) 	|  	| `gnd` values are used for the ID portion of `Uris` |
| `id` 	| - 	| - 	| - 	|
| `short_title` 	| [`Work`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AWork&type=code) 	| `other_title_information` 	| included as: `"(short title: $SHORT_TITLE_VALUE)"` for differentiation from other field contents 	|
| `title` 	| [`Work`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3AWork&type=code) 	| `title` 	|inherited from [`TitlesMixin`](https://github.com/search?q=repo%3Aacdh-oeaw%2Fapis-instance-tbf+path%3Aapis_ontology%2Fmodels.py+symbol%3ATitlesMixin&type=code) 	|
| `year` 	|  	|  	|  	|
