'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy
import mathutils
from math import radians

class Bone:
    def __init__(self):
        self.name=None
        self.parent=None
        self.boneObject=None
        self.vertexGroupIndex=None
        self.localMatrix=None
        self.absoluteMatrix=None
        self.inverseBindPoseMatrix=None
        self.bindPoseMatrix=None
        self.restPoseMatrix=None
        self.vertexWeights=[]
        self.localMatrixList=[]
        self.inverseBindPoseMatrixList=[]
        self.bindPoseMatrixList=[]
        self.restPoseMatrixList=[]
        self.index=None
        
    
class Armature:
    def __init__(self,world):
        self.name=None
        self.armatureObject=None
        self.absoluteMatrix=None
        self.localMatrix=None
        self.rootBone=None
        self.childrenBones=[]
        self.vertexGroupWeight=[]
        self.vertexGroupDict={}
        self.numberOfBones=None
        self.bones=[]
        self.world=world
        
    def setAllBones(self):
        
        rootBone=self.armatureObject.data.bones[0]
        
        self.childrenBones.append(rootBone)
        
        self.loadChildrenBones(rootBone)

        
    def loadChildrenBones(self,bone):
        
        for children in bone.children:    
            
            self.childrenBones.append(children)
            
            self.loadChildrenBones(children)
            
    def loadBonesInfo(self):
        
        #get total count of bones
        self.numberOfBones=len(self.childrenBones)
        
        #get the armature absolute matrix
        self.absoluteMatrix=self.armatureObject.matrix_world
        
        for bones in self.childrenBones:
            
            bone=Bone()
            
            #get bone name
            bone.name=bones.name
            
            #get bone local matrix
            
            if(bones.parent==None):
                #set bone parent
                bone.parent='root'
                #set local matrix
                bone.localMatrix=self.world.localMatrix*self.absoluteMatrix*bones.matrix_local
                #set absolute matrix
                bone.absoluteMatrix=bone.localMatrix
                #set bind pose
                bone.bindPoseMatrix=bone.absoluteMatrix
                #set inverse bind pose
                bone.inverseBindPoseMatrix=bone.bindPoseMatrix.inverted()
                #get rest pose matrix
                bone.restPoseMatrix=self.armatureObject.pose.bones[bone.name].matrix
                
                
            else:
                #set bone parent
                bone.parent=bones.parent.name
                #set local matrix
                bone.localMatrix=self.world.localMatrix*self.absoluteMatrix*bones.matrix_local
                #set absolute matrix
                bone.absoluteMatrix=bones.parent.matrix_local.inverted()*bone.localMatrix
                #set bind pose
                bone.bindPoseMatrix=bone.absoluteMatrix
                #set bind pose inverse
                bone.inverseBindPoseMatrix=bone.bindPoseMatrix.inverted()
                #get rest pose matrix
                bone.restPoseMatrix=self.armatureObject.pose.bones[bone.name].parent.matrix.inverted()*self.armatureObject.pose.bones[bone.name].matrix
                        
                        
            #look for the vertex group
            bone.index=self.vertexGroupDict[bone.name]
            
            #get vertex weights for bone            
            for i in range(0,len(self.vertexGroupWeight),self.numberOfBones):
                
                bone.vertexWeights.append(self.vertexGroupWeight[bone.index+i])
                
            #append matrix data to list
            bone.localMatrixList.append(bone.localMatrix)
            bone.bindPoseMatrixList.append(bone.bindPoseMatrix)
            bone.inverseBindPoseMatrixList.append(bone.inverseBindPoseMatrix)
            bone.restPoseMatrixList.append(self.world.localMatrix*self.absoluteMatrix*bone.restPoseMatrix)
              
            #attach bone to armature class
            
            self.bones.append(bone)

    def unloadBones(self):
        
        print("<armature>",end="")
        
        for bone in self.bones:
            print()
            print("<bone name=\"%s\" parent=\"%s\">"%(bone.name,bone.parent))
            print("<local_matrix>",end="")
            for m in bone.localMatrixList:
                print("%f %f %f %f "%tuple(m.row[0]),end="")
                print("%f %f %f %f "%tuple(m.row[1]),end="")
                print("%f %f %f %f "%tuple(m.row[2]),end="")
                print("%f %f %f %f"%tuple(m.row[3]),end="")
            print("</local_matrix>")
            
            print("<bind_pose_matrix>",end="")
            for m in bone.bindPoseMatrixList:
                print("%f %f %f %f "%tuple(m.row[0]),end="")
                print("%f %f %f %f "%tuple(m.row[1]),end="")
                print("%f %f %f %f "%tuple(m.row[2]),end="")
                print("%f %f %f %f"%tuple(m.row[3]),end="")
            
            print("</bind_pose_matrix>")
            
            print("<inverse_bind_pose_matrix>",end="")
            for m in bone.inverseBindPoseMatrixList:
                print("%f %f %f %f "%tuple(m.row[0]),end="")
                print("%f %f %f %f "%tuple(m.row[1]),end="")
                print("%f %f %f %f "%tuple(m.row[2]),end="")
                print("%f %f %f %f"%tuple(m.row[3]),end="")
                
            print("</inverse_bind_pose_matrix>")
            
            print("<rest_pose_matrix>",end="")
            for m in bone.restPoseMatrixList:
                print("%f %f %f %f "%tuple(m.row[0]),end="")
                print("%f %f %f %f "%tuple(m.row[1]),end="")
                print("%f %f %f %f "%tuple(m.row[2]),end="")
                print("%f %f %f %f"%tuple(m.row[3]),end="")
                
            print("</rest_pose_matrix>")
            
            print("<vertex_weights>",end="")
            for vw in bone.vertexWeights:
                print("%f "%vw,end="")
            print("</vertex_weights>")
            
            print("</bone>")
        
        
        print("</armature>")
        
        print()

