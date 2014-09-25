'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy

def main():

    cube=bpy.data.objects["Cube"]
    print(cube.name)

if __name__ == '__main__':
    main()