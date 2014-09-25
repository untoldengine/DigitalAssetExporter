'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy

class materials:
    def __init__(self):
        self.diffuse=[]
        self.specular=[]
        
    
class coordinates:
    def __init__(self):
        self.vertices=[]
        self.normal=[]
        self.uv=[]


class textures:
    def __init__(self):
        self.texture

class model:
    def __init__(self):
        self.localSpace=[]
        self.absoluteSpace=[]
    

class lights:
    pass

class camera:
    pass
  


def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv

    cube=bpy.data.objects["Cube"]
    print(cube.name)

if __name__ == '__main__':
    main()