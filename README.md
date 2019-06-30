# Raytracer
A simple recursive raytracer writting in python (v.3.6)

What I've learned from this project:
- working with more complex algorithms in python
- deepened my understanding of linear algebra
- how to use textures and implement shading algorithms

If you want to use it you will need to install Pillow (previously known as simply "PIL")
Objects are in the object_list. 
- Spehres require x,y and z coordinates, a scale, and a texture/color
- Planes require x,y and z coordinates, a normal vector and a texture/color
- Triangles require their 3 vertices and a texture/color

You can add or edit light in the light_list. A light consists of its position and a color.

![Raytraced image with dimension 800x800 and a recursion depth of 3](https://raw.githubusercontent.com/tommydittberner/raytracer/master/raytracer800x800.jpg)
