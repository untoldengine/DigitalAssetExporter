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
                
                
                for vertices in scene.objects[model.name].data.vertices:
                    
                    #get vertices of model
                    print(vertices.co)
                    
                    #get normal of model
                
                    print(vertices.normal)
                    
                
                for uvCoordinates in scene.objects[model.name].data.uv_layers.active.data:
                    
                    #get uv coordinates of model                    
                    print(uvCoordinates.uv)
                
                #get index of model
                for indices in scene.objects[model.name].data.loops:
                    print(indices.vertex_index)

                
                materials=scene.objects[model.name].active_material
                    
                #get diffuse color
                diffuse_color=materials.diffuse_color
                print(diffuse_color)
                
                #get specular color
                specular_color=materials.specular_color
                print(specular_color)
                
                #get texture name
                texture=scene.objects[model.name].data.uv_textures.active.data[0].image.name
                
                print(texture)
                
                #get local matrix
                
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