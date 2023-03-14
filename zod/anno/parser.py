"""Annotation parsers."""
import json
from typing import Any, Dict, List

from zod.anno.tsr.class_map import get_class_idx
from zod.constants import AnnotationProject, Camera
from zod.data_classes.box import Box2D

from .object import ObjectAnnotation
from .tsr.traffic_sign import TrafficSignAnnotation


def _read_annotation_file(annotation_file: str) -> List[Dict[str, Any]]:
    """Read an annotation file."""
    with open(annotation_file, "r") as file:
        annotation = json.load(file)
    return annotation


def parse_object_detection_annotation(annotation_path: str) -> List[ObjectAnnotation]:
    """Parse the objects annotation from the annotation string."""
    annotation = _read_annotation_file(annotation_path)
    return [ObjectAnnotation.from_dict(obj) for obj in annotation]


def parse_traffic_sign_annotation(annotation_path: str) -> List[TrafficSignAnnotation]:
    """Parse the traffic sign annotation from the annotation string."""
    annotation = _read_annotation_file(annotation_path)
    annotated_objects = []
    for annotated_object in annotation:
        # Ignore all unclear traffic signs
        if annotated_object["properties"]["unclear"]:
            continue
        bounding_box = Box2D.from_points(annotated_object["geometry"]["coordinates"], Camera.FRONT)
        annotated_objects.append(
            TrafficSignAnnotation(
                bounding_box=bounding_box,
                traffic_sign_class=annotated_object["properties"]["class"],
                traffic_sign_idx=get_class_idx(annotated_object["properties"]["class"]),
                occlusion_ratio=annotated_object["properties"]["occlusion_ratio"],
                annotation_uuid=annotated_object["properties"]["annotation_uuid"],
                electronic_sign=annotated_object["properties"]["is_electronic"],
                uuid=annotated_object["properties"]["annotation_uuid"],
            )
        )
    return annotated_objects


def parse_lane_markings_annotation(annotation_path: str, classes=["lm_dashed", "lm_solid"]):
    """Parse the lane markings annotation from the annotation string."""
    annotations = _read_annotation_file(annotation_path)
    polygons = []
    for annotation in annotations:
        if "class" in annotation["properties"]:
            annotated_class = annotation["properties"]["class"]
            if annotated_class in classes:
                polygons.append(annotation["geometry"]["coordinates"])
    return polygons


def parse_ego_road_annotation(annotation_path: str, classes=["EgoRoad_Road"]):
    """Parse the egoroad annotation from the annotation string."""
    annotations = _read_annotation_file(annotation_path)
    polygons = []
    for annotation in annotations:
        if "class" in annotation["properties"]:
            annotated_class = annotation["properties"]["class"]
            if annotated_class in classes:
                polygons.append(annotation["geometry"]["coordinates"])
    return polygons


ANNOTATION_PARSERS = {
    AnnotationProject.LANE_MARKINGS: parse_lane_markings_annotation,
    AnnotationProject.EGO_ROAD: parse_ego_road_annotation,
    AnnotationProject.OBJECT_DETECTION: parse_object_detection_annotation,
    AnnotationProject.TRAFFIC_SIGNS: parse_traffic_sign_annotation,
}


if __name__ == "__main__":
    pass
