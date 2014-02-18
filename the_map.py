from PIL import Image

class Map:
    def __init__(self, size=None, filename=None):
        if size and filename:
            print "Cannot specify both size and filename!"
            exit(1)
        if size:
            self.width, self.height = size
            self.map = []
            for y in range(self.height):
                self.map.append( [0] * self.width )
            
        elif filename:
            image = Image.open(filename, 'r')
            self.width, self.height = image.size
            self.map = []
            for y in range(self.height):
                a = []
                for x in range(self.width):
                    p = image.getpixel((x,y))
                    if sum(p)/3 < 100:
                        a.append(1)
                    else:
                        a.append(0)
                self.map.append(a)
                
