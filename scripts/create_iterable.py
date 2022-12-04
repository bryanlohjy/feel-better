import face_recognition
from PIL import Image, ImageDraw
import numpy
import requests
from io import BytesIO
from pexels import search
from typing import Tuple
import json
import math


def load_image_from_url(url: str):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return numpy.array(img)


def face_location_to_box(img, box: Tuple[int, int, int, int]):
    (img_h, img_w, _) = img.shape
    (top, right, bottom, left) = box
    return {
        "x": top,
        "y": left,
        "width": right - left,
        "height": bottom - top,
        "norm_x": left / img_w,
        "norm_y": top / img_h,
        "norm_width": (right - left) / img_w,
        "norm_height": (bottom - top) / img_h,
    }


def get_primary_face_box_in_url(url):
    img = load_image_from_url(url)
    face_locations = face_recognition.api.face_locations(img)
    face_boxes = [face_location_to_box(img, location) for location in face_locations]
    if face_boxes:
        # return the largest box
        box_areas = [b["width"] * b["height"] for b in face_boxes]
        primary_face_box = face_boxes[box_areas.index(max(box_areas))]
        return primary_face_box
    else:
        return []


def photo_to_iterable_item(photo):
    src = photo["src"]["large"]
    return {
        "src": src,
        "avg_color": photo["avg_color"],
        "description": photo["alt"],
        "face_box": get_primary_face_box_in_url(src),
    }


def visualize_item(path, iterable):
    img_array = load_image_from_url(iterable["src"])
    img = Image.fromarray(img_array)
    (img_height, img_width, _) = img_array.shape
    if iterable["face_box"]:
        img_with_box = ImageDraw.Draw(img)
        face_box = iterable["face_box"]
        box_position = [
            (
                (face_box["norm_x"]) * img_width,
                (face_box["norm_y"]) * img_height,
            ),
            (
                (face_box["norm_x"] + face_box["norm_width"]) * img_width,
                (face_box["norm_y"] + face_box["norm_height"]) * img_height,
            ),
        ]
        img_with_box.rectangle(box_position, outline="red")

    img.save(path)


def write_json(path: str, dict):
    json_object = json.dumps(dict, indent=2)

    with open(path, "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    output_path = "src/iterables/iterable.json"
    # TODO: cmd line args for query, pages, image size

    # fetch data from pexels
    results = search({"query": "happy portrait face", "per_page": 80})
    photos = [photo for photo in results["photos"]]

    # detect face locations
    iterable = [photo_to_iterable_item(photo) for photo in photos]
    iterable = [i for i in iterable if i["face_box"]]

    # output
    write_json(output_path, {"iterable": iterable})
    print(f"Created iterable at {output_path}")

    # visualize face_boxes:
    for i, item in enumerate(iterable):
        path = f'scripts/debug/{i}_{item["description"].lower().replace(" ", "_")}.png'
        visualize_item(path, item)
        print(f"Saved visualization at {path}")
