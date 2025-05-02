from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Player and camera state
camera_pos = (0, 500, 500)
player_pos = [0, 0, 0]  # x, y, z
player_speed = 10
player_angle = 0  
grid_length = 400
grid_size = 20

# Building 
buildings = [(-150, -150), (150, 150), (150, -150), (-150, 150), (0, 200)]

# Water cubes
water_cube = []  # [x, y, z, vx, vy, vz]

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_buildings():
    glColor3f(1, 0, 0)
    for (x, z) in buildings:
        glPushMatrix()
        glTranslatef(x, 30, z)
        glutSolidCube(60)
        glPopMatrix()

def draw_player():
    x, y, z = player_pos
    glPushMatrix()
    glTranslatef(x, y + 30, z)
    glRotatef(player_angle, 0, 1, 0)

    # Body
    glColor3f(0, 0.5, 1)
    glutSolidCube(60)

    # Head
    glPushMatrix()
    glColor3f(1, 1, 0.8)
    glTranslatef(0, 50, 0)
    glutSolidSphere(20, 10, 10)
    glPopMatrix()

    # L.H
    glPushMatrix()
    glColor3f(1, 0.6, 0.2)
    glTranslatef(-40, 0, 0)
    glRotatef(90, 0, 0, 1)
    gluCylinder(gluNewQuadric(), 4, 4, 20, 10, 10)
    glPopMatrix()

    # R.H
    glPushMatrix()
    glColor3f(1, 0.6, 0.2)
    glTranslatef(40, 0, 0)
    glRotatef(-90, 0, 0, 1)
    gluCylinder(gluNewQuadric(), 4, 4, 20, 10, 10)
    glPopMatrix()

    # extinguisher
    glPushMatrix()
    glColor3f(0.3, 0.3, 0)
    glTranslatef(0, 0, 35)       
    glRotatef(90, 0, 0, 1)
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10)
    glTranslatef(0, 0, 30)
    glColor3f(0.2, 0.2, 0.2)
    gluSphere(gluNewQuadric(),3, 10, 10)
    glPopMatrix()

    glPopMatrix()

def draw_water_cubes():
    for cube in water_cube:
        x, y, z, _, _, _ = cube
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.8, 0.8, 1.0)
        glutSolidCube(8)
        glPopMatrix()

def collides_with_building(x, z):
    for bx, bz in buildings:
        if abs(x - bx) < 60 and abs(z - bz) < 60:
            return True
    return False

def move_player(dx, dz):
    angle = player_angle % 360
    
    # Forward/backward movement (handles 'b' and 'f' keys)
    if angle < 45 or angle >= 315:      # Facing forward (0°)
        move_x = 0
        move_z = -dz  # Negative because in OpenGL, -Z is forward
    elif 45 <= angle < 135:             # Facing left (90°)
        move_x = -dz
        move_z = 0
    elif 135 <= angle < 225:            # Facing backward (180°)
        move_x = 0
        move_z = dz
    else:                               # Facing right (270°)
        move_x = dz
        move_z = 0
    
    # Left/right movement 
    if angle < 45 or angle >= 315:      # Facing forward
        move_x += -dx  
        move_z += 0
    elif 45 <= angle < 135:             # Facing left
        move_x += 0
        move_z += -dx  
    elif 135 <= angle < 225:            # Facing backward
        move_x += dx   
        move_z += 0
    else:                               # Facing right
        move_x += 0
        move_z += dx   
    
    new_x = player_pos[0] + move_x
    new_z = player_pos[2] + move_z

    if not (-570 <= new_x <= 570 and -570 <= new_z <= 570):
        return

    if collides_with_building(new_x, new_z):
        return

    player_pos[0] = new_x
    player_pos[2] = new_z


def keyboardListener(key, x, y):
    global player_angle
    if key == b'b':
        move_player(0, player_speed)
    elif key == b'f':
        move_player(0, -player_speed)
    elif key == b'a':
        player_angle = (player_angle + 5) % 360
    elif key == b'd':
        player_angle = (player_angle - 5) % 360
    elif key == b'l':
        move_player(-10, 0)
    elif key == b'r':
        move_player(10, 0)

def specialKeyListener(key, x, y):
    global camera_pos
    cx, cy, cz = camera_pos
    if key == GLUT_KEY_LEFT:
        cx -= 20
    elif key == GLUT_KEY_RIGHT:
        cx += 20
    elif key == GLUT_KEY_UP:
        cy += 20
    elif key == GLUT_KEY_DOWN:
        cy -= 20
    camera_pos = (cx, cy, cz)

def mouseListener(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        px, py, pz = player_pos
        water_cube.append([px, py + 40, pz - 65, 0, 0, -10])

def update_water_cubes():
    global water_cube
    for cube in water_cube:
        cube[0] += cube[3]
        cube[1] += cube[4]
        cube[2] += cube[5]
    water_cube = [cube for cube in water_cube 
                 if -1000 < cube[0] < 1000 
                 and -1000 < cube[2] < 1000]

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              player_pos[0], player_pos[1] + 30, player_pos[2],
              0, 1, 0)

def idle():
    update_water_cubes()
    glutPostRedisplay()

def draw_grid():
    cell = grid_length * 2 / grid_size
    for i in range(grid_size):
        for j in range(grid_size):
            if (i + j) % 2 == 0:
                glColor3f(0, 0.2, 0.3)
            else:
                glColor3f(1, 0.8, 1)

            x1 = -grid_length + i * cell
            x2 = x1 + cell
            z1 = -grid_length + j * cell
            z2 = z1 + cell

            glBegin(GL_QUADS)
            glVertex3f(x1, 0, z1)
            glVertex3f(x2, 0, z1)
            glVertex3f(x2, 0, z2)
            glVertex3f(x1, 0, z2)
            glEnd()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    draw_grid()
    draw_text(10, 770, f"Player Position: {player_pos}")
    draw_text(10, 740, f"Player Angle: {player_angle}°")
    draw_text(10, 710, f"Water Cubes: {len(water_cube)}")
    draw_buildings()
    draw_player()
    draw_water_cubes()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Fire Extinguishing Simulator")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()