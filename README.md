# Sistema Planetario 3D
Programa que crea una representación gráfica en 2D, de un sistema planetario descrito
en un archivo `json`.

## Instalación y ejecución
Para poder utilizar la aplicación se necesitan instalar los paquetes requeridos por
el proyecto. Estos se encuentran en el archivo `requeriments.txt` y para instalarlos
se debe correr el comando:
```
pip install -r requeriments.txt
```

Para correr la aplicación, se debe hacer la llamada por consola ubicada en la carpeta de la aplicación:
```
python system_3dview.py bodies.json
```
Siendo `bodies.json` el archivo `json` donde está la información del sistema planetario. Se puede cambiar
el archivo del que se quiera sacar la información cambiando el último argumento de la llamada anterior.

## Uso
En la aplicación exiten dos modos de visualización. El primero es una vista global del sistema, donde la cámara 
está en todo momento mirando al astro central y se mueve en coordenadas cilíndricas. Con las teclas **A** y **D**
se maneja el ángulo desde el que se mira al astro (girando alrededor de él), con **W** y **S** la altura, y con 
**Z** y **X** la distancia a la estrella. En el segundo modo, la cámara está fija siguiendo a un cuerpo en específico, 
el cual se selecciona con las flechas izquierda y derecha.

## Estructura archivo `json`
El archivo `json` contiene una lista jerarquizada de cuerpos celestes que cumple con:
- Nombre es el nombre del astro. Debe existir un archivo en Texturas/Nombres/*Nombre*.png para poder renderizar el nombre del cuerpo al mostrar su información
- Color que corresponde a un arreglo con el color en RGB.
- Radius que es el radio del cuerpo celeste.
- Distance es la distancia al cuerpo padre.
- Velocity es la velocidad de traslaci ́on con respecto a su padre, y su signo indica el sentido de rotación (sistema horario)
- Model corresponde al directorio donde se encuentra el modelo del cuerpo en `obj`. Si se especifica "Null", se crea una esfera del color y porte especificados antes.
- Inclination es el ángulo en radianes que presenta la órbita del cuerpo con respecto
- Satellites corresponde a una lista de cuerpos celeste que orbitan alrededor, si no tiene se agrega ”Null”.
- El primer cuerpo debe representar la estrella del sistema que se ubicara en el centro, por lo que los datos de Velocity y Distance se ignoran en este caso.

Un ejemplo de archivo `json`:
```
{
    " Nombre": "Sol",
    " Color" : [ 1, 1, 0 ],
    " Radius" : 0.1,
    " Distance" : 0.0,
    " Velocity" : 0.0,
    " Model" : " Null",
    " Inclination" : 0,
    " Satellites" : [
        {
            " Nombre": "planeta",
            " Color" : [ 0.0, 0.2, 0.8 ],
            " Radius" : 0.05,
            " Distance" : 0.6,
            " Velocity" : 0.4,
            " Model" : "Cuerpos\\planeta.obj",
            " Inclination" : 0.1,
            " Satellites" : "Null"
        }
    ]
}
```
Esto representa una estrella con un planeta, donde el planeta tiene el modelo `planeta.obj`.