from the_map import Map
from voronoi import *
import sys
from PIL import Image

if __name__=='__main__':
    m = Map(filename=sys.argv[1])
    v = DynamicVoronoi(m.height, m.width, m.map)
    v.update()
    
    image = Image.new("RGB", (v.size_x, v.size_y))
    for y in range(v.size_y):
        for x in range(v.size_x):
            if v.isVoronoi(x,y):
                image.putpixel((x,y),(0,0,255))
            if v.grid_map[x][y]==1:
                image.putpixel((x,y),(0,0,0))
            else:
                image.putpixel((x,y),(255,255,255))
    image.show()
