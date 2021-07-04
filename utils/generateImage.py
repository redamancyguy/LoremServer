import os
import random
from io import BytesIO
from PIL import ImageFont
from PIL.ImageDraw import ImageDraw
from PIL import Image
from wordcloud import WordCloud


def wordImage(data):
    wc = WordCloud(
        font_path=os.getcwd() + '/utils/code.otf',
        background_color=None,
        max_words=2000,
        mode='RGBA')
    if type(data) is str:
        wc.generate(data)
    elif type(data) is dict:
        wc.generate_from_frequencies(data)
    matrix_RGB = wc.to_array()
    image = Image.fromarray(matrix_RGB)
    fp = BytesIO()
    image.save(fp, format='PNG')
    return fp.getvalue()


def codeImage(verify_code):
    mode = 'RGB'
    size = (200, 100)
    red = random.randrange(255)
    green = random.randrange(255)
    blue = random.randrange(255)
    color_bg = (red, green, blue)
    image = Image.new(mode=mode, size=size, color=color_bg)
    imageDraw = ImageDraw(image, mode=mode)
    imageFont = ImageFont.truetype(os.getcwd() + '/utils/code.otf', 100)
    for i, item in enumerate(verify_code):
        fill = (random.randrange(255), random.randrange(255), random.randrange(255))
        imageDraw.text(xy=(50 * i, 0), text=item, fill=fill, font=imageFont)
    for i in range(1000):
        fill = (random.randrange(255), random.randrange(255), random.randrange(255))
        xy = (random.randrange(201), random.randrange(100))
        imageDraw.point(xy=xy, fill=fill)
    fp = BytesIO()
    image.save(fp, 'png')
    return fp.getvalue()


if __name__ == '__main__':
    # wordImage('sunwenli wenlisun zhaixiue exiuzhai')
    data = open('test.txt', 'r').read()
    wc = WordCloud(
        font_path= 'code.otf',
        background_color=None,
        max_words=2000,
        mode='RGBA')
    if type(data) is str:
        wc.generate(data)
    elif type(data) is dict:
        wc.generate_from_frequencies(data)
    else:
        print('data type error')
    matrix_RGB = wc.to_array()
    image = Image.fromarray(matrix_RGB)
    image.show()
