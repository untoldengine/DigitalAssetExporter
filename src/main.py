'''
Created on Sep 25, 2014

@author: haroldserrano
'''
import bpy
import mathutils
import operator
import copy
from math import radians


class PointLights:
    def __init__(self):
        self.name=None
        self.falloffDistance=None
        self.energy=None
        self.linearAttenuation=None
        self.quadraticAttenuation=None
        self.localSpace=[]
        self.color=[]
        
    def unloadPointLightData(self):
        
        print("<falloff_distance>%f</falloff_distance>"%self.falloffDistance)
        print("<energy>%f</energy>"%self.energy)
        print("<linear_attenuation>%f</linear_attenuation>"%self.linearAttenuation)
        print("<quadratic_attenuation>%f</quadratic_attenuation>"%self.quadraticAttenuation)
        
        print("<light_color>",end="")
        for s in self.color:
            print("%f %f %f 1.0"%tuple(s),end="")
        print("</light_color>") 
        
        print("<local_matrix>",end="")
        for m in self.localSpace:
            print("%f %f %f %f "%tuple(m.row[0]),end="")
            print("%f %f %f %f "%tuple(m.row[1]),end="")
            print("%f %f %f %f "%tuple(m.row[2]),end="")
            print("%f %f %f %f"%tuple(m.row[3]),end="")
        print("</local_matrix>")
        
        
    
class Animation:
    def __init__(self):
        self.name=None
        self.keyframes=[]
        self.fps=None
    
class Keyframe:
    def __init__(self):
        self.time=None
        self.animationBonePoses=[]

class AnimationBonePoses:
    def __init__(self):
        self.name=None
        self.pose=[]    
    
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
        self.animations=[]
        self.hasAnimation=False
        self.world=world
        self.bindShapeMatrix=[]
        self.accumulatedParentMatrix=[]
        self.listOfParents=[]
        
    def getListOfParents(self,bone):
        
        if(bone.parent==None):
            #self.listOfParents.append(bone.name)
            return 1
        else:
            self.listOfParents.append(bone.parent)
            self.getListOfParents(bone.parent)
        
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
                bone.localMatrix=bones.matrix_local
                #set absolute matrix
                bone.absoluteMatrix=bone.localMatrix
                #set bind pose
                bone.bindPoseMatrix=bone.absoluteMatrix
                #set inverse bind pose
                bone.inverseBindPoseMatrix=bones.matrix_local.inverted()
                
                
            else:
                
                #clear the list
                self.listOfParents.clear()
                self.accumulatedParentMatrix=mathutils.Matrix.Identity(4)
                #set bone parent
                bone.parent=bones.parent.name
                #set local matrix
                bone.localMatrix=bones.matrix_local
                #set absolute matrix
                
                self.getListOfParents(bones)
                self.listOfParents.reverse()
                
                #the following for loops gets the right pose matrix for each parent of the current bone.
                #here is a pseudo example of what is happening
                #if(k==1): //bone 1..not root bone
                  #  bone.absoluteMatrix=bones.parent.matrix_local.inverted()*bones.matrix_local
                    
                    
                 #   grandPapMatrix=bones.parent.matrix_local.inverted()*bones.matrix_local
                    
                #if(k==2): //bone 2
                #    bone.absoluteMatrix=grandPapMatrix.inverted()*bones.matrix_local
                
                for parentBones in self.listOfParents:
                    
                    self.accumulatedParentMatrix=self.accumulatedParentMatrix*parentBones.matrix_local
                    
                    self.accumulatedParentMatrix=self.accumulatedParentMatrix.inverted()
                    
                
                bone.absoluteMatrix=self.accumulatedParentMatrix*bones.matrix_local
                
                #set bind pose
                bone.bindPoseMatrix=bone.absoluteMatrix
                #set bind pose inverse
                bone.inverseBindPoseMatrix=bones.matrix_local.inverted()
                
            #look for the vertex group
            bone.index=self.vertexGroupDict[bone.name]
            
            #get vertex weights for bone            
            for i in range(0,len(self.vertexGroupWeight),self.numberOfBones):
                
                bone.vertexWeights.append(self.vertexGroupWeight[bone.index+i])
                
            #append matrix data to list
            bone.localMatrixList.append(copy.copy(bone.localMatrix))
            bone.bindPoseMatrixList.append(copy.copy(bone.bindPoseMatrix))
            bone.inverseBindPoseMatrixList.append(copy.copy(bone.inverseBindPoseMatrix))
            
            #attach bone to armature class
            
            self.bones.append(bone)

    def unloadBones(self):
        
        print("<armature>",end="")
        print()
        print("<bind_shape_matrix>",end="")
        for m in self.bindShapeMatrix:
            print("%f %f %f %f "%tuple(m.row[0]),end="")
            print("%f %f %f %f "%tuple(m.row[1]),end="")
            print("%f %f %f %f "%tuple(m.row[2]),end="")
            print("%f %f %f %f"%tuple(m.row[3]),end="")
        print("</bind_shape_matrix>")
        
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
    
    def frameToTime(self,frame):
        fps=bpy.context.scene.render.fps
        rawTime=frame/fps
        return round(rawTime,3)
        
        
    def setAnimations(self):
        
        actions=bpy.data.actions
        
        scene=bpy.context.scene
        
        if(len(actions)>0):
            
            self.hasAnimation=True
            
            for action in actions:
                #create an animation object
                
                animation=Animation()
                animation.name=action.name
                animation.fps=bpy.context.scene.render.fps
                
                #create a keyframe dictionary needed to store and then sort the keyframes
                keyframeDict={}
                
                
                for fcurves in action.fcurves:
                    for keyframe in fcurves.keyframe_points:
                        
                        #check if the keyframe exist
                        if(keyframeDict.get(keyframe.co[0]) is None):
                        
                            keyframeDict[keyframe.co[0]]=keyframe.co[0]
                
                #sort the dictionary
                sortedKeyframes=sorted(keyframeDict.items(),key=operator.itemgetter(0))
                
                #get keyframes in sorted ascending order
                for keyframes in sortedKeyframes:
                    
                    #for each keyframe, create an object
                    keyframe=Keyframe()
                    #set the keyframe time
                    keyframe.time=self.frameToTime(keyframes[1])
                    
                    #set the scene to the keyframe
                    scene.frame_set(keyframes[1])
                    #update the scene
                    
                    #get the pose for each bone at that timeline
                    for bones in self.childrenBones:
                        
                        animationBonePose=AnimationBonePoses()
                        animationBonePose.name=bones.name
                        
                         
                        if(bones.parent==None):
                            animationBonePose.pose.append(copy.copy(self.armatureObject.pose.bones[bones.name].matrix))
                            
                        else:
                            animationBonePose.pose.append(copy.copy(self.armatureObject.pose.bones[bones.name].parent.matrix.inverted()*self.armatureObject.pose.bones[bones.name].matrix))
                        
                        keyframe.animationBonePoses.append(animationBonePose)
                        
                    
                    #append the keyframes to the animation
                    animation.keyframes.append(keyframe)
                
                #append the animation to the armature
                self.animations.append(animation)    
                    
    
    def unloadAnimations(self):
        
        if(self.hasAnimation is True):
            
            print("<animations>")
            for animation in self.animations:
                #print animations
                print("<animation name=\"%s\" fps=\"%f\">"%(animation.name,animation.fps))
                
                for keyframe in animation.keyframes:
                    
                    #print keyframe time
                    print("<keyframe time=\"%f\">"%keyframe.time)
                    
                    for bonePoses in keyframe.animationBonePoses:
                        
                        #print bone poses
                        print("<pose_matrix name=\"%s\">"%bonePoses.name,end="")
                        
                        for m in bonePoses.pose:
                            print("%f %f %f %f "%tuple(m.row[0]),end="")
                            print("%f %f %f %f "%tuple(m.row[1]),end="")
                            print("%f %f %f %f "%tuple(m.row[2]),end="")
                            print("%f %f %f %f"%tuple(m.row[3]),end="")
                        
                        print("</pose_matrix>")
                        
                    print("</keyframe>")
                
                print("</animation>")
            print("</animations>")             
            

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

