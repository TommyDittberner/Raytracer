from math import sqrt, tan, pi
from PIL import Image

class Point():
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, vector):
        return Point(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    def __sub__(self, other_point):
        return Vector(self.x - other_point.x, self.y - other_point.y, self.z - other_point.z)

    def __mul__(self, factor):
        return Point(self.x * factor, self.y * factor, self.z * factor)

    def __repr__(self):
        return "Point(%s.%s,%s)" % (repr(self.x), repr(self.y), repr(self.z))

class Vector():
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other_vector):
        return Vector(self.x + other_vector.x, self.y + other_vector.y, self.z + other_vector.z)

    def __sub__(self, other_vector):
        return Vector(self.x - other_vector.x, self.y - other_vector.y, self.z - other_vector.z)

    def __mul__(self, other):
        if type(other) is Vector or type(other) is Color:
            return Vector(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __repr__(self):
        return "Vector(%s.%s,%s)" % (repr(self.x), repr(self.y), repr(self.z))

    def dot(self, other_vector):
        return self.x * other_vector.x + self.y * other_vector.y + self.z * other_vector.z

    def cross(self, other_vector):
        return Vector(self.y * other_vector.z - self.z * other_vector.y,
                      self.z * other_vector.x - self.x * other_vector.z,
                      self.x * other_vector.y - self.y * other_vector.x)

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        length = self.length()
        return Vector(self.x / length, self.y / length, self.z / length)

    def scale(self, factor):
        return self * factor

    def reflect(self, normal):
        return self - normal * normal.dot(self) * 2

class Ray():
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalized()

    def __repr__(self):
        return "Ray(%s.%s)" % (repr(self.origin), repr(self.direction))

    def point_at_parameter(self, t):
        return self.origin + self.direction.scale(t)

class Plane():
    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalized()
        self.material = material

    def __repr__(self):
        return "Plane(%s.%s)" % (repr(self.point), repr(self.normal))

    def intersection_parameter(self, ray):
        op = ray.origin - self.point
        a = op.dot(self.normal)
        b = ray.direction.dot(self.normal)
        if b:
            return - a/b
        else:
            return None

    def normal_at(self, p):
        return self.normal

class Sphere():
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def __repr__(self):
        return "Sphere(%s,%s)" % (repr(self.center), repr(self.radius))

    def intersection_parameter(self, ray):
        co = self.center - ray.origin
        v = co.dot(ray.direction)
        discriminant = v*v - co.dot(co) + self.radius*self.radius
        if discriminant < 0:
            return None
        else:
            return v - sqrt(discriminant)

    def normal_at(self, p):
        return (p - self.center).normalized()

class Triangle():
    def __init__(self, a, b, c, material):
        self.a = a
        self.b = b
        self.c = c
        self.u = self.b - self.a
        self.v = self.c - self.a
        self.material = material

    def __repr__(self):
        return "Triangle(%s.%s,%s)" % (repr(self.a), repr(self.b), repr(self.c))

    def intersection_parameter(self, ray):
        w = ray.origin - self.a
        dv = ray.direction.cross(self.v)
        dvu = dv.dot(self.u)
        if dvu == 0.0:
            return None
        wu = w.cross(self.u)
        r = dv.dot(w) / dvu
        s = wu.dot(ray.direction)  / dvu
        if 0 <= r and r <= 1 and 0 <= s and s <= 1 and r+s <= 1:
            return wu.dot(self.v) / dvu
        else:
            return None

    def normal_at(self, p):
        return self.u.cross(self.v).normalized()

class Color(Vector):
    def __init__(self, r, g, b):
        super().__init__(r, g, b)

class Light():
    def __init__(self, position, color=Color(1,1,1)):
        self.position = position
        self.color = color

class CheckerboardMaterial():
    def __init__(self, checkSize=0.5):
        self.baseColor = Color(0,0,0)
        self.otherColor = Color(1,1,1)
        self.checkSize = checkSize
        self.reflection = 0
        self.ambient = 1.0
        self.diffuse = 0.6
        self.specular = 0.1
        self.n = 32

    def baseColorAt(self, hitpoint):
        v = Vector(hitpoint.x, hitpoint.y, hitpoint.z)
        v = v.scale(1 / self.checkSize)
        if (int(abs(v.x) + 0.5) + int(abs(v.y) + 0.5) + int(abs(v.z) + 0.5)) % 2:
            return self.otherColor
        return self.baseColor

    def shade(self, light_ray, normal, camera_direction, light):
        return Color(0,0,0) #no shading

class Material():
    def __init__(self, baseColor, ambient=1.0, diffuse=0.6, specular=0.2, reflection=0.2):
        self.baseColor = baseColor
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.reflection = reflection

    def baseColorAt(self, hitpoint):
        return self.baseColor * self.ambient

    def shade(self, light_ray, normal, camera_direction, light):

        light_direction = light_ray.direction
        color = Color(0,0,0)
        #diffuse
        cos_phi = light_direction.dot(normal)
        if cos_phi > 0:
            color += light.color * self.diffuse * cos_phi

        #spcular
        reflection = light_direction.reflect(normal)
        cos_theta = reflection.dot(camera_direction)
        if cos_theta > 0:
            color += light.color * self.specular * cos_theta ** SHININESS

        return color

class Camera():
    def __init__(self, e, c, up, fov):
        self.e = e
        self.c = c
        self.up = up
        self.fov = fov
        self.f = (e-c).normalized()
        self.s = self.f.cross(up).normalized()
        self.u = self.s.cross(self.f)
        self.alpha = fov/2
        self.aspectratio = IMAGE_HEIGHT / IMAGE_WIDTH
        self.heigth = 2 * tan(self.alpha)
        self.width = self.aspectratio * self.heigth
        self.pixelwidth = self.width / (IMAGE_WIDTH -1)
        self.pixelheight = self.heigth / (IMAGE_HEIGHT -1)

    def testShadow(self, object_list, light_ray):
        for object in object_list:
            hitpoint = object.intersection_parameter(light_ray)
            if hitpoint and hitpoint > 0.01:
                return True
        return False

    def calcRay(self, x, y):
        xcomp = self.s.scale(x * self.pixelwidth - self.width / 2)
        ycomp = self.u.scale(y * self.pixelheight - self.heigth / 2)
        return Ray(self.e, self.f + xcomp + ycomp)

    def getColorAt(self, ray, object, object_list, light_list, hitpoint, normal):
        color = object.material.baseColorAt(hitpoint)  # Ambient
        for light in light_list:
            light_ray = Ray(hitpoint, light.position - hitpoint)
            color += object.material.shade(light_ray, normal, ray.direction, light)
            if self.testShadow(object_list, light_ray):
                color *= SHADOW_FACTOR
        return color

    def traceRay(self, ray, object_list, light_list, lvl):
        nearest_intersection = float('inf')
        color = BACKGROUND_COLOR
        for object in object_list:
            hitdist = object.intersection_parameter(ray)
            if hitdist and hitdist > 0.01 and hitdist < nearest_intersection:
                nearest_intersection = hitdist
                hitpoint = ray.point_at_parameter(nearest_intersection)
                normal = object.normal_at(hitpoint)
                color = self.getColorAt(ray, object, object_list, light_list, hitpoint, normal)
                if lvl < 0:
                    lvl = 0
                if lvl == RENDERLEVEL:
                    return color
                else:
                    reflected_ray = Ray(hitpoint, ray.direction.reflect(normal))
                    reflectionColor = self.traceRay(reflected_ray, object_list, light_list, lvl+1)
                    return color + reflectionColor * object.material.reflection
        return color

    def putpixels(self, color, x, y):
        c = (int(color.x * 255), int(color.y * 255), int(color.z * 255))
        image.putpixel((x,IMAGE_HEIGHT - y), c)

    def render(self, object_list, light_list, lvl):
        for y in range(IMAGE_HEIGHT+1):
            for x in range(IMAGE_WIDTH+1):
                ray = self.calcRay(x, y)
                color = self.traceRay(ray, object_list, light_list, 0)
                self.putpixels(color, x, y)
        image.show()

if __name__ == "__main__":
    FIELD_OF_VIEW = 45
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = IMAGE_WIDTH
    RENDERLEVEL = 3
    SHININESS = 16 #bigger = more shiny

    BACKGROUND_COLOR = Color(0,0,0)
    WHITE = Color(1,1,1)
    SHADOW_FACTOR = 0.3

    RED = Material(Color(0.7, 0, 0))
    GREEN = Material(Color(0, 0.7, 0))
    BLUE = Material(Color(0, 0, 0.7))
    YELLOW = Material(Color(0.7, 0.7, 0))
    DARKGRAY = Material(Color(0.1, 0.1, 0.1))
    CHECK = CheckerboardMaterial(checkSize=1)

    light_list = [Light(Point(30,30,10), Color(1,1,1))]
                  #,Light(Point(-30, 30, 10), Color(1, 1, 1))]

    object_list = [
        Sphere(Point(3, 3, 30), 2.5, RED),
        Sphere(Point(-3, 3, 30), 2.5, GREEN),
        Sphere(Point(0, 9, 30), 2.5, BLUE),
        Triangle(Point(3, 3, 30), Point(-3, 3, 30), Point(0, 9, 30), YELLOW),
        Plane(Point(0, 0, 0), Vector(0, 1, 0), CHECK)
    ]

    cam = Camera(Point(0,1.8,10), Point(0,1,0), Vector(0,1,0), FIELD_OF_VIEW)
    image = Image.new('RGB', (IMAGE_WIDTH+1, IMAGE_HEIGHT+1), "white")
    cam.render(object_list, light_list, RENDERLEVEL)
