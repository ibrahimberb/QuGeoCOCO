import json
import os.path as op
import glob

import logging
from typing import Dict

from src.log import get_handler

handler = get_handler()

log = logging.getLogger(__name__)
log.handlers[:] = []
log.addHandler(handler)
log.setLevel(logging.DEBUG)


class GeoJSONHandler:
    """
    Class for handling GeoJSON files exported from QuPath. Contains information regarding the coordinates, properties,
    and class names of the annotations.
    """

    def __init__(self, geojson_folder_path):
        self.geojson_folder_path = geojson_folder_path
        self.geojson_files_to_content = self.get_geojson_files()
        self.geojson_files = list(self.geojson_files_to_content.keys())
        self.file_to_annotations = self.load_annotations()
        self.class_id_mapping = self.create_class_id_mapping()
        self.unique_classes = self.load_unique_classes()

    def get_geojson_files(self):
        """
        This function retrieves GeoJSON files from a specified folder and returns them as a dictionary.

        Returns
        -------
        geojson_files (dict): A dictionary where the keys are the filenames of the GeoJSON files and the values are the
        corresponding parsed GeoJSON data as dictionaries.
        """
        geojson_files = {}
        for filepath in glob.glob(op.join(self.geojson_folder_path, "*.geojson")):
            filename = op.basename(filepath)
            geojson = json.load(open(filepath))
            assert type(geojson) == dict, (
                f"Expected a dictionary, got {type(geojson)}\nMake sure you check the `Export as FeatureCollection` "
                f"option in QuPath when exporting the annotation."
            )
            geojson_files[filename] = geojson

        log.info(
            f"Found {len(geojson_files)} geojson file(s) in {self.geojson_folder_path}"
        )
        return geojson_files

    def load_unique_classes(self):
        """
        Load and return a list of unique classes from the provided class ID mapping.

        Note
        ----
            If one may want to change the class ID mapping in an alphanumerical order, one may
            sort the list of unique classes.
        """
        unique_classes = list(set(self.class_id_mapping.values()))
        log.info(f"Unique classes: {unique_classes}")
        return unique_classes

    def update_mapping(self, new_mapping):
        """
        Update the class ID mapping and the list of unique classes. This may be a handy function if one wants to
        assign a new class ID mapping to the GeoJSONHandler object.

        Parameters
        ----------
        new_mapping (dict): A dictionary where the keys are the class names and the values are the corresponding class
        IDs.

        Example
        --------
        # Let's say `class_1` is assigned to class ID 1 and `class_2` is assigned to class ID 2.
        # We can update the mapping as follows:
        >>> geojson_handler.update_mapping({"class_1": 2, "class_2": 1})
        """
        self.class_id_mapping = new_mapping
        self.unique_classes = sorted(list(set(self.class_id_mapping.values())))
        log.info(f"Mapping updated.")
        log.info(f"Unique classes: {self.unique_classes}")
        log.info(f"Class id mapping: {self.class_id_mapping}")

    def update_mapping_names(self, old_name, new_name):
        """
        Update class names within the class ID mapping based on the provided old and new names.

        Parameters:
        -----------
            old_name (str): The existing class name to be updated.
            new_name (str): The new class name to replace the old name.

        Example
        --------
        # Let's say `class_1` is assigned to class ID 1 and `class_2` is assigned to class ID 2.
        # We can update the mapping as follows:
        >>> geojson_handler.update_mapping_names("class_1", "my_class_1")
        """
        new_mapping = self.class_id_mapping.copy()
        if old_name not in new_mapping:
            raise ValueError(f"{old_name} not in the mapping.")
        if new_name in new_mapping:
            raise ValueError(f"{new_name} already in the mapping.")

        new_mapping[new_name] = new_mapping.pop(old_name)
        self.update_mapping(new_mapping)

    def create_class_id_mapping(self) -> Dict[str, int]:
        """
        Create and return a mapping of class names to unique IDs based on GeoJSON content. The mapping contains the
        class names are keys and their corresponding unique IDs (incremented by 1) are values.

        Returns
        -------
            class_id_mapping (dict): A dictionary mapping class names to unique integer IDs.
        """
        unique_classes = set()
        for filename, geojson in self.geojson_files_to_content.items():
            for feature in geojson["features"]:
                class_name = feature["properties"]["classification"]["name"]
                unique_classes.add(class_name)

        class_id_mapping = {
            class_name: i + 1 for i, class_name in enumerate(unique_classes)
        }
        log.info(f"Class id mapping: {class_id_mapping}")
        return class_id_mapping

    def load_annotations(self):
        """
        Parse GeoJSON data to load and return a dictionary of filename-to-annotation-class pairs.
        """
        file_to_annotation_class_pairs = {}
        for filename, geojson in self.geojson_files_to_content.items():
            file_to_annotation_class_pairs[filename] = self.parse_geojson(geojson)

        return file_to_annotation_class_pairs

    @staticmethod
    def parse_geojson(geojson):
        """
        Parse GeoJSON data to extract annotation class pairs.

        Parameters
        ----------
            geojson (dict): GeoJSON data containing annotation features.

        Returns
        -------
            annotation_class_pairs (list): A list of tuples, each containing annotation coordinates and corresponding
            class names.
        """
        annotation_class_pairs = []
        for feature in geojson["features"]:
            if feature["geometry"]["type"] != "Polygon":
                raise ValueError("Only Polygon features are supported")

            [coordinates] = feature["geometry"]["coordinates"]
            class_name = feature["properties"]["classification"]["name"]
            coordinates = [list(coord) for coord in coordinates]
            annotation_class_pairs.append((coordinates, class_name))

        return annotation_class_pairs