class Materials:
    def __init__(self):
        self.diffuse=[]
        self.specular=[]
        self.shininess=0.0
    
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
    def __init__(self,world):
        self.name=''
        self.hasUV=False
        self.hasMaterials=False
        self.hasArmature=False
        self.coordinates=Coordinates()
        self.materials=Materials()
        self.texture=Textures()
        self.localSpace=[]
        self.absoluteSpace=[]
        self.armature=None
        self.vertexGroupWeight=[] 
        self.vertexGroupDict={}   
        self.worldMatrix=world
        
    def unloadModelData(self):
        
        self.unloadCoordinates()
        self.unloadMaterials()
        self.unloadTexture()
        self.unloadLocalSpace()
        self.unloadArmature()
    
    def unloadCoordinates(self):
        
        print("<vertices>",end="")
            
        for i in range(0,len(self.coordinates.vertices)):
            
            print("%f %f %f "%tuple(self.coordinates.vertices[i]),end="")   
                
        print("</vertices>")
        
        print()
        
        print("<normal>",end="")
        
        for i in range(0,len(self.coordinates.normal)):
            
            print("%f %f %f "%tuple(self.coordinates.normal[i]),end="")
                     
        print("</normal>")
        
        print()
            
        if(self.hasUV):
            
            print("<uv>",end="")
        
            for i in range(0,len(self.coordinates.uv)):
                
                print("%f %f "%tuple(self.coordinates.uv[i]),end="")
                   
            print("</uv>")
            
            print() 
    
        print("<index>",end="")
        
        for i in self.coordinates.index:
            print("%d "%i,end="")
        
        print("</index>")
        
        print()
        
    def unloadMaterials(self):
        
        if(self.hasMaterials):
            print("<diffuse_color>",end="")
            for d in self.materials.diffuse:
                print("%f %f %f 1.0" %tuple(d),end="")  
            print("</diffuse_color>")    
                
            print("<specular_color>",end="")
            for s in self.materials.specular:
                print("%f %f %f 1.0"%tuple(s),end="")
            print("</specular_color>")    
            
            print("<ambient_color>",end="")    
            print("0.0 0.0 0.0 1.0",end="")
            print("</ambient_color>") 
            
            print("<emission_color>",end="")
            print("0.0 0.0 0.0 1.0",end="")
            print("</emission_color>") 
            
            print("<shininess>",end="")
            print("%f"%self.materials.shininess,end="")
            print("</shininess>")
            print()
            
    def unloadTexture(self):
        
        if(self.hasUV):
            print("<texture_image>%s</texture_image>"%self.texture)
            
            print()
    
    def unloadLocalSpace(self):
        
        print("<local_matrix>",end="")
        for m in self.localSpace:
            print("%f %f %f %f "%tuple(m.row[0]),end="")
            print("%f %f %f %f "%tuple(m.row[1]),end="")
            print("%f %f %f %f "%tuple(m.row[2]),end="")
            print("%f %f %f %f"%tuple(m.row[3]),end="")
        print("</local_matrix>")
        
        print()
        
    def unloadArmature(self):
        
        if(self.hasArmature):
            self.armature.unloadBones()
    
    def setArmature(self):
        self.armature.setRootBone()
        
