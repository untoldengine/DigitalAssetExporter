'''
Created on Sep 25, 2014

Digital Asset Exporter script for the Untold Engine. It extracts the attributes of a 3D model.

Copyright (C) 2018  Untold Engine Studions

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

@author: Harold Serrano
'''
import bpy
import bmesh
import mathutils
import operator
import copy
from math import radians
from math import degrees

#class to write to a file

class ExportFile:
    def __init__(self, filePath):
        self.filePath=filePath
        self.fileToWrite=None
        
    def openFile(self):
        self.fileToWrite=open(self.filePath, 'w', encoding='utf-8')
        
    
    def writeData(self, dataToWrite, space=None):

        dataToWrite=str(dataToWrite)
        
        if space is None:
            self.fileToWrite.write(dataToWrite+"\n")
        else:

            self.fileToWrite.write(dataToWrite)
    
    def closeFile(self):
        self.fileToWrite.close()
        
        
        return {'FINISHED'}

class NavMeshNode:
    def __init__(self):
        self.index=None
        self.location=[]
        self.neighbours=[]

class NavMesh:
    
    def __init__(self):
        self.name=None
        self.navMeshNodes=[]


    def unloadNavMeshData(self,exportFile):


        for node in self.navMeshNodes:

            exportFile.writeData("<node index=\"%d\">"%(node.index))

            exportFile.writeData("<node_location>",' ')

            for location in node.location:
                exportFile.writeData("%f %f %f"%tuple(location),' ')

            exportFile.writeData("</node_location>")

            exportFile.writeData("<node_neighbours>",' ')

            for neighbour in node.neighbours:
                exportFile.writeData("%d "%neighbour,' ')

            exportFile.writeData("</node_neighbours>")
                        
            exportFile.writeData("</node>") 
            
        
