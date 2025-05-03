import json
import uuid
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.cache import cache
from .tasks import generate_image
from .coder import decode


class ImageGenerationView(View):
    """
    Класс для создания задачи генерации изображения, задача отправляется в redis
    Клиент получит ответ uuid задачи
    Обязательные параметры:\n
        promt - промт пользователя для генерации; \n
        style - стиль картинки, который доступен из https://cdn.fusionbrain.ai/static/styles/key; \n
        secret - секретный ключ, который шифруется в картинку.

    Секретный ключ также рекомендуется шифровать со стороны сервиса, который запрашивает картинку,
    чтобы текущий и Ваш сервисы не могли получить доступ к данным

    """

    def post(self, request):
        data = json.loads(request.body)

        if data.get("promt") and data.get("style") and data.get("secret"):

            uuid_task = uuid.uuid4()
            cache.set(uuid_task, {"STATUS": "GENERATE"}, timeout=700)

            generate_image.delay(uuid_task, data)
            return JsonResponse({"TASK_ID": f"{uuid_task}"}, status=200)

        else:
            return HttpResponse(status=400, reason="The necessary parameters are missing (promt, style, secret).")


class ImagegenerationCheckView(View):
    """
    Класс для проверки готовности генерации и зашифрования картинки
    Принимает на вход uuid задачи, которую клиент получил в ответ на запрос генерации
    Возвращает статус задачи, если картинка готова, то возвращает вместе со статусом в формате base64
    """

    def get(self, request, uuid_task):

        data = cache.get(uuid_task)
        if data:
            if data["STATUS"] == "DONE" and data["IMAGE"]:
                image = "data:image/png;base64," + data["IMAGE"]
                data["IMAGE"] = image
                return JsonResponse(data, status=200)

            elif data["STATUS"] == "GENERATE":
                return JsonResponse(data, status=200)
        else:
            return HttpResponse([None], status=200)


class ImageCheckView(View):
    """
    Класс для нахождения в картинке зашифрованных данных
    """

    def post(self, request):
        try:
            # Загружает JSON-данные из тела запроса
            data = json.loads(request.body)

            # Получает изображение в виде base64-строки

            image_base64 = data.get("image")
            if not image_base64:
                return HttpResponse(status=415, reason="No image provided in the request.")

            if "base64," in image_base64:
                image_base64 = image_base64.split("base64,")[1].strip()

            decode_str = decode(image_base64)

            if decode_str:
                return HttpResponse(decode_str, content_type="text/plain")
            else:
                return HttpResponse(status=400, reason="Could not get data from the image.")

        except Exception:
            # Если подключать логирование, использовать e
            return HttpResponse(status=400)
