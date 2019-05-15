import multiprocessing as mp
from multiprocessing import Process, Value
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import numpy as np
import cv2
import ctypes
import webcolors

# global for hex of yellow, white, black, lime, aqua, fuschia & blue
colors = ['#FFFF00', '#FFFFFF', '#000000', '#00FF00', '#FF0000', '#00FFFF', '#FF00FF', '#0000FF']
FONT = 'Arial.ttf'


def pOne(queue_a, queue_b, num_images, height, width, amount):
    print("p1")
    #num = num_images.value
    #n = 0
    #for n in range(num):
    # randomly chooses color from color array
    ran = random.choice(colors)
    rgb = webcolors.hex_to_rgb(ran)
    h = height.value
    w = width.value

    array = np.zeros((h, w, 3), np.uint8)
    array[:] = rgb

    # create wrapper
    shr_arr = mp.Array(ctypes.c_double, len(array))

    # put numparray in queue & pass to p2
    queue_a.put(array)
    #p2 = Process(target=pTwo, args=(queue_a, queue_b, num_images, height, width, amount))
    #p2.start()




def pTwo(queue_a, queue_b, num_images, height, width, amount):
    print("p2")
    am = amount.value
    am = + 1
    # make nump array into image
    image = Image.fromarray(queue_a.get())
    name = ('test'+ str(am)+'.png')
    image.save(name)

    # get rgb color from img pix then get hex color
    x = 3
    y = 4
    pix = image.load()
    rgb = pix[x, y]
    hexx = webcolors.rgb_to_hex(rgb)

    # annoying way to do this cv2.circle takes bgr not rgb
    if (hexx == '#ffff00'):
        comp = (128,0,128)
    elif (hexx == '#ffffff'):
        comp = (0,0,0)
    elif (hexx == '#000000'):
        comp = (255,255,255)
    elif (hexx == '#00ff00'):
        comp = (0,0,255)
    elif (hexx == '#ff0000'):
        comp = (0,255,0)
    elif (hexx == '#00ffff'):
        comp = (0,165,255)
    elif (hexx == '#ff00ff'):
        comp = (0,255,0)
    elif(hexx == '#0000ff'):
        comp = (0,165,255)

    color = webcolors.rgb_to_name(rgb)
    if color == 'magenta':
        color = 'fuchsia'
    if color == 'cyan':
        color = 'aqua'

    #get radius
    immg = Image.open(name)
    w, h = immg.size
    r = w * 0.25
    r = int(r)


    # watermark with color name
    wm = cv2.imread(name, -1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(wm, str(color), (0, 25), font, 1, (128, 128, 128))
    new = ("new"+ str(am) + ".jpg")
    cv2.imwrite(new, wm)
    cv2.waitKey(0)

    # find center
    wm_img = cv2.imread(new)
    gray_img = cv2.cvtColor(wm_img, cv2.COLOR_BGR2GRAY)
    moment = cv2.moments(gray_img)
    X = int(moment["m10"]/moment["m00"])
    Y = int(moment["m01"]/moment["m00"])

    #filled circle w comp color
    cv2.circle(wm_img,(X,Y),r,comp,-1)
    cv2.imwrite("final"+ str(am) +".jpg",wm_img)
    cv2.waitKey(0)

    # pass image to queue_b
    final_img = Image.open("new"+ str(am) +".jpg")
    #np_fimg = np.array(final_img)
    queue_b.put(final_img)

def pThree(array_a):
    print("p3")
    npp = np.array(array_a)
    #print(type(npp))
    nparr = np.frombuffer((npp))
    #print(type(nparr))
    cv2.imshow('array_a_img', nparr)
    cv2.waitKey(1)
    cv2.destroyAllWindows()



if __name__ == '__main__':
    event_quit = mp.Event()
    print("Press any key to start or 'q' to quit:")
    while(input()!='q'):
        num = input("Type a number of random images I should generate: ")
        h = input("Enter height: ")
        w = input("Enter width: ")
        a = 0
        num_images = Value('i', int(num))
        height = Value('i', int(h))
        width = Value('i', int(w))
        amount = Value('i', int(a))
        queue_a = mp.Queue()
        queue_b = mp.Queue()

        n = num_images.value
        i = 0
        for i in range(n):
            p1 = Process(target=pOne, args=(queue_a, queue_b, num_images, height, width, amount))
            p1.start()
            p2 = Process(target=pTwo, args=(queue_a, queue_b, num_images, height, width, amount))
            p2.start()

        array_a = mp.Array(ctypes.c_double, 100)
        array_a = queue_b.get()

        p3 = Process(target=pThree, args=(array_a,))
        p3.start()
        p1.join()
        p2.join()
        p3.join()
        event_quit.set()
        print("Press any key to start or 'q' to quit:")
    event_quit.set()