class PointLights:
    def __init__(self):
        self.name=None
        self.energy=None
        self.localSpace=[]
        self.color=[]
        
    def unloadPointLightData(self,exportFile):
        
        exportFile.writeData("<energy>%f</energy>"%self.energy)
        
        exportFile.writeData("<light_color>",' ')
        for s in self.color:
            exportFile.writeData("%f %f %f 1.0"%tuple(s),' ')
        exportFile.writeData("</light_color>") 
        
        exportFile.writeData("<local_matrix>",' ')
        for m in self.localSpace:
            exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
            exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
        exportFile.writeData("</local_matrix>")
        
        
    
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
        self.modelerAnimationSpaceTransform=[]
        
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

    def unloadBones(self,exportFile):
        
        exportFile.writeData("<armature>",' ')
        
         
        exportFile.writeData("<bind_shape_matrix>",' ')
        for m in self.bindShapeMatrix:
            exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
            exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
        exportFile.writeData("</bind_shape_matrix>")
        
        for bone in self.bones:
             
            exportFile.writeData("<bone name=\"%s\" parent=\"%s\">"%(bone.name,bone.parent))
            exportFile.writeData("<local_matrix>",' ')
            for m in bone.localMatrixList:
                exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
            exportFile.writeData("</local_matrix>")
            
            exportFile.writeData("<bind_pose_matrix>",' ')
            for m in bone.bindPoseMatrixList:
                exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
            
            exportFile.writeData("</bind_pose_matrix>")
            
            exportFile.writeData("<inverse_bind_pose_matrix>",' ')
            for m in bone.inverseBindPoseMatrixList:
                exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
                
            exportFile.writeData("</inverse_bind_pose_matrix>")
            
            exportFile.writeData("<rest_pose_matrix>",' ')
            for m in bone.restPoseMatrixList:
                exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
                
            exportFile.writeData("</rest_pose_matrix>")
            
            exportFile.writeData("<vertex_weights weight_count=\"%d\">"%(len(bone.vertexWeights)),' ')
            for vw in bone.vertexWeights:
                exportFile.writeData("%f "%vw,' ')
            exportFile.writeData("</vertex_weights>")
            
            exportFile.writeData("</bone>")
        
        
        exportFile.writeData("</armature>")
        
         
    
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
                        
                        parentBoneSpace=mathutils.Matrix.Identity(4)
                        childBoneSpace=mathutils.Matrix.Identity(4)
                        finalBoneSpace=mathutils.Matrix.Identity(4)
                         
                        if(bones.parent==None):
                            
                            parentBoneSpace=self.armatureObject.pose.bones[bones.name].matrix*parentBoneSpace
                    
                            finalBoneSpace=parentBoneSpace
                            
                        else:
                               
                            parentBoneSpace=self.armatureObject.pose.bones[bones.name].parent.matrix.inverted()*parentBoneSpace
                            
                            childBoneSpace=self.armatureObject.pose.bones[bones.name].matrix*childBoneSpace
                            
                            childBoneSpace=parentBoneSpace*childBoneSpace
                            
                            finalBoneSpace=childBoneSpace
                            
                        
                        animationBonePose.pose.append(copy.copy(finalBoneSpace))
                            
                        keyframe.animationBonePoses.append(animationBonePose)
                        
                    
                    #append the keyframes to the animation
                    animation.keyframes.append(keyframe)
                
                #append the animation to the armature
                self.animations.append(animation)    
                    
    
    def unloadAnimations(self,exportFile):
        
        if(self.hasAnimation is True):
            
            exportFile.writeData("<animations>")
            
            exportFile.writeData("<modeler_animation_transform>",' ')
            for m in self.modelerAnimationSpaceTransform:
                exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
            exportFile.writeData("</modeler_animation_transform>")
            
             
            for animation in self.animations:
                #exportFile.writeData animations
                exportFile.writeData("<animation name=\"%s\" fps=\"%f\">"%(animation.name,animation.fps))
                
                for keyframe in animation.keyframes:
                    
                    #exportFile.writeData keyframe time
                    exportFile.writeData("<keyframe time=\"%f\">"%keyframe.time)
                    
                    for bonePoses in keyframe.animationBonePoses:
                        
                        #exportFile.writeData bone poses
                        exportFile.writeData("<pose_matrix name=\"%s\">"%bonePoses.name,' ')
                        
                        for m in bonePoses.pose:
                            exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
                            exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
                            exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
                            exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
                        
                        exportFile.writeData("</pose_matrix>")
                        
                    exportFile.writeData("</keyframe>")
                
                exportFile.writeData("</animation>")
            exportFile.writeData("</animations>")             
            

class Materials:
    def __init__(self):
        self.name=''
        self.diffuse=[]
        self.specular=[]
        self.diffuse_intensity=[]
        self.specular_intensity=[] 
        self.specular_hardness=[]  
    
class Coordinates:
    def __init__(self):
        self.vertices=[]
        self.normal=[]
        self.uv=[]
        self.index=[]

class Faces:
    def __init__(self):
        self.vertices=[]
        self.edgesIndex=[]
        self.facesIndex=[]

class Textures:
    def __init__(self):
        self.texture=''

