import math
import urllib.request
from PIL import Image
import io
import cv2
import numpy as np
import sys
import os
import glob

Radius_Earth = 6378137
Minimum_Latitude = -85.05112878
Minimum_Longitude = -180
Maximum_Latitude = 85.05112878
Maximum_Longitude = 180

# Converting Latitude/Longitude to Pixels
def latlong_to_pixelXY(latitude,longitude,detail_level):
    """
    :param latitude: 
    :param longitude: 
    :param detail_level: 
    :return: latitude, longitude to pixel value
    """
    latitude=clip(latitude,Minimum_Latitude,Maximum_Latitude)
    longitude=clip(longitude, Minimum_Longitude, Maximum_Longitude)
    x=(longitude+180)/360
    sinLatitude=math.sin(latitude*math.pi/180)
    y=0.5-math.log((1+sinLatitude)/(1-sinLatitude))/(4*math.pi)
    map_size=size_map(detail_level)
    x_pixel=int(clip(x*map_size+0.5,0,map_size-1))
    y_pixel=int(clip(y*map_size+0.5,0,map_size-1))
    return x_pixel,y_pixel

# Converting Pixels to their corresponding Latitude/Longitude
def pixeXY_to_latlong(x_pixel,y_pixel,detail_level):
	map_size=size_map(detail_level)
	x=(clip(x_pixel,0,map_size-1)/map_size)-0.5
	y=0.5-(clip(y_pixel,0,map_size-1)/map_size)
	latitude=90-360*atan(exp(-y*2*pi))/pi
	longitude=360*x
	return latitude,longitude

# Converting the Pixel Values to Map Tiles
def pixelXY_to_tileXY(x_pixel,y_pixel):
    """
    :param pixleX: 
    :param pixelY: 
    :return: tileXY co-ordinates
    """
    x_tile=x_pixel/256
    y_tile=y_pixel/256
    return x_tile,y_tile

# Converting the Latitude/Longitude Values to Map Tiles
def latlong_to_tile(latitude,longitude,detail_level):
    """
    :param latitude: 
    :param longitude: 
    :param level: 
    :return: lat long to tile XY cordinates
    """
    x_pixel,y_pixel=latlong_to_pixelXY(latitude,longitude,detail_level)
    x_tile,y_tile=pixelXY_to_tileXY(x_pixel,y_pixel)
    return x_tile,y_tile

# Generating Quad Key from the Tile Values
def tileXY_to_quadkey(x_tile,y_tile,detail_level):
    """
    :param x_tile: 
    :param y_tile: 
    :param detail_level: 
    :return: quadkey
    """
    quadKey = ""
    for i in range(detail_level):
        temp=detail_level-i
        digit = ord('0')
        mask = 1 << (temp-1)
        if (x_tile & mask) is not 0:
            digit += 1
        if (y_tile & mask) is not 0:
            digit +=2
        quadKey += chr(digit)
    return quadKey

# Retrieving Map Images Based on Quad Key
def getimage_from_quadkey(quad_keys):
    for i in range(0,len(quad_keys)):
        image_filename = "image_"+str(i+1)+".jpeg"
        #using these quad keys downloading the corresponding images
        image_url="http://h0.ortho.tiles.virtualearth.net/tiles/h%s.jpeg?g=131"%(quad_keys[i])
        urllib.request.urlretrieve(image_url,image_filename)

# Joining the images to create the resultant image
def join_images(count):
    img_list=list()
    image_tuple=list()
    for i in range(0,count):
        img_list.append(cv2.imread("image_"+str(i+1)+".jpeg"))
    
    subList = [img_list[n:n+4] for n in range(0, len(img_list), 4)]
    for i in range(0,len(subList)):
        image_tuple.append(list(np.vstack(subList[i])))
    final_image = np.hstack(tuple(image_tuple))
    cv2.imwrite('image_MapResult.jpeg',final_image)
    

# If the input exceeds the minimum or maximum value of latitude/longitude clip it into the minimum or maximum value 
def clip(n, minValue, maxValue):
    """
    :param n: 
    :param minValue: 
    :param maxValue: 
    :return: min/max value
    """
    return min(max(n,minValue),maxValue)

def size_map(detail_level):
    if detail_level>=1 and detail_level<=23:
        return 256 << detail_level

def ground_resolution(latitude,detail_level):
    if detail_level>=1 and detail_level<=23:
        latitude=clip(latitude,Minimum_Longitude,Maximum_Longitude)
        return math.cos(latitude*math.pi/180)*2*math.pi*Radius_Earth/size_map(detail_level)

def mapscale(latitude,detail_level,screenDPI):
	if detail_level>=1 and detail_level<=23:
		return ground_resolution(latitude,detail_level)*screenDPI/0.0254


def main():
    print("Starting Appliction")
    print("Removing existing image JPEG files")
    for filename in glob.glob('image_*.jpeg'):
    	os.remove(filename)
    lat1 = float(sys.argv[1])
    lon1 = float(sys.argv[2])
    lat2 = float(sys.argv[3])
    lon2 = float(sys.argv[4])
    print("generating tiles")
    x1,x2 = latlong_to_tile(lat1,lon1,17)
    y1,y2 = latlong_to_tile(lat2,lon2,17)
    if x1>y1:
        t1,t2=y1,y2
        y1,y2=x1,x2
        x1,x2=t1,t2
    tiles_list=list()
    quad_keys=list()
    # calculate number of tiles 
    for i in range(int(x1),int(y1+1)):
        for j in range(int(x2),int(y2+1)):
            tiles_list.append((i,j))
    print("Total images genarated : ",len(tiles_list))
    print("generating quadkey for image tiles...")
    for i in range(0,len(tiles_list)):
        quadkey=tileXY_to_quadkey(tiles_list[i][0],tiles_list[i][1],17)
        quad_keys.append(quadkey)
    print("QuadKeys Generated.")
    print("Getting images for quad keys")
    getimage_from_quadkey(quad_keys)
    print("Joining all images")
    join_images(len(quad_keys))
    print("final image generated")    


if __name__ == '__main__':
	main()