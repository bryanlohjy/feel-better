import requests
from typing import TypedDict, Union, Literal, Optional
import json

api_url = "https://api.pexels.com/v1"
with open("api_keys.json") as user_file:
    file_contents = user_file.read()
    api_key = json.loads(file_contents)["pexels"]


class SearchOptions(TypedDict):
    # The search query. Ocean, Tigers, Pears, etc.
    query: str
    # Desired photo orientation. The current supported orientations are: landscape, portrait or square.
    orientation: Optional[
        Union[Literal["portrait"], Literal["landscape"], Literal["square"]]
    ]
    # Minimum photo size. The current supported sizes are: large(24MP), medium(12MP) or small(4MP).
    size: Optional[Union[Literal["large"], Literal["medium"], Literal["small"]]]
    # Desired photo color. Supported colors: red, orange, yellow, green, turquoise, blue, violet, pink, brown, black, gray, white or any hexidecimal color code (eg. #ffffff).
    color: Optional[str]
    # The locale of the search you are performing. The current supported locales are: 'en-US' 'pt-BR' 'es-ES' 'ca-ES' 'de-DE' 'it-IT' 'fr-FR' 'sv-SE' 'id-ID' 'pl-PL' 'ja-JP' 'zh-TW' 'zh-CN' 'ko-KR' 'th-TH' 'nl-NL' 'hu-HU' 'vi-VN' 'cs-CZ' 'da-DK' 'fi-FI' 'uk-UA' 'el-GR' 'ro-RO' 'nb-NO' 'sk-SK' 'tr-TR' 'ru-RU'.
    locale: Optional[str]
    # The page number you are requesting. Default: 1
    page: Optional[int]
    # The number of results you are requesting per page. Default: 15 Max: 80
    per_page: Optional[int]


def search(options: SearchOptions):
    url = f"{api_url}/search"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers, params=options)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(e)