class Lights:
    pass

class Camera:
    pass

class World:
    def __init__(self):
        self.localMatrix=[]
        
  
class Loader:
    def __init__(self):
        self.modelList=[]
        
    def r3d(self,v):
        return round(v[0],6), round(v[1],6), round(v[2],6)


    def r2d(self,v):
        return round(v[0],6), round(v[1],6)
    
    
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
        
        #get world matrix
        world=World()
        world.localMatrix=mathutils.Matrix.Identity(4)
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.localMatrix*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        
        
        #get all models in the scene
        for models in scene.objects:
            
            if(models.type=="MESH"):
                
                model=Model(world)
                
                #get name of model
                model.name=models.name
                
                 #get index of model
                for i,indices in enumerate(scene.objects[model.name].data.loops):
                    
                    #get vertices of model
                    
                    vertex=scene.objects[model.name].data.vertices[indices.vertex_index].co
                    
                    #convert vertex to openGL coordinate
                    vertex=world.localMatrix*vertex                
                    
                    vertex=self.r3d(vertex)
                    
                    model.coordinates.vertices.append(vertex)
                    
                    #get normal of model
                    
                    normal=scene.objects[model.name].data.vertices[indices.vertex_index].normal
                    
                    #convert normal to OpenGL coordinate
                    normal=world.localMatrix*normal
                    
                    normal=self.r3d(normal)
                    
                    model.coordinates.normal.append(normal)
                    
                    #get vertex weight
                    
                    for vertexGroup in scene.objects[model.name].data.vertices[indices.vertex_index].groups:
                        
                        model.vertexGroupWeight.append(vertexGroup.weight)
                    
                    #get the index
                    model.coordinates.index.append(i)
                
                
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
                
                #get local matrix
                matrix_local=scene.objects[model.name].matrix_local
                
                model.localSpace.append(matrix_local)
                
                #get vertex group index and name
                #this data contains which bone affects which
                for vertexGroups in scene.objects[model.name].vertex_groups:
                    model.vertexGroupDict[vertexGroups.name]=vertexGroups.index
                    
                
                #check if model has armature
                armature=models.find_armature()
            
                if(armature!=None):
                
                    model.hasArmature=True
                    
                    modelArmature=Armature(world)
    
                    modelArmature.armatureObject=armature
                    
                    model.armature=modelArmature
                    
                    #copy the vertex group from the model to the armature
                    model.armature.vertexGroupWeight=model.vertexGroupWeight
                    
                    #copy vertex group dictionary
                    model.armature.vertexGroupDict=model.vertexGroupDict
                    
                    model.armature.setAllBones()
                    
                    model.armature.loadBonesInfo()
                    
                self.modelList.append(model)
                
    
    def loadLights(self):
        pass
    
    def loadCamera(self):
        pass

    def unloadData(self):
        
        print("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        print("<ROLDIE xmlns=\"\" version=\"0.0.1\">")
        
        print("<asset>")
        
        self.unloadModel()
        
        
        print("</asset>")
        
        print("</ROLDIE>")
        
        
    def unloadModel(self):
        
        print("<meshes>")
        
        for model in self.modelList:
            
            print("<mesh name=\"%s\">"%model.name)
            
            model.unloadModelData()
            
            print("</mesh>")                                 
            
            print()
        
        print("</meshes>")
    
    def unloadLights(self):
        pass
    
    def unloadCamera(self):
        pass
    
def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv

    loader=Loader()
    loader.loadModel()
    
    loader.unloadData()

if __name__ == '__main__':
    main()