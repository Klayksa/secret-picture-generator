from celery import shared_task
from django.core.cache import cache
from django.conf import settings
import base64
from .generator import ImageGenerator
from .coder import code


@shared_task
def generate_image(uuid_task, data):
    promt = data.get("promt")
    style = data.get("style")
    secret = data.get("secret")

    generator = ImageGenerator(
        api_key=settings.IMAGE_API_KEY, secret_key=settings.IMAGE_API_SECRET_KEY
    )
    uuid_generation = generator.generate(prompt=promt, style=style)
    image = generator.check_generation(request_id=uuid_generation)

    secret_image = code(image, secret)

    secret_image = base64.b64encode(secret_image.getvalue()).decode("utf-8")

    cache.set(uuid_task, {"STATUS": "DONE", "IMAGE": secret_image}, timeout=600)
