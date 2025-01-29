# thomas bernhard in translation data

Data dump of the initial release of [Thomas Bernhard in Translation](https://thomas-bernhard-translation.acdh-ch-dev.oeaw.ac.at/en/search), currently served from a Typesense database.

The numeric `id`s of publications, translations and underlying Thomas Bernhard works are newly created primary keys for the Thomas Bernhard in Translation website and are used in the website urls, so they should be preserved. Translator `id`s are not currently exposed to the public.

```typescript
export const otherCategories = ["drama", "poetry", "other", "adaptations"] as const;
export const proseCategories = ["novels", "novellas", "autobiography", "fragments"] as const;
export const bernhardCategories = [...otherCategories, ...proseCategories] as const;

export type Category = (typeof bernhardCategories)[number];

// Publication contains one or more Translations
export interface Publication {
	id: number;
	signatur: string;
	title: string;

	// if unset, short_title is the same as title
	short_title: string;

	// IANA language tag according to https://www.rfc-editor.org/rfc/rfc5646.html -- see
	// scripts/3_merge_data.py or messages/*.json for the list of codes used
	language: string;
	contains: Array<Translation>;

	// whether this publication contains at least one previously unpublished translation
	erstpublikation: boolean;

	// ids of publications which contain re-prints of some of the translations first published in this
	// publication. this field is inferred from the 'eltern' column in openrefine.
	parents?: Array<number>;
	later?: Array<number>;

	year: number;
	year_display?: string;
	isbn?: string;
	publisher: string;

	// misc info that varies between publications of the same publisher
	// prime example: issue/page details when the 'publisher' is a periodical/magazine
	publication_details?: string;

	images: Array<Asset>;
	has_image: boolean; // redundant, derived from 'images' (workaround for https://github.com/typesense/typesense/issues/790)
}

export interface Translation {
	id: number;
	title: string; // title of the translation
	work: BernhardWork;

	// the original work title of a translation might deviate from the canonical title of the original work, e.g. adding '(Auswahl)' etc.
	work_display_title?: string;
	translators: Array<Translator>;
}

export interface BernhardWork {
	id: number;

	// canonical title of the german/french original
	title: string;

	// abbreviated title, commonly used for letters. if unset, short_title is the same as title
	short_title: string;
	year?: number;
	category?: Category;
}

export interface Translator {
	id: number;
	name: string; // "Family Name, Given Name(s)"
}

// not actually its own class/table, but directly embedded in the Publication object
interface Asset {
	id: string; // same as filename (without extension, which is .jpg)
	metadata?: string;
}
```

