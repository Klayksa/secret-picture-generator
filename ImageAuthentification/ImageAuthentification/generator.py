import json, time, requests


class ImageGenerator:
    """
    Класс для генерации изображений с помощью fusionbrain api.
    При генерации изображения fusionbrain сначала отдает uuid своей задачи, по которой можно получить статус и картинку с помошью check_generation.
    При инициализации передается api_key и secret_key, которые берутся из django.settings или из виртуального окружения.
    """

    def __init__(self, api_key, secret_key):
        self.URL = "https://api-key.fusionbrain.ai/"
        self.AUTH_HEADERS = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }
        self.model = self.__get_model()

    def __get_model(self) -> int:
        # Получаем id модели fusionbrain
        response = requests.get(self.URL + "key/api/v1/models", headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]["id"]

    def generate(self, prompt, style, images=1, width=1024, height=1024) -> str:
        # Запрос на генерацию изображений
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": f"{style}",
            "generateParams": {
                "query": f"{prompt}",
            },
        }

        data = {
            "model_id": (None, self.model),
            "params": (None, json.dumps(params), "application/json"),
        }
        response = requests.post(
            self.URL + "key/api/v1/text2image/run",
            headers=self.AUTH_HEADERS,
            files=data,
        )
        data = response.json()
        return data["uuid"]

    def check_generation(self, request_id, attempts=60, delay=10) -> str:
        # Проверяем статус генерации
        while attempts > 0:
            response = requests.get(self.URL + "key/api/v1/text2image/status/" + request_id, headers=self.AUTH_HEADERS)
            data_generation = response.json()
            if data_generation["status"] == "DONE":
                images = data_generation["images"]
                return images[0]

            attempts -= 1
            time.sleep(delay)
        return None