class Model:
    def __init__(self,world):
        self.name=''
        self.vertexCount=''
        self.indexCount=''
        self.dimension=[]
        self.hasUV=False
        self.hasTexture=False
        self.hasMaterials=False
        self.hasArmature=False
        self.hasAnimation=False
        self.coordinates=Coordinates()
        self.materials=Materials()
        self.materialIndex=[]
        self.texture=Textures()
        self.localSpace=[]
        self.absoluteSpace=[]
        self.armature=None
        self.vertexGroupWeight=[] 
        self.vertexGroupDict={}   
        self.worldMatrix=world
        self.prehullvertices=[]
        self.faces=Faces()
        
    def unloadModelData(self,exportFile):
        
        self.unloadCoordinates(exportFile)
        self.unloadHull(exportFile)
        self.unloadMaterialIndex(exportFile)
        self.unloadMaterials(exportFile)
        self.unloadTexture(exportFile)
        self.unloadLocalSpace(exportFile)
        self.unloadArmature(exportFile)
        self.unloadDimension(exportFile)
        self.unloadFaces(exportFile)

    def unloadModelWithAnimation(self, exportFile):
        
        self.unloadCoordinates(exportFile)
        self.unloadHull(exportFile)
        self.unloadMaterialIndex(exportFile)
        self.unloadMaterials(exportFile)
        self.unloadTexture(exportFile)
        self.unloadLocalSpace(exportFile)
        self.unloadArmature(exportFile)
        self.unloadAnimations(exportFile)
        self.unloadDimension(exportFile)
        self.unloadFaces(exportFile)


    def unloadNavMeshdata(self, exportFile):

        self.unloadNavMesh(exportFile)

    
    def unloadCoordinates(self,exportFile):
                
        exportFile.writeData("<vertices>",' ')
            
        for i in range(0,len(self.coordinates.vertices)):
            
            exportFile.writeData("%f %f %f "%tuple(self.coordinates.vertices[i]),' ')   
                
        exportFile.writeData("</vertices>")
        
         
        
        exportFile.writeData("<normal>",' ')
        
        for i in range(0,len(self.coordinates.normal)):
            
            exportFile.writeData("%f %f %f "%tuple(self.coordinates.normal[i]),' ')
                     
        exportFile.writeData("</normal>")
        
         
            
        if(self.hasUV):
            
            exportFile.writeData("<uv>",' ')
        
            for i in range(0,len(self.coordinates.uv)):
                
                exportFile.writeData("%f %f "%tuple(self.coordinates.uv[i]),' ')
                   
            exportFile.writeData("</uv>")
            
              
    
        exportFile.writeData("<index>",' ')
        
        for i in self.coordinates.index:
            exportFile.writeData("%d "%i,' ')
        
        exportFile.writeData("</index>")
        
         
        
    def unloadHull(self,exportFile):
        
        exportFile.writeData("<prehullvertices>",' ')
            
        for i in range(0,len(self.prehullvertices)):
            
            exportFile.writeData("%f %f %f "%tuple(self.prehullvertices[i]),' ')   
                
        exportFile.writeData("</prehullvertices>")
        
         
            
    def unloadMaterials(self,exportFile):
        
        if(self.hasMaterials):
            exportFile.writeData("<diffuse_color>",' ')
            for d in self.materials.diffuse:
                exportFile.writeData("%f %f %f 1.0 " %tuple(d),' ')  
            exportFile.writeData("</diffuse_color>")    
                
            exportFile.writeData("<specular_color>",' ')
            for s in self.materials.specular:
                exportFile.writeData("%f %f %f 1.0 "%tuple(s),' ')
            exportFile.writeData("</specular_color>")    
            
            exportFile.writeData("<diffuse_intensity>",' ')
            for di in self.materials.diffuse_intensity:
                exportFile.writeData("%f " %di,' ')
            exportFile.writeData("</diffuse_intensity>")       
            
            exportFile.writeData("<specular_intensity>",' ')
            for si in self.materials.specular_intensity:
                exportFile.writeData("%f " %si,' ')
            exportFile.writeData("</specular_intensity>") 
            
            exportFile.writeData("<specular_hardness>",' ')
            for sh in self.materials.specular_hardness:
                exportFile.writeData("%f " %sh,' ')
            exportFile.writeData("</specular_hardness>") 
    
             
    
    def unloadMaterialIndex(self,exportFile):
        if(self.hasMaterials):
            exportFile.writeData("<material_index>",' ')
            for i in self.materialIndex:
                exportFile.writeData("%d " %i,' ')  
            exportFile.writeData("</material_index>")  
             
                
    def unloadTexture(self,exportFile):
        
        if(self.hasTexture):
            exportFile.writeData("<texture_image>%s</texture_image>"%self.texture)
            
             
    
    def unloadLocalSpace(self,exportFile):
        
        exportFile.writeData("<local_matrix>",' ')
        for m in self.localSpace:
            exportFile.writeData("%f %f %f %f "%tuple(m.row[0]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[1]),' ')
            exportFile.writeData("%f %f %f %f "%tuple(m.row[2]),' ')
            exportFile.writeData("%f %f %f %f"%tuple(m.row[3]),' ')
        exportFile.writeData("</local_matrix>")
        
         
        
    def unloadArmature(self,exportFile):
        
        if(self.hasArmature):
            self.armature.unloadBones(exportFile)
    
    def setArmature(self):
        self.armature.setRootBone()
        
    def unloadAnimations(self,exportFile):
        
        if(self.hasArmature):
            if(self.armature.hasAnimation):
                self.armature.unloadAnimations(exportFile)   
        
    def unloadDimension(self,exportFile):
        
        exportFile.writeData("<dimension>",' ')
            
        for dimension in self.dimension:
            exportFile.writeData("%f %f %f"%tuple(dimension),' ')  
                
        exportFile.writeData("</dimension>")
        
    def unloadFaces(self,exportFile):

        exportFile.writeData("<mesh_vertices>",' ')

        for meshVertex in self.faces.vertices:
            exportFile.writeData("%f %f %f "%tuple(meshVertex),' ')

        exportFile.writeData("</mesh_vertices>")     

        exportFile.writeData("<mesh_edges_index>",' ')

        for meshEdge in self.faces.edgesIndex:
            exportFile.writeData("%d "%meshEdge,' ')

        exportFile.writeData("</mesh_edges_index>")

        exportFile.writeData("<mesh_faces_index>",' ')

        for meshface in self.faces.facesIndex:
            exportFile.writeData("%d "%meshface,' ')

        exportFile.writeData("</mesh_faces_index>")
        
