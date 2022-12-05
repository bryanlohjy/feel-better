import face_recognition
from PIL import Image, ImageDraw
import numpy
import requests
from io import BytesIO
from pexels import search
from typing import Tuple, Union, Literal, List
import json
import argparse
from tqdm import tqdm


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


def normalize_landmarks(img, landmarks):
    (img_h, img_w, _) = img.shape
    normalized = {}
    for (key, value) in landmarks.items():
        normalized[key] = [[coord[0] / img_w, coord[1] / img_h] for coord in value]
    return normalized


def get_primary_face_in_image(url):
    img = load_image_from_url(url)
    face_locations = face_recognition.api.face_locations(img)
    face_boxes = [face_location_to_box(img, location) for location in face_locations]
    if face_boxes:
        # return the largest box
        box_areas = [b["width"] * b["height"] for b in face_boxes]
        primary_face_index = box_areas.index(max(box_areas))
        primary_face_box = face_boxes[primary_face_index]

        landmarks_list = face_recognition.api.face_landmarks(img)
        landmarks = landmarks_list[primary_face_index]

        return {
            "face_box": primary_face_box,
            "landmarks": {
                "norm": normalize_landmarks(img, landmarks),
                "values": landmarks,
            },
        }


def photo_to_iterable_item(photo):
    src = photo["src"]["large"]
    face = get_primary_face_in_image(src)
    return {
        "src": src,
        "avg_color": photo["avg_color"],
        "description": photo["alt"],
        "face_box": face.get("face_box", None) if face else [],
        "landmarks": face.get("landmarks", None) if face else [],
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


Landmark = Union[
    Literal["chin"],
    Literal["left_eyebrow"],
    Literal["right_eyebrow"],
    Literal["nose_bridge"],
    Literal["nose_tip"],
    Literal["left_eye"],
    Literal["right_eye"],
    Literal["top_lip"],
    Literal["bottom_lip"],
]


def get_vector_from_landmarks(item, landmarks: List[Landmark]):
    vector = numpy.array([])
    for landmark_key in landmarks:
        landmark_coords = numpy.array(item["landmarks"]["norm"][landmark_key]).flatten()
        vector = numpy.concatenate([vector, landmark_coords])
    return vector.tolist()


def get_distance_between_vectors(a: List[float], b: List[float]):
    dist = numpy.linalg.norm(numpy.array(a) - numpy.array(b))
    return dist


def sort_iterable_by_landmarks(iterable, landmarks):
    base_vector = get_vector_from_landmarks(iterable[0], landmarks)
    sortables = [
        {
            "item": item,
            "dist_from_base": get_distance_between_vectors(
                base_vector, get_vector_from_landmarks(item, landmarks)
            ),
        }
        for item in iterable
    ]
    sorted_iterable = sorted(sortables, key=lambda x: x["dist_from_base"])
    return [item["item"] for item in sorted_iterable]


def write_json(path: str, dict):
    json_object = json.dumps(dict, indent=2)

    with open(path, "w") as outfile:
        outfile.write(json_object)


debug_folder_path = "scripts/debug"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument(
        "-q", "--query", help="Search query", default="happy portrait face"
    )
    parser.add_argument(
        "-c",
        "--count",
        help="Amount of images to get (max of 80)",
        default="80",
        type=int,
    )
    parser.add_argument(
        "-s",
        "--sort_by_landmarks",
        help="List of landmarks to sort by",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="Output path",
        default="src/iterables/iterable.json",
    )
    parser.add_argument(
        "-d", "--debug", help="Output path", default=False, type=lambda v: bool(v)
    )

    # # Read arguments from command line
    args = parser.parse_args()

    # fetch data from pexels
    results = search({"query": args.query, "per_page": args.count})
    photos = [photo for photo in results["photos"]]

    # detect face locations
    iterable = []
    print("Detecting faces...")
    for photo in tqdm(photos):
        item = photo_to_iterable_item(photo)
        if item["face_box"]:
            iterable.append(item)

    if args.sort_by_landmarks:
        iterable = sort_iterable_by_landmarks(iterable, args.sort_by_landmarks)

    # output
    write_json(args.output_path, {"iterable": iterable})
    print(f"Created iterable at {args.output_path}")

    if args.debug:
        print("Saving debug images...")
        # visualize face_boxes:
        for i, item in tqdm(enumerate(iterable)):
            path = f'{debug_folder_path}/{i}_{item["description"].lower().replace(" ", "_")}.png'
            visualize_item(path, item)
            print(f"Saved visualization at {path}")
