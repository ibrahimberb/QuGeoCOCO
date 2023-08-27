import json

import logging
from src.log import get_handler

handler = get_handler()

log = logging.getLogger(__name__)
log.handlers[:] = []
log.addHandler(handler)
log.setLevel(logging.DEBUG)


class QuPathImage:
    """
    A template class containing the information of a QuPath image - a property in exported QuPath project file.
    """

    def __init__(self, image):
        self.image = image
        self.image_path = image["serverBuilder"]["uri"]
        self.metadata = image["serverBuilder"]["metadata"]
        self.entry_id = image["entryID"]
        self.randomized_name = image["randomizedName"]
        self.name = self.metadata["name"]
        self.width = self.metadata["width"]
        self.height = self.metadata["height"]

    def __str__(self):
        return f"Image: {self.name} ({self.width}x{self.height})"

    def __repr__(self):
        return self.__str__()


class QuPathProjectHandler:
    """
    A class for handling QuPath project files.
    """

    def __init__(self, path):
        qupath_project_extension = ".qpproj"
        if not path.endswith(qupath_project_extension):
            raise ValueError(f"Invalid file type. Must be a {qupath_project_extension} file.")
        self.path = path
        self.project = self.load_project()
        self.images = self.load_images()
        log.info(f"Project has {len(self.images)} images.")

    def load_project(self):
        log.info("Loading the project file...")
        return json.load(open(self.path))

    def load_images(self):
        log.info("Loading images...")
        image_objects = [QuPathImage(image) for image in self.project["images"]]
        return {image_obj.name: image_obj for image_obj in image_objects}