class Lights:
    pass

class Camera:
    pass

class World:
    def __init__(self):
        self.metalSpaceTransform=[]
        self.metalLocalSpaceTransform=[]
        self.metalAnimationSpaceTransform=[]
        self.metalArmatureSpaceTransform=[]
        self.metalParentAnimationSpaceTransform=[]
  
class Loader:
    def __init__(self):
        self.modelList=[]
        self.pointLightsList=[]
        self.cameraList=[]
        self.navMeshList=[]
        self.world=None
        
    def r3d(self,v):
        return round(v[0],6), round(v[1],6), round(v[2],6)


    def r2d(self,v):
        return round(v[0],6), round(v[1],6)
    
    
    def start(self):
        
        self.loadModel()
        self.loadPointLights()
        #self.loadCamera()
        
    def writeToFile(self, exportFile):
        self.unloadData(exportFile)
        self.unloadModel(exportFile)
        self.unloadPointLights(exportFile)
        #self.unloadCamera()
    
    def loadModel(self):
        
        scene=bpy.context.scene
        
        #get world matrix
        world=World()
        #convert world to metal coords
        world.metalSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.metalSpaceTransform*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.metalSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))

        #metal transformation
        world.metalSpaceTransform *= mathutils.Matrix.Scale(-1, 4, (1, 0, 0))
        world.metalSpaceTransform *= mathutils.Matrix.Rotation(radians(180), 4, "Z")


        world.metalLocalSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalLocalSpaceTransform*=mathutils.Matrix.Rotation(radians(90),4,"X")
        world.metalLocalSpaceTransform*=mathutils.Matrix.Scale(-1,4,(0,0,1))


        world.metalArmatureSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalArmatureSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.metalArmatureSpaceTransform*=mathutils.Matrix.Rotation(radians(90),4,"X")
        world.metalArmatureSpaceTransform*=mathutils.Matrix.Scale(-1,4,(0,0,1))

        # metal transformation
        world.metalArmatureSpaceTransform *= mathutils.Matrix.Scale(-1, 4, (1, 0, 0))
        world.metalArmatureSpaceTransform *= mathutils.Matrix.Rotation(radians(180), 4, "Z")
        
        world.metalModelerAnimationSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalModelerAnimationSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.metalModelerAnimationSpaceTransform*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.metalModelerAnimationSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))

        # metal transformation
        world.metalModelerAnimationSpaceTransform *= mathutils.Matrix.Scale(-1, 4, (1, 0, 0))
        world.metalModelerAnimationSpaceTransform *= mathutils.Matrix.Rotation(radians(180), 4, "Z")

        world.metalModelerAnimationSpaceTransform=world.metalModelerAnimationSpaceTransform.inverted()
        
        
        self.world=world

        #Normalize the rotation and scale of all objects

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        #get all models in the scene
        for models in scene.objects:
            
            #export models that are of type mesh and are not hidden
            if(models.type=="MESH" and models.hide is False):


                #triangularized the models

                # set the model as active
                scene.objects.active = models

                # put the model in edit mode
                bpy.ops.object.mode_set(mode='EDIT')

                # select all parts of the model
                bpy.ops.mesh.select_all(action='SELECT')

                # triangulize the model
                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

                # put the model back in normal mode
                bpy.ops.object.mode_set(mode='OBJECT')

                #end triangularization
                
                model=Model(world)
                
                #get name of model
                model.name=models.name
                
                #get local matrix
                matrix_local=world.metalLocalSpaceTransform*scene.objects[model.name].matrix_local*world.metalLocalSpaceTransform
                
                #negate the z-axis
                #matrix_local[2][3]=-matrix_local[2][3]
                
                model.localSpace.append(matrix_local)
                
                #get absolute matrix
                model.absoluteSpace.append(scene.objects[model.name].matrix_world)
                
                 #get index of model
                for i,indices in enumerate(scene.objects[model.name].data.loops):
                    
                    #get vertices of model
                    
                    vertex=scene.objects[model.name].data.vertices[indices.vertex_index].co
                    
                    #convert vertex to metal coordinate
                    vertex=world.metalSpaceTransform*vertex                
                    
                    vertex=self.r3d(vertex)
                    
                    model.coordinates.vertices.append(vertex)
                    
                    #get normal of model
                    
                    normal=scene.objects[model.name].data.vertices[indices.vertex_index].normal
                    
                    #convert normal to metal coordinate
                    normal=world.metalSpaceTransform*normal
                    
                    normal=self.r3d(normal)
                    
                    model.coordinates.normal.append(normal)
                    
                    #get vertex weight
                    
                    vertexGroupWeightDict={}  #create a dictionary for the weights
                    
                    for vertexGroup in scene.objects[model.name].data.vertices[indices.vertex_index].groups:
                        
                        vertexGroupWeightDict[vertexGroup.group]=vertexGroup.weight
                        
                    model.vertexGroupWeight.append(vertexGroupWeightDict)
                        
                    #get the index
                    model.coordinates.index.append(i)
                    
                    #get material index
                    #material_index=scene.objects[model.name].data.polygons[indices.vertex_index].material_index
                    #model.materialIndex.append(material_index)
                
                if(scene.objects[model.name].data.uv_layers):
                    for uvCoordinates in scene.objects[model.name].data.uv_layers.active.data:
                        
                        #get uv coordinates of model                    
    
                        model.coordinates.uv.append(self.r2d(uvCoordinates.uv))
                        model.hasUV=True
                    
                #check if model has materials
                
                if(len(scene.objects[model.name].material_slots)<1):

                    meshMaterial=bpy.data.materials.new(name="NewMaterial")
                    scene.objects[model.name].data.materials.append(meshMaterial)

                
                #get material index
                for materialIndex in scene.objects[model.name].data.polygons:
                    #need to append it three for each triangle vertex
                    model.materialIndex.append(materialIndex.material_index)
                    model.materialIndex.append(materialIndex.material_index)
                    model.materialIndex.append(materialIndex.material_index)
                    
                    
                #get model material slots
                for materialSlot in scene.objects[model.name].material_slots:
                    
                    model.materials.diffuse.append(bpy.data.materials[materialSlot.name].diffuse_color)
                    model.materials.specular.append(bpy.data.materials[materialSlot.name].specular_color)
                    model.materials.diffuse_intensity.append(bpy.data.materials[materialSlot.name].diffuse_intensity)
                    model.materials.specular_intensity.append(bpy.data.materials[materialSlot.name].specular_intensity)
                    model.materials.specular_hardness.append(bpy.data.materials[materialSlot.name].specular_hardness)
                    
                model.hasMaterials=True
                
                
                #get texture name
                if(model.hasUV==True):
                    if(scene.objects[model.name].data.uv_textures.active.data[0].image!=None):
                        
                        model.hasTexture=True;
                        
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
                    
                    #update the metal space of the armature
                    #modelArmature.localMatrix=world.metalArmatureSpaceTransform.inverted()*armature.matrix_local*world.metalArmatureSpaceTransform
                    
                    #modify the armature local matrix

                    modelArmature.localMatrix=mathutils.Matrix.Identity(4)

                    model.localSpace.clear()

                    model_armature_localSpace=world.metalArmatureSpaceTransform*armature.matrix_local*world.metalArmatureSpaceTransform

                    model.localSpace.append(model_armature_localSpace)

                    #end modify the armature local matrix

                    #set name
                    model.armature.name=armature.name
                    
                    #set Bind Shape Matrix
                    model.armature.bindShapeMatrix.append(modelArmature.localMatrix)
                    
                    #set the modeler animation transformation space
                    model.armature.modelerAnimationSpaceTransform.append(world.metalModelerAnimationSpaceTransform)
                    
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

                #SECTION TO EXTRACT THE FACES OF THE MESH
                for meshVertex in scene.objects[model.name].data.vertices:

                    #convert vertex to metal coordinate
                    meshFaceVertex=world.metalSpaceTransform*meshVertex.co                
                    
                    meshFaceVertex=self.r3d(meshFaceVertex)

                    model.faces.vertices.append(meshFaceVertex)

                for meshEdge in scene.objects[model.name].data.edges:
                    for vertexIndex in meshEdge.vertices:
                        model.faces.edgesIndex.append(vertexIndex)

                for meshFace in scene.objects[model.name].data.polygons:
                    for vertexIndex in meshFace.vertices:
                        model.faces.facesIndex.append(vertexIndex)

                #SECTION TO COMPUTE THE CONVEX HULL

                meshCopy=bpy.data.meshes.new("modelCopy")
                newModel=bpy.data.objects.new("modelCopy",meshCopy)

                newModel.data=models.data.copy()
                newModel.scale=models.scale
                newModel.location=models.location
                scene.objects.link(newModel)

                newModel.select=True

                scene.objects.active=newModel

                # put the model in edit mode
                bpy.ops.object.mode_set(mode='EDIT')

                # select all parts of the model
                bpy.ops.mesh.select_all(action='SELECT')

                #compute the convex hull

                bpy.ops.mesh.convex_hull()


                #get the individual vertices to compute convex hull
                for prehullvertices in scene.objects[model.name].data.vertices:
                
                    #get the coordinate
                    prehullvertex=prehullvertices.co
                    
                    #convert vertex to metal coordinate
                    prehullvertex=world.metalSpaceTransform*prehullvertex                
                    
                    prehullvertex=self.r3d(prehullvertex)
                    
                    model.prehullvertices.append(prehullvertex) 

                
                bpy.ops.object.mode_set(mode='OBJECT')

                scene.objects.unlink(newModel)

                scene.objects.active=models

                #END SECTION TO COMPUTE CONVEX HULL
       
                self.modelList.append(model)


                
    
    def loadPointLights(self):
        
        scene=bpy.context.scene
        
         #get all lights in the scene
        for lights in scene.objects:
            
            if(lights.type=="LAMP"):
                
                if(bpy.data.lamps[lights.name].type=="SUN"):

                    light=PointLights()
                    
                    light.name=lights.name
                    
                    #light color
                    light.color.append(scene.objects[light.name].data.color)
                    
                    #Light energy
                    light.energy=scene.objects[light.name].data.energy
                    
                    #light local space
                    light.localSpace.append(self.world.metalLocalSpaceTransform*scene.objects[light.name].matrix_local*self.world.metalLocalSpaceTransform)
                    
                    #append the lights to the list
                    self.pointLightsList.append(light)

    def loadNavMesh(self):

        scene=bpy.context.scene

        #get world matrix
        world=World()
        #convert world to metal coords
        world.metalSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))
        world.metalSpaceTransform*=mathutils.Matrix.Rotation(radians(90), 4, "X")
        world.metalSpaceTransform*=mathutils.Matrix.Scale(-1, 4, (0,0,1))

        #metal transformation
        world.metalSpaceTransform *= mathutils.Matrix.Scale(-1, 4, (1, 0, 0))
        world.metalSpaceTransform *= mathutils.Matrix.Rotation(radians(180), 4, "Z")


        world.metalLocalSpaceTransform=mathutils.Matrix.Identity(4)
        world.metalLocalSpaceTransform*=mathutils.Matrix.Rotation(radians(90),4,"X")
        world.metalLocalSpaceTransform*=mathutils.Matrix.Scale(-1,4,(0,0,1))        
        
        self.world=world

        for model in scene.objects:
            
            #export models that are of type mesh and are not hidden
            if(model.type=="MESH" and model.hide is False):

                # START SECTION FOR NAV MESH NODES

                # put the model in edit mode
                bpy.ops.object.mode_set(mode='EDIT')

                # select all parts of the model
                bpy.ops.mesh.select_all(action='SELECT')


                navMesh=NavMesh()

                navMesh.name=model.name

                bm=bmesh.from_edit_mesh(scene.objects[model.name].data)

                for modelFace in bm.faces:
                    

                    navMeshNode=NavMeshNode()

                    navMeshNode.index=modelFace.index

                    #center of face
                    meshNode_location=modelFace.calc_center_median()

                    meshNode_location=world.metalSpaceTransform*meshNode_location

                    meshNode_location=self.r3d(meshNode_location)

                    navMeshNode.location.append(meshNode_location)
                    
                    # get the neihbors of the mesh nodes
                    for edge in modelFace.edges:
                        linked = edge.link_faces
                        for face in linked:
                            if(face.index!=modelFace.index):
                                navMeshNode.neighbours.append(face.index)

                    navMesh.navMeshNodes.append(navMeshNode)

                bpy.ops.object.mode_set(mode='OBJECT')

                # END SENCTION FOR NAV MESH NODES

                #append nav mesh
                self.navMeshList.append(navMesh)
    
    def loadCamera(self):
        pass

    def unloadData(self,exportFile, dataTypeToExport):
        
        exportFile.writeData("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        exportFile.writeData("<UntoldEngine xmlns=\"\" version=\"0.0.2\">")
        
        exportFile.writeData("<asset>")


        if dataTypeToExport == "Mesh":

            self.unloadModel(exportFile)

        elif dataTypeToExport == "MeshAnim":

            self.unloadModelWithAnimation(exportFile)

        elif dataTypeToExport == "Animation":
            
            self.unloadAnimation(exportFile)

        elif dataTypeToExport == "Light":
            
            self.unloadPointLights(exportFile)

        elif dataTypeToExport == "NavMesh":

            self.unloadNavMesh(exportFile)
        
        exportFile.writeData("</asset>")
        
        exportFile.writeData("</UntoldEngine>")
        
        
    def unloadModel(self,exportFile):
        
        exportFile.writeData("<meshes>")
        
        for model in self.modelList:
            
            exportFile.writeData("<!--Start of Mesh Data-->")
            exportFile.writeData("<mesh name=\"%s\" vertex_count=\"%d\" index_count=\"%d\">"%(model.name,len(model.coordinates.vertices),len(model.coordinates.index)))
            
            model.unloadModelData(exportFile)
            
            exportFile.writeData("</mesh>")                                 
            
        
        exportFile.writeData("</meshes>")
        
    def unloadAnimation(self, exportFile):
        
        exportFile.writeData("<meshes>")
        
        for model in self.modelList:
            
            exportFile.writeData("<!--Start of Mesh Data-->")
            exportFile.writeData("<mesh name=\"%s\" vertex_count=\"%d\" index_count=\"%d\">"%(model.name,len(model.coordinates.vertices),len(model.coordinates.index)))
            
            model.unloadAnimations(exportFile)
            
            exportFile.writeData("</mesh>")                                 
            
        
        exportFile.writeData("</meshes>")

    def unloadModelWithAnimation(self, exportFile):
        
        exportFile.writeData("<meshes>")
        
        for model in self.modelList:
            
            exportFile.writeData("<!--Start of Animation Data-->")
            exportFile.writeData("<mesh name=\"%s\" vertex_count=\"%d\" index_count=\"%d\">"%(model.name,len(model.coordinates.vertices),len(model.coordinates.index)))
            
            model.unloadModelWithAnimation(exportFile)
            
            exportFile.writeData("</mesh>")                                 
            
        
        exportFile.writeData("</meshes>")
        
    def unloadPointLights(self,exportFile):
        
        exportFile.writeData("<point_lights>")
        for lights in self.pointLightsList:
             
            exportFile.writeData("<point_light name=\"%s\">"%lights.name)
            
            lights.unloadPointLightData(exportFile)
            
            exportFile.writeData("</point_light>")
             
        exportFile.writeData("</point_lights>")

    def unloadNavMesh(self,exportFile):

        exportFile.writeData("<!--Start of Navigation Data-->")
        exportFile.writeData("<navigation_mesh>")

        for navMesh in self.navMeshList:

            exportFile.writeData("<nav_mesh name=\"%s\">"%navMesh.name)

            navMesh.unloadNavMeshData(exportFile)

            exportFile.writeData("</nav_mesh>")

        exportFile.writeData("</navigation_mesh>")
        
         
    def unloadCamera(self):
        pass


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Menu, Panel, UIList

