'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy

class Materials:
    def __init__(self):
        self.diffuse=[]
        self.specular=[]
        
    
class Coordinates:
    def __init__(self):
        self.vertices=[]
        self.normal=[]
        self.uv=[]
        self.index=[]


class Textures:
    def __init__(self):
        self.texture=''

class Model:
    def __init__(self):
        self.name=''
        self.coordinates=Coordinates()
        self.materials=Materials()
        self.texture=Textures()
        self.localSpace=[]
        self.absoluteSpace=[]    

    def getData(self):
        pass
    
    def setData(self):
        pass
    
    
class Lights:
    pass

class Camera:
    pass
  
class Loader:
    def __init__(self):
        self.modelList=[]
    
    def start(self):
        
        self.loadModel()
        self.loadLights()
        self.loadCamera()
        
    def writeToFile(self):
        self.unloadModel()
        self.unloadLights()
        self.unloadCamera()
    
    def loadModel(self):
        
        scene=bpy.context.scene
        
        for models in scene.objects:
            
            if(models.type=="MESH"):
                
                model=Model()
                
                #get name of model
                model.name=models.name
                
                #get vertices of model
                for vertices in scene.objects[model.name].data.vertices:
                    print(vertices.co)
                    
                #get normal of model
                
                    print(vertices.normal)
                    
                #get uv coordinates of model
                
                for uvCoordinates in scene.objects[model.name].data.uv_layers.active.data:
                    
                    print(uvCoordinates.uv)
                
                #get index of model
                
                self.modelList.append(model)
                
                
    def loadLights(self):
        pass
    
    def loadCamera(self):
        pass

    def unloadModel(self):
        pass
    def unloadLights(self):
        pass
    
    def unloadCamera(self):
        pass
    
def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv

    loader=Loader()
    loader.loadModel()

if __name__ == '__main__':
    main()