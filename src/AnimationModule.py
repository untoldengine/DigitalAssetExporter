'''
Created on Jul 18, 2016

@author: haroldserrano
'''

import bpy
import mathutils
import operator
import copy

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
            
