'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy
import sys
sys.path.append(r'/Users/haroldserrano/Documents/workspace/DALBlenderScript/src/')  # Absolute path
import LoaderModule

def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv
    #set scene to frame zero
    scene=bpy.context.scene
    scene.frame_set(0)
    
    loader=LoaderModule.Loader()
    loader.loadModel()
    loader.loadPointLights()
    
    loader.unloadData()
    

if __name__ == '__main__':
    main()