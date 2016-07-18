'''
Created on Jul 18, 2016

@author: haroldserrano
'''
import bpy
import mathutils
from math import radians
import SceneModule
import ModelModule
import LightsModule
import AnimationModule


class Loader:
    def __init__(self):
        self.modelList=[]
        self.pointLightsList=[]
        self.cameraList=[]
        self.world=None
        
    def r3d(self,v):
        return round(v[0],6), round(v[1],6), round(v[2],6)


    def r2d(self,v):
        return round(v[0],6), round(v[1],6)
    
    
    def start(self):
        
        self.loadModel()
        self.loadPointLights()
        self.loadCamera()
        
    def writeToFile(self):
        self.unloadModel()
        self.unloadPointLights()
        self.unloadCamera()
    
    def loadModel(self):
        
        scene=bpy.context.scene
        
        #get world matrix
        world=SceneModule.World()
        #convert world to opengl coords
        world.localMatrix=mathutils.Matrix.Identity(4)
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.localMatrix*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        
        self.world=world
        
        #get all models in the scene
        for models in scene.objects:
            
            if(models.type=="MESH"):
                
                model=ModelModule.Model(world)
                
                #get name of model
                model.name=models.name
                
                #get local matrix
                matrix_local=world.localMatrix*scene.objects[model.name].matrix_local
                
                model.localSpace.append(matrix_local)
                
                #get absolute matrix
                model.absoluteSpace.append(scene.objects[model.name].matrix_world)
                
                 #get index of model
                for i,indices in enumerate(scene.objects[model.name].data.loops):
                    
                    #get vertices of model
                    
                    vertex=scene.objects[model.name].data.vertices[indices.vertex_index].co
                    
                    #convert vertex to openGL coordinate
                    vertex=scene.objects[model.name].matrix_local*vertex                
                    
                    vertex=self.r3d(vertex)
                    
                    model.coordinates.vertices.append(vertex)
                    
                    #get normal of model
                    
                    normal=scene.objects[model.name].data.vertices[indices.vertex_index].normal
                    
                    #convert normal to OpenGL coordinate
                    normal=scene.objects[model.name].matrix_local*normal
                    
                    normal=self.r3d(normal)
                    
                    model.coordinates.normal.append(normal)
                    
                    #get vertex weight
                    
                    vertexGroupWeightDict={}  #create a dictionary for the weights
                    
                    for vertexGroup in scene.objects[model.name].data.vertices[indices.vertex_index].groups:
                        
                        vertexGroupWeightDict[vertexGroup.group]=vertexGroup.weight
                        
                    model.vertexGroupWeight.append(vertexGroupWeightDict)
                        
                    #get the index
                    model.coordinates.index.append(i)
                
                if(scene.objects[model.name].data.uv_layers):
                    for uvCoordinates in scene.objects[model.name].data.uv_layers.active.data:
                        
                        #get uv coordinates of model                    
    
                        model.coordinates.uv.append(self.r2d(uvCoordinates.uv))
                        model.hasUV=True
                    
                #check if model has materials
                
                if(scene.objects[model.name].active_material):
                
                    model.hasMaterials=True
                    
                    materials=scene.objects[model.name].active_material
                        
                    #get diffuse color
                    diffuse_color=materials.diffuse_color
                    
                    model.materials.diffuse.append(diffuse_color)
                    
                    #get specular color
                    specular_color=materials.specular_color
    
                    model.materials.specular.append(specular_color)
    
                    #get shininess of material
                    shininess=materials.specular_hardness
                    
                    model.materials.shininess=shininess
                
                
                #get texture name
                if(model.hasUV):
                    
                    texture=scene.objects[model.name].data.uv_textures.active.data[0].image.name
                    
                    model.texture=texture
                
                #get all the vertex groups affecting the object
                for vertexGroups in scene.objects[model.name].vertex_groups:
                    model.vertexGroupDict[vertexGroups.name]=vertexGroups.index
                    
                
                #check if model has armature
                armature=models.find_armature()
            
                if(armature!=None):
                
                    model.hasArmature=True
                    
                    modelArmature=AnimationModule.Armature(world)
    
                    modelArmature.armatureObject=armature
                    
                    model.armature=modelArmature
                    
                    #set name
                    model.armature.name=armature.name
                    
                    #set Bind Shape Matrix
                    model.armature.bindShapeMatrix.append(scene.objects[model.name].matrix_world)
                    
                    #copy the vertex group from the model to the armature
                    
                    #go throught the vertexGroupWeight, get the dictionary
                    # and fill in with zero any vertex group that does not exist
                    # then append the data to model.armature.vertexGroupWeight
                    
                    for n in model.vertexGroupWeight:
                        for j in range(0,len(model.vertexGroupDict)):
                            if(n.get(j) is None):
                                model.armature.vertexGroupWeight.append(0.0)
                            else:
                                model.armature.vertexGroupWeight.append(n.get(j))
                                
                    
                    #copy vertex group dictionary
                    model.armature.vertexGroupDict=model.vertexGroupDict
                    
                    model.armature.setAllBones()
                    
                    model.armature.loadBonesInfo()
                    
                    model.armature.setAnimations()
                
                #get dimension of object
                model.dimension.append(scene.objects[model.name].dimensions)        
                    
                self.modelList.append(model)
                
    
    def loadPointLights(self):
        
        scene=bpy.context.scene
        
         #get all lights in the scene
        for lights in scene.objects:
            
            if(lights.type=="LAMP"):
                
                light=LightsModule.PointLights()
                
                light.name=lights.name
                
                #light color
                light.color.append(scene.objects[light.name].data.color)
                
                #Light energy
                light.energy=scene.objects[light.name].data.energy
                
                #light fall off distance
                light.falloffDistance=scene.objects[light.name].data.distance
                
                #light linear attenuation
                light.linearAttenuation=scene.objects[light.name].data.linear_attenuation
                
                #light quadratic attenuation
                light.quadraticAttenuation=scene.objects[light.name].data.quadratic_attenuation
                
                #light local space
                light.localSpace.append(self.world.localMatrix*scene.objects[light.name].matrix_local)
                
                #append the lights to the list
                self.pointLightsList.append(light)
    
    def loadCamera(self):
        pass

    def unloadData(self):
        
        print("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        print("<UntoldEngine xmlns=\"\" version=\"0.0.1\">")
        
        print("<asset>")
        
        self.unloadModel()
        self.unloadPointLights()
        
        print("</asset>")
        
        print("</UntoldEngine>")
        
        
    def unloadModel(self):
        
        print("<meshes>")
        
        for model in self.modelList:
            
            print("<mesh name=\"%s\" vertex_count=\"%d\" index_count=\"%d\">"%(model.name,len(model.coordinates.vertices),len(model.coordinates.index)))
            
            model.unloadModelData()
            
            print("</mesh>")                                 
            
            print()
        
        print("</meshes>")
        print()
        
    def unloadPointLights(self):
        
        print("<point_lights>")
        for lights in self.pointLightsList:
            print()
            print("<point_light name=\"%s\">"%lights.name)
            
            lights.unloadPointLightData()
            
            print("</point_light>")
            print()
        print("</point_lights>")
        
        print()
    def unloadCamera(self):
        pass
    