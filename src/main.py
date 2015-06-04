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
        
    def unloadPointLightData(self,file):
        
        file.write("<falloff_distance>%f</falloff_distance>\n"%self.falloffDistance)
        file.write("<energy>%f</energy>\n"%self.energy)
        file.write("<linear_attenuation>%f</linear_attenuation>\n"%self.linearAttenuation)
        file.write("<quadratic_attenuation>%f</quadratic_attenuation>\n"%self.quadraticAttenuation)
        
        file.write("<light_color>")
        for s in self.color:
            file.write("%f %f %f 1.0"%tuple(s))
        file.write("</light_color>\n") 
        
        file.write("<local_matrix>")
        for m in self.localSpace:
            file.write("%f %f %f %f "%tuple(m.row[0]))
            file.write("%f %f %f %f "%tuple(m.row[1]))
            file.write("%f %f %f %f "%tuple(m.row[2]))
            file.write("%f %f %f %f"%tuple(m.row[3]))
        file.write("</local_matrix>\n")
        
        
    
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

    def unloadBones(self,file):
        
        file.write("<armature>")
        file.write("\n")
        file.write("<bind_shape_matrix>")
        for m in self.bindShapeMatrix:
            file.write("%f %f %f %f "%tuple(m.row[0]))
            file.write("%f %f %f %f "%tuple(m.row[1]))
            file.write("%f %f %f %f "%tuple(m.row[2]))
            file.write("%f %f %f %f"%tuple(m.row[3]))
        file.write("</bind_shape_matrix>\n")
        
        for bone in self.bones:
            file.write("\n")
            file.write("<bone name=\"%s\" parent=\"%s\">\n"%(bone.name,bone.parent))
            file.write("<local_matrix>")
            for m in bone.localMatrixList:
                file.write("%f %f %f %f "%tuple(m.row[0]))
                file.write("%f %f %f %f "%tuple(m.row[1]))
                file.write("%f %f %f %f "%tuple(m.row[2]))
                file.write("%f %f %f %f"%tuple(m.row[3]))
            file.write("</local_matrix>\n")
            
            file.write("<bind_pose_matrix>")
            for m in bone.bindPoseMatrixList:
                file.write("%f %f %f %f "%tuple(m.row[0]))
                file.write("%f %f %f %f "%tuple(m.row[1]))
                file.write("%f %f %f %f "%tuple(m.row[2]))
                file.write("%f %f %f %f"%tuple(m.row[3]))
            
            file.write("</bind_pose_matrix>\n")
            
            file.write("<inverse_bind_pose_matrix>")
            for m in bone.inverseBindPoseMatrixList:
                file.write("%f %f %f %f "%tuple(m.row[0]))
                file.write("%f %f %f %f "%tuple(m.row[1]))
                file.write("%f %f %f %f "%tuple(m.row[2]))
                file.write("%f %f %f %f"%tuple(m.row[3]))
                
            file.write("</inverse_bind_pose_matrix>\n")
            
            file.write("<rest_pose_matrix>")
            for m in bone.restPoseMatrixList:
                file.write("%f %f %f %f "%tuple(m.row[0]))
                file.write("%f %f %f %f "%tuple(m.row[1]))
                file.write("%f %f %f %f "%tuple(m.row[2]))
                file.write("%f %f %f %f"%tuple(m.row[3]))
                
            file.write("</rest_pose_matrix>\n")
            
            file.write("<vertex_weights>")
            for vw in bone.vertexWeights:
                file.write("%f "%vw)
            file.write("</vertex_weights>\n")
            
            file.write("</bone>\n")
        
        
        file.write("</armature>\n")
        
        file.write("\n")
    
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
                    
    
    def unloadAnimations(self,file):
        
        if(self.hasAnimation is True):
            
            file.write("<animations>\n")
            for animation in self.animations:
                #print animations
                file.write("<animation name=\"%s\" fps=\"%f\">\n"%(animation.name,animation.fps))
                
                for keyframe in animation.keyframes:
                    
                    #print keyframe time
                    file.write("<keyframe time=\"%f\">\n"%keyframe.time)
                    
                    for bonePoses in keyframe.animationBonePoses:
                        
                        #print bone poses
                        file.write("<pose_matrix name=\"%s\">"%bonePoses.name)
                        
                        for m in bonePoses.pose:
                            file.write("%f %f %f %f "%tuple(m.row[0]))
                            file.write("%f %f %f %f "%tuple(m.row[1]))
                            file.write("%f %f %f %f "%tuple(m.row[2]))
                            file.write("%f %f %f %f"%tuple(m.row[3]))
                        
                        file.write("</pose_matrix>\n")
                        
                    file.write("</keyframe>\n")
                
                file.write("</animation>\n")
            file.write("</animations>\n")             
            

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
        self.vertexCount=''
        self.indexCount=''
        self.hasUV=False
        self.hasMaterials=False
        self.hasArmature=False
        self.hasAnimation=False
        self.coordinates=Coordinates()
        self.materials=Materials()
        self.texture=Textures()
        self.localSpace=[]
        self.absoluteSpace=[]
        self.armature=None
        self.vertexGroupWeight=[] 
        self.vertexGroupDict={}   
        self.worldMatrix=world
        
    def unloadModelData(self,file):
        
        self.unloadCoordinates(file)
        self.unloadMaterials(file)
        self.unloadTexture(file)
        self.unloadLocalSpace(file)
        self.unloadArmature(file)
        self.unloadAnimations(file)
    
    def unloadCoordinates(self,file):
                
        file.write("<vertices>")
            
        for i in range(0,len(self.coordinates.vertices)):
            
            file.write("%f %f %f "%tuple(self.coordinates.vertices[i]))   
                
        file.write("</vertices>\n")
        
        file.write("\n")
        
        file.write("<normal>")
        
        for i in range(0,len(self.coordinates.normal)):
            
            file.write("%f %f %f "%tuple(self.coordinates.normal[i]))
                     
        file.write("</normal>\n")
        
        file.write("\n")
            
        if(self.hasUV):
            
            file.write("<uv>")
        
            for i in range(0,len(self.coordinates.uv)):
                
                file.write("%f %f "%tuple(self.coordinates.uv[i]))
                   
            file.write("</uv>\n")
            
            file.write("\n") 
    
        file.write("<index>")
        
        for i in self.coordinates.index:
            file.write("%d "%i)
        
        file.write("</index>\n")
        
        file.write("\n")
        
    def unloadMaterials(self,file):
        
        if(self.hasMaterials):
            file.write("<diffuse_color>")
            for d in self.materials.diffuse:
                file.write("%f %f %f 1.0" %tuple(d))  
            file.write("</diffuse_color>\n")    
                
            file.write("<specular_color>")
            for s in self.materials.specular:
                file.write("%f %f %f 1.0"%tuple(s))
            file.write("</specular_color>\n")    
            
            file.write("<ambient_color>")    
            file.write("0.0 0.0 0.0 1.0")
            file.write("</ambient_color>\n") 
            
            file.write("<emission_color>")
            file.write("0.0 0.0 0.0 1.0")
            file.write("</emission_color>\n") 
            
            file.write("<shininess>")
            file.write("%f"%self.materials.shininess)
            file.write("</shininess>\n")
            file.write("\n")
            
    def unloadTexture(self,file):
        
        if(self.hasUV):
            file.write("<texture_image>%s</texture_image>\n"%self.texture)
            
            file.write("\n")
    
    def unloadLocalSpace(self,file):
        
        file.write("<local_matrix>")
        for m in self.localSpace:
            file.write("%f %f %f %f "%tuple(m.row[0]))
            file.write("%f %f %f %f "%tuple(m.row[1]))
            file.write("%f %f %f %f "%tuple(m.row[2]))
            file.write("%f %f %f %f"%tuple(m.row[3]))
        file.write("</local_matrix>\n")
        
        file.write("\n")
        
    def unloadArmature(self,file):
        
        if(self.hasArmature):
            self.armature.unloadBones(file)
    
    def setArmature(self):
        self.armature.setRootBone()
        
    def unloadAnimations(self,file):
        
        if(self.hasArmature):
            if(self.armature.hasAnimation):
                self.armature.unloadAnimations(file)
        
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

    def unloadData(self,file):
        
        file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        file.write("<UntoldEngine xmlns=\"\" version=\"0.0.1\">\n")
        
        file.write("<asset>\n")
        
        self.unloadModel(file)
        self.unloadPointLights(file)
        
        file.write("</asset>\n")
        
        file.write("</UntoldEngine>\n")
        
        
    def unloadModel(self,file):
        
        file.write("<meshes>\n")
        
        for model in self.modelList:
            
            file.write("<mesh name=\"%s\" vertex_count=\"%d\" index_count=\"%d\">\n"%(model.name,len(model.coordinates.vertices),len(model.coordinates.index)))
            
            model.unloadModelData(file)
            
            file.write("</mesh>\n")                                 
            
            file.write("\n")
        
        file.write("</meshes>\n")
        
        file.write("\n")
        
    def unloadPointLights(self,file):
        
        file.write("<point_lights>\n")
        for lights in self.pointLightsList:
            file.write("\n")
            file.write("<point_light name=\"%s\">\n"%lights.name)
            
            lights.unloadPointLightData(file)
            
            file.write("</point_light>\n")
            file.write("\n")
        file.write("</point_lights>\n")
        
        file.write("\n")
    def unloadCamera(self):
        pass
    
def main():

#bpy.context.scene.objects['Cube'].data.uv_layers.active.data[0].uv
    #set scene to frame zero
    scene=bpy.context.scene
    scene.frame_set(0)
    
    outfile=open('/Users/haroldserrano/Desktop/new.txt','w')
    
    loader=Loader()
    loader.loadModel()
    loader.loadPointLights()
    
    loader.unloadData(outfile)
    

if __name__ == '__main__':
    main()