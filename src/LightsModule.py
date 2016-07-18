'''
Created on Jul 18, 2016

@author: haroldserrano
'''

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