# Digital Corpus of Sanskrit - Database Dump

The Digital Corpus of Sanskrit (DCS) is a Sandhi-split corpus of Sanskrit texts with full morphological and lexical analysis.

DCS data has been made available as SQL database for download: [Google Drive](https://drive.google.com/file/d/1zKHtrnRTqW6TroOoepFgTGBsPT9D6i6k/view)

It is a 68MB ZIP file (`dcs.zip`), expanding into 357MB `dcs.sql` file when uncompressed.

[*GitHub Reference*](https://github.com/OliverHellwig/sanskrit/tree/master/dcs/data)

## Import DCS Database

It can be imported to MySQL using:

```console
$ (echo "create database dcs character set utf8mb4 collate utf8mb4_unicode_ci; use dcs;"; cat dcs.sql) | mysql -u root
```

## Set the 0 values from `verbal_form_finite_id` and `verbal_form_infinte_id` to `NULL` to enable ForeignKeyField

```sql
UPDATE word_references SET verbal_form_finite_id = NULL WHERE verbal_form_finite_id = 0;
UPDATE word_references SET verbal_form_infinite_id = NULL WHERE verbal_form_infinite_id = 0;
```

---

## Connection Options

* Using `peewee`
* Using `sqlalchemy` (WIP)

## Credits

* Oliver Hellwig: Digital Corpus of Sanskrit (DCS). 2010-2021. [GitHub](https://github.com/OliverHellwig/sanskrit/tree/master/dcs/data)
