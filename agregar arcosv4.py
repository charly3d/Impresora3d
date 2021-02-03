########################
#     IMPORTACIONES    #
########################
from numpy import matrix
from numpy import linalg
import numpy as np
import math
import re

#import matplotlib.pyplot as plt

########################
#       FUNCIONES      #
########################
def radioycentro (pto1,pto2,pto3):
    #sistema de ecuaciones para determinar ecuacion AxX=B
    x1=pto1[0]*1000
    y1=pto1[1]*1000
    x2=pto2[0]*1000
    y2=pto2[1]*1000
    x3=pto3[0]*1000
    y3=pto3[1]*1000
    A=matrix([[x1,y1,1],[x2,y2,1],[x3,y3,1]])
    B=matrix([[-(x1**2+y1**2)],[-x2**2-y2**2],[-x3**2-y3**2]])

    A_inv=A.I
    X=A_inv*B
    #print(X)
    #centro del circulo
    cx=-float(X[0][0])/2000
    cy=-float(X[1][0])/2000
    #radio circulo
    r=math.sqrt(float(-float(X[2][0])+(cx*1000)**2+(cy*1000)**2))/1000
    #print ('r=',r,'x=',cx,'y=',cy)

    return (cx,cy,r)
def vpto(cx,cy,r,pto4):
    #determinar si el cuarto punto pertenece a la circunferencia
    distancia=math.sqrt((pto4[0]*1000-cx*1000)**2+(pto4[1]*1000-cy*1000)**2)-r*1000
    tolerancia=0.1
    #print (distancia)
    if distancia/1000<=tolerancia:
        return True
    else:
        return False
def sentido(ptoi,ptom,ptof):
    ptoi=np.array(ptoi)
    ptof=np.array(ptof)
    ptom=np.array(ptom)
    vi=ptof-ptoi
    vm=ptom-ptoi
    sent=np.cross(vi,vm)
    
    if sent>0 :
        arco='G2'
    else:
        arco='G3'
    return arco

########################
#       PROGRAMA       #
########################

#manejadores archivos
nombre=input('nombre del archivo: ')
nombre2=nombre+'arcos.gcode'
nombre=nombre+'.gcode'

#contadores y listas 
contador=0
ctalinea=0
ctag2g3=0
ctalb=0
lineas=[]
x=[0]
y=[0]
e=[0]
z=[0]
escribir=''
x1=0
y1=0
z1=0
e1=0
x0=0
y0=0
z0=0
e0=0
posicion=(x0,y0,z0,e0)
posicionanterior=(x1,y1,z1,e1)
#Crear y abrir archivos
nuevo=open(nombre2,'w')
archivo=open(nombre)

#Recorre archivo para buscar lineas que se puedan agrupar en G2 o G3
for linea in archivo:
    ctalinea+=1                                              #cuenta lineas recorridas

    linea=linea.rstrip()                              #elimina espacios de la derecha
    palabras=linea.split() 
    escribir=escribir+'\n'+linea                     #agrega la linea recorrida la lista escribir
    if 'X' in linea:
        x1=re.findall(r'^G.+X([0-9.]+)',linea)
        if len (x1)!=0:
            x1=float(x1[0])
    if 'Y' in linea:
        y1=re.findall(r'^G.+Y([0-9.]+)',linea)
        if len (y1)!=0:
            y1=float(y1[0])
    if 'Z' in linea:
        z1=re.findall(r'^G.+Z([0-9.]+)',linea)
        if len (z1)!=0:
            z1=float(z1[0])
    if 'E' in linea:
        e1=re.findall(r'^G.+E([0-9.]+)',linea)
        if len (e1)!=0:
            e1=float(e1[0])

    
    if 'LAYER' in linea:
        print (linea)
    if len(linea)==0 or not linea.startswith('G1 X')or 'Z'in linea or 'F' in linea: #se fija que comience con G1 X y que no este vacia
        if len (x)>=4:

            I=-x[0]+cx
            J=-y[0]+cy
            nuevalinea='\n%s F1200 X%g Y%g I%g J%g E%g'%(sentido(ptoi,pto2,(x[-2],y[-2])),x[-1],y[-1],I,J,e[-1])
            ctag2g3+=1
            escribir=nuevalinea+'\n'+linea
            nuevo.write(escribir)
            #print(ptoi,ptof,round(cx,3),round(cy,3),round(r,3),round(I,3),round(J,3))
            escribir=''
            contador=0
            lineas=[]
            x0=x1
            y0=y1
            z0=z1
            e0=e1
            x=[x0]
            y=[y0]
            e=[e0]

            continue
        
        nuevo.write(escribir)                         #Si la linea esta vacia o no empieza con G1 X 
                                                      # la vuelve a escribrir tal cual estaba y rinicia
        escribir=''                                   #contadores y listas
        contador=0
        ctalb+=1
        lineas=[]
        x=[x1]
        y=[y1]
        e=[e1]
        continue    

    contador+=1
    lineavieja=linea
    lineas.append(palabras)                          #agrega a la lista linea las palabras de la linea ['G1','X213','Y221','E265']
         
    x.append(x1)
    y.append(y1)
    e.append(e1)
    
    
    if contador >=4:                                 #si pasaron cuatro lineas con g1 se fija que 3 formen un circulo y que el cuarto se parte del circulo

        #crea los puntos para calcular circulo y verificar que el cuarto pertenezca  
        p1_3=int(len(x)/3)
        p2_3=int(len(x)*2/3)
        ptoi=(x[0],y[0])
        pto2=(x[p1_3],y[p1_3])
        pto3=(x[p2_3],y[p2_3])
        ptof=(x[-1],y[-1])
        print (ptoi,y1,x1)
        (cx,cy,r)=radioycentro(ptoi,pto2,pto3)       #obtenercirculo
        I=-x[0]+cx
        J=-y[0]+cy
        #if vpto(cx,cy,r,ptof):continue               #si el cuarto punto esta dentro del circulo pasa a la siguiente linea 

                                                     #si el cuarto punto no pertenece al circulo escribe las lineas tal cual estaban y vuelve todo a cero

        if not vpto(cx,cy,r,ptof) :
            (cx,cy,r)=radioycentro(ptoi,pto2,pto3)
            I=-x[0]+cx
            J=-y[0]+cy
            nuevalinea='\n%s F1200 X%g Y%g I%g J%g E%g'%(sentido(ptoi,pto2,(x[-2],y[-2])),x[-2],y[-2],I,J,e[-2])
            #print(p1_3,p2_3)
            ctag2g3+=1
            escribir=nuevalinea
            nuevo.write(escribir)

            escribir=''
            contador=1
            lineas=[]
            lineas.append(palabras)
            x=x[-2:]
            y=y[-2:]
            e=e[-2:]
  
nuevo.write(escribir)       
print (ctalb,ctalinea,ctag2g3,x,y,e)

nuevo.close
nuevo=open(nombre2)
archivo.close
nuevo.close






