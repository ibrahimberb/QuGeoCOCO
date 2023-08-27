import os.path as op
from dataclasses import dataclass

from src.qupath_handler import QuPathProjectHandler
from src.geojson_handler import GeoJSONHandler
from src.helpers import export_json

from typing import Union, List

import logging
from src.log import get_handler

handler = get_handler()

log = logging.getLogger(__name__)
log.handlers[:] = []
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def _get_image_id(image_name: str) -> str:
    """
    Uses the image (without the extension) as file image id.
    """

    image_id, _ = op.splitext(image_name)
    return image_id


@dataclass
class ImageData:
    """
    Class for keeping track of images in Coco style.
    coco_style["images"] = [ImageData, ImageData, ...]
    """

    id: str
    dataset_id: int
    path: str
    width: int
    height: int
    file_name: str

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "file_name": self.file_name,
        }


class ImagesField:
    """
    Class for adapting QuPathProjectHandler to COCO Styler
    """

    def __init__(self, qupath_project: QuPathProjectHandler) -> None:
        self.qpp_handler = qupath_project

    def _get_image(self, image_name, json=True) -> Union[ImageData, dict]:
        qupath_image = self.qpp_handler.images[image_name]

        image_data = ImageData(
            id=_get_image_id(qupath_image.name),
            dataset_id=None,  # TODO, not important for now, but can be added later on.
            file_name=qupath_image.name,
            path=qupath_image.image_path,
            height=qupath_image.height,
            width=qupath_image.width,
        )

        if json:
            return image_data.to_json()
        else:
            return image_data

    def get_images(self, json=True) -> List:
        return [
            self._get_image(image_name, json=json)
            for image_name in self.qpp_handler.images.keys()
        ]


class CategoriesField:
    """
    Class for adapting categories to COCO styler.
    """

    def __init__(self, categories: List[str]):
        assert (
            type(categories) == list
        ), f"Categories should be a list of strings, got {type(categories)}"

        self.categories = []
        self.category_id = 1

        for category in categories:
            self.add_category(category)

    def add_category(self, category_name):
        self.categories.append(
            {
                "id": self.category_id,
                "name": category_name,
                # TODO: these fields may be added later depending on the need.
                # "supercategory": "", Leaving this out for now
                #  color, metadata, etc. can be added here
            }
        )
        log.debug(f"Added category: {category_name} (id: {self.category_id})")
        self.category_id += 1

    def get_categories(self):
        return self.categories


@dataclass
class AnnotationData:
    """
    Class for keeping track of annotations in Coco style.
    coco_style["annotations"] = [AnnotationData, AnnotationData, ...]
    """

    id: int
    image_id: str
    category_id: int
    segmentation: List[List[float]]
    area: float
    bbox: List[float]

    def to_json(self):
        return {
            "id": self.id,
            "image_id": self.image_id,
            "category_id": self.category_id,
            "segmentation": self.segmentation,
            "area": self.area,
            "bbox": self.bbox,
        }


class AnnotationsField:
    """
    Class for adapting annotations for COCO style.
    """

    def __init__(self, geojson_handler: GeoJSONHandler) -> None:
        self.geojson_handler = geojson_handler
        self.geojson_files = self.geojson_handler.geojson_files
        self.category_id_mapping = self.geojson_handler.class_id_mapping

    @staticmethod
    def _get_segmentation(geojson_data: List[List[float]]) -> List[float]:
        """
        Returns a list of coordinates in COCO style.
        """
        assert all(
            len(item) == 2 for item in geojson_data
        ), "All sublists should have exactly two items"

        # Flattens a nested list of lists into a single flat list.
        return [value for sublist in geojson_data for value in sublist]

    def _get_category_id(self, class_name: str) -> int:
        """
        Returns category id for a given class name.
        """
        return self.category_id_mapping[class_name]

    def get_annotation(self, geojson_file: str, json=True):
        """
        Returns COCO style annotation.
        """

        annotations_per_geojson = []

        annotation_class_pairs = self.geojson_handler.file_to_annotations[geojson_file]
        for annotation_class_pair in annotation_class_pairs:
            annotation_coordinates = annotation_class_pair[0]
            class_name = annotation_class_pair[1]
            annotation_data = AnnotationData(
                id=None,  # TODO: I think this is not crucial for now.
                image_id=_get_image_id(geojson_file),
                category_id=self.category_id_mapping[class_name],
                segmentation=[self._get_segmentation(annotation_coordinates)],
                area=None,  # TODO: this should be calculated.
                bbox=None,  # TODO: this should be calculated.
            )
            if json:
                annotations_per_geojson.append(annotation_data.to_json())
            else:
                annotations_per_geojson.append(annotation_data)

        return annotations_per_geojson

    def get_annotations(self, json=True) -> List[AnnotationData]:
        """
        Returns a list of all annotations.
        """
        annotations = []
        for geojson_file in self.geojson_files:
            log.debug(f"Processing {geojson_file}...")
            annotations.extend(self.get_annotation(geojson_file, json))
        return annotations


class CocoStyle:
    """
    A template class containing all the fields in COCO style.
    """

    def __init__(
        self,
        images_field: ImagesField,
        categories_field: CategoriesField,
        annotations_field: AnnotationsField,
    ):
        self.images = images_field.get_images()
        self.categories = categories_field.get_categories()
        self.annotations = annotations_field.get_annotations()

        self._json = {
            "images": self.images,
            "categories": self.categories,
            "annotations": self.annotations,
        }

    def to_json(self):
        return self._json


class QuGeoCOCO:
    """
    Main class that harmonizes QuPath and GeoJSON annotations to COCO style.
    Uses:
        - QuPathProjectHandler
        - GeoJSONHandler
    """

    def __init__(
        self,
        qupath_project_file_path,
        geojson_folder_path,
        qugeococo_categories: List[str],
    ):
        self.qpp_handler = QuPathProjectHandler(qupath_project_file_path)
        self.geojson_handler = GeoJSONHandler(geojson_folder_path)
        self.qugeococo_categories = qugeococo_categories
        self.coco_style = self.get_coco_style()

    def get_coco_style(self):
        images_field = ImagesField(self.qpp_handler)
        categories_field = CategoriesField(self.qugeococo_categories)
        annotations_field = AnnotationsField(self.geojson_handler)
        return CocoStyle(
            images_field=images_field,
            categories_field=categories_field,
            annotations_field=annotations_field,
        )

    def save(self, save_path):
        export_json(save_path, self.coco_style.to_json())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert QuPath GeoJSON annotations to COCO style."
    )
    parser.add_argument(
        "--qupath-project",
        type=str,
        required=True,
        help="Path to the QuPath project file (.qpproj)",
    )

    parser.add_argument(
        "--geojson-folder",
        type=str,
        required=True,
        help="Path to the folder containing the GeoJSON files.",
    )

    # categories should be list of strings
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        required=True,
        help="List of categories to be used in the COCO style.",
    )

    parser.add_argument(
        "--save-path",
        type=str,
        required=True,
        help="Path to save the COCO style JSON file.",
    )

    args = parser.parse_args()

    log.info(f"QuPath project file: {args.qupath_project}")
    log.info(f"GeoJSON folder: {args.geojson_folder}")
    log.info(f"Categories: {args.categories}")
    log.info(f"Save path: {args.save_path}")

    qugeococo = QuGeoCOCO(
        qupath_project_file_path=args.qupath_project,
        geojson_folder_path=args.geojson_folder,
        qugeococo_categories=args.categories,
    )

    qugeococo.save(args.save_path)

    log.info(f"Saved COCO style JSON file to {args.save_path}")
