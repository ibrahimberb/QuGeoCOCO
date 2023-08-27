# `SRC` Module

The `src` module contains the following files:

```
|__ src
    |__ __init__.py
    |__ geojson_handler.py
    |__ helpers.py
    |__ log.py
    |__ qugeococo.py
    |__ QuGeoCOCO_Module.MD
    |__ qupath_handler.py
```

## `geojson_handler.py`

This script contains the `GeoJsonHandler` class, which is responsible for
holding the information regarding the coordinates, properties,
and class names of the annotations, and that information can be used by
the `QuGeoCOCO` class to generate the COCO-style JSON file.

## `qupath_handler.py`

This script contains the `QuPathProjectHandler` class, which is responsible
for reading the annotations from the QuPath project file and converting
them into a format that can be used by the `QuGeoCOCO` class.

## `qugeococo.py`

This script contains the `QuGeoCOCO` class, which is harmonizes the
information from the `GeoJsonHandler` and `QuPathProjectHandler` classes
to generate the COCO-style JSON file.

It also contains the `CocoStyle` class that provides
a template for COCO-style representations of annotations.
The COCO-style contains the following essential components:

* _images_: a list of image information, including the image ID, file name.
* _annotations_: a list of annotation information, including the annotation ID, image ID, category ID, and bounding box
  coordinates.
* _categories_: a list of category information, including the category ID and name.

Therefore, the script also contains template classes for these fields:

* ImageField
* AnnotationField
* CategoryField

## `helpers.py`

This script contains helper functions that are used by the `QuGeoCOCO` class. More functionality
can be added to this script as needed.

## `log.py`

A convenience script that contains a function for logging messages to the console while interacting
with Jupyter notebooks.

## `__init__.py`

Defines the `src` module as a Python module.

## `QuGeoCOCO_Module.MD` (this file)

A markdown file that contains the documentation for the `src` module.
