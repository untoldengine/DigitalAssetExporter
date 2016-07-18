'''
Created on Jul 18, 2016

@author: haroldserrano
'''

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
        self.dimension=[]
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
        
    def unloadModelData(self):
        
        self.unloadCoordinates()
        self.unloadMaterials()
        self.unloadTexture()
        self.unloadLocalSpace()
        self.unloadArmature()
        self.unloadAnimations()
        self.unloadDimension()
    
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
        
    def unloadDimension(self):
        
        print("<dimension>",end="")
            
        for dimension in self.dimension:
            print("%f %f %f"%tuple(dimension),end="")  
                
        print("</dimension>")
        
        print()
        