class ConvexHull:
    def __init__(self):
        self.vertices=[]
        
    def unloadConvexHull(self):
        print("<convexHull>",end="")
            
        for i in range(0,len(self.vertices)):
            
            print("%f %f %f "%tuple(self.vertices[i]),end="")   
                
        print("</convexHull>")

class Textures:
    def __init__(self):
        self.texture=''

class Model:
    def __init__(self,world):
        self.name=''
        self.vertexCount=''
        self.indexCount=''
        self.hasUV=False
        self.hasMaterials=False
        self.hasArmature=False
        self.hasAnimation=False
        self.coordinates=Coordinates()
        self.convexHull=ConvexHull()
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
        self.unloadAnimations()
        self.unloadConvexHull()
    
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
        
    def unloadAnimations(self):
        
        if(self.hasArmature):
            if(self.armature.hasAnimation):
                self.armature.unloadAnimations()
                
    def unloadConvexHull(self):
        self.convexHull.unloadConvexHull()
        
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
        world=World()
        #convert world to opengl coords
        world.localMatrix=mathutils.Matrix.Identity(4)
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.localMatrix*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.localMatrix*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        
        self.world=world
        
        #get all models in the scene
        for models in scene.objects:
            
            if(models.type=="MESH"):
                
                model=Model(world)
                
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
                    
                    modelArmature=Armature(world)
    
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
                    
                #get the convex hull
                for hull in model.coordinates.vertices[0:8]:
                
                    model.convexHull.vertices.append(hull)
                    
                    
                self.modelList.append(model)
                
    
    def loadPointLights(self):
        
        scene=bpy.context.scene
        
         #get all lights in the scene
        for lights in scene.objects:
            
            if(lights.type=="LAMP"):
                
                light=PointLights()
                
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
    
def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv
    #set scene to frame zero
    scene=bpy.context.scene
    scene.frame_set(0)
    
    loader=Loader()
    loader.loadModel()
    loader.loadPointLights()
    
    loader.unloadData()
    

if __name__ == '__main__':
    main()