class View3DPanel():
    bl_space_type='VIEW_3D'
    bl_region_type='TOOLS'

# Create a panel for the export settings
class exportPanel(View3DPanel, Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Untold Engine Export"
    bl_idname = "OBJECT_PT_exportpanel"
    bl_context="objectmode"
    bl_category="Untold Engine"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Export 3D Models")


        row = layout.row()
        row.operator("object.untoldengineexport")


# Create an export button
class exportButton(bpy.types.Operator):
    bl_label = "Export"
    bl_idname = "object.untoldengineexport"
    bl_description = "Export"
 
    def execute(self, context):

        # call the export helper class
        bpy.ops.untold_engine_export.data('INVOKE_DEFAULT')
        
        return {'FINISHED'}


class ExportHelperClass(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "untold_engine_export.data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Mesh"

    # ExportHelper mixin class uses this
    filename_ext = ".u4d"

    filter_glob = StringProperty(
            default="*.u4d",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    # use_setting = BoolProperty(
    #         name="Example Boolean",
    #         description="Example Tooltip",
    #         default=True,
    #         )

    dataTypeToExport = EnumProperty(
            name="Export Type",
            description="Choose data to export",
            items=(('Mesh', "Mesh Data Only", "Export Mesh Data only"),
                   ('MeshAnim', "Mesh and Animation Data", "Export Mesh and Animation Data"),
                   ('Animation', "Animation Data Only", "Export Animation Data only"),
                   ('Light', "Light Data Only", "Export Light Data only"),
                   ('NavMesh', "Navigation Data", "Export NavMesh Data only")),
            default='Mesh',
            )

    def execute(self, context):
        return main(context, self.filepath, self.dataTypeToExport)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportHelperClass.bl_idname, text="Text Export Operator")


def register():
    bpy.utils.register_class(exportPanel)
    bpy.utils.register_class(exportButton)
    bpy.utils.register_class(ExportHelperClass)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(exportPanel)
    bpy.utils.unregister_class(exportButton)
    bpy.utils.unregister_class(ExportHelperClass)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    
def main(context, filePath, dataTypeToExport):


    #set scene to frame zero
    scene=bpy.context.scene
    scene.frame_set(0)
    
    #open the file to write
    exportFile=ExportFile(filePath)
    exportFile.openFile()

    loader=Loader()
    loader.loadModel()
    loader.loadPointLights()

    if dataTypeToExport == "NavMesh":
        loader.loadNavMesh()
    
    loader.unloadData(exportFile, dataTypeToExport)

    #close the file
    exportFile.closeFile()

    return {'FINISHED'}
    

if __name__ == '__main__':
    register()

    # test call
    #bpy.ops.untold_engine_export.data('INVOKE_DEFAULT')
    