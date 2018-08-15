import random

async def zalgo(text: str, intensity: int = 50):
    zalgo_threshold = intensity
    zalgo_chars = [chr(i) for i in range(0x0300, 0x036F + 1)]
    zalgo_chars.extend([u'\u0488', u'\u0489'])
    source = text.upper()
    if not is_narrow_build:
        source = insert_randoms(source)
    zalgoized = []
    for letter in source:
        zalgoized.append(letter)
        zalgo_num = random.randint(0, zalgo_threshold) + 1
        for _ in range(zalgo_num):
            zalgoized.append(random.choice(zalgo_chars))
    response = random.choice(zalgo_chars).join(zalgoized)
    return response

async def insert_randoms(text):
    random_extras = [chr(i) for i in range(0x1D023, 0x1D045 + 1)]
    newtext = []
    for char in text:
        newtext.append(char)
        if random.randint(1, 5) == 1:
            newtext.append(random.choice(random_extras))
    return u''.join(newtext)

def is_narrow_build():
    try:
        chr(0x10000)
    except ValueError:
        return True
    return False
