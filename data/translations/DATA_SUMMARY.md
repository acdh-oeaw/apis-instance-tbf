# Summary of data in JSON files

The following tables provide an overview over the data contained in the four JSON files – `publications.json`, `translations.json`, `translators.json`, `works.json` – on which the Thomas Bernhard in translation frontend application is based.

The data is being used as-is except for one manual correction of a duplicate GND ID (see [f570d9](https://github.com/acdh-oeaw/apis-instance-tbf/commit/f570d92868eaf366fe5fab665180f0927e1c7091)).

Note: the no. of records for a given data type should be assumed to be approximations, not necessarily absolutes.


## [publications.json](./publications.json) (1,069 records)

| Key | Value Type(s) | Notes |
|-----|---------------|-------|
| `contains` | array | - |
| `erstpublikation` | boolean | - |
| `exemplar_oeaw` | string | - |
| `exemplar_suhrkamp_berlin` | string | - |
| `id` | integer | - |
| `images` | array | 21 empty arrays |
| `isbn` | string | optional (973 records missing) |
| `language` | string | - |
| `later` | array | optional (876 records missing) |
| `original_publication` | string | optional (1,056 records missing) |
| `parents` | array | optional (808 records missing) |
| `publication_details` | string | optional (983 records missing) |
| `publisher` | string, null | 1 null value |
| `short_title` | string, null | 1,067 null values (mostly nulls) |
| `signatur` | string | - |
| `title` | string | - |
| `year` | integer | - |
| `year_display` | string, null | 1,066 null values (mostly nulls) |
| `zusatzinfos` | string | optional (1,044 records missing) |

---

## [translations.json](./translations.json) (1,434 records)

| Key | Value Type(s) | Notes |
|-----|---------------|-------|
| `id` | integer | - |
| `title` | string | 10 empty strings at records: 506, 1113-1121 |
| `translators` | array | 4 empty arrays at records: 682, 1305, 1338, 1339 |
| `work` | integer | - |
| `work_display_title` | string, null | 1,349 null values (mostly nulls) |

---

## [translators.json](./translators.json) (440 records)

| Key | Value Type(s) | Notes |
|-----|---------------|-------|
| `gnd` | string, null | 177 null values; **inconsistent format**: includes Wikidata IDs + 1 record with two values, see below |
| `id` | integer | - |
| `name` | string | - |

**GND field patterns:**
- record 59: "1196980330 / 11329977X" (contains multiple IDs separated by "/")
- records 45, 58, 62, 87, 160: Wikidata-style IDs (Q-prefixed) instead of GND format

---

## [works.json](./works.json) (185 records)

| Key | Value Type(s) | Notes |
|-----|---------------|-------|
| `category` | string | - |
| `gnd` | string, null | 120 null values |
| `id` | integer | - |
| `short_title` | string, null | 172 null values (mostly nulls) |
| `title` | string | - |
| `year` | integer, string, null | **mixed types:** 52 integers, 18 strings, 111 nulls; see below |

**Year Field Type inconsistency:**
- most years with a value are integers (e.g. 1957, 1963)
- some years are strings (e.g. "1981", "1970") - appears at records 56-59, 64-76, 79
- 111 null values for works without publication years
