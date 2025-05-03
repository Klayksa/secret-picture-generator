from django.conf import settings
from PIL import Image
from cryptography.fernet import Fernet
import io
import base64


def code(image, data, key=settings.ENCRIPTION_KEY) -> bytes:
    # Кодируем
    data_coder = Fernet(key)
    encrypted_string = data_coder.encrypt(data.encode())
    binary_data = "".join(format(byte, "08b") for byte in encrypted_string)

    image = Image.open(io.BytesIO(base64.b64decode(image)))
    pixels = image.load()
    index = 0
    width, height = image.size

    # По порядку проходится по пикселям изображения и заменяет младшие биты канала RGB на биты зашифрованной строки
    for y in range(height):
        for x in range(width):
            if index < len(binary_data):
                r, g, b = pixels[x, y]

                r = (r & 0xFE) | int(binary_data[index])
                index += 1

                if index < len(binary_data):
                    g = (g & 0xFE) | int(binary_data[index])
                    index += 1

                if index < len(binary_data):
                    b = (b & 0xFE) | int(binary_data[index])
                    index += 1

                pixels[x, y] = (r, g, b)

            if index >= len(binary_data):
                break

    # Для возврата запроса изображение преобразуется в base64
    bytes_data = io.BytesIO()
    image.save(bytes_data, format="PNG")
    bytes_data.seek(0)

    return bytes_data


def decode(image, key=settings.ENCRIPTION_KEY) -> str:
    # Декодируется изображение и из пикселей собирается строка битов для расшифровки
    image = Image.open(io.BytesIO(base64.b64decode(image)))
    pixels = image.load()
    binary_data = ""
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i : i + 8]
        if len(byte) == 8:
            byte_data.append(int(byte, 2))

    if not byte_data:
        raise ValueError("Нет данных для расшифровки.")

    # Расшифровка данных
    data_coder = Fernet(key)

    try:
        decrypted_string = data_coder.decrypt(bytes(byte_data)).decode()
        return decrypted_string
    except Exception:
        return None
