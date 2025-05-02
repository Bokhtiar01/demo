from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import sys
import random

# Camera variables
camera_radius = 500
camera_rotation_angle = 45
camera_height = 500
camera_follow = False

# Game state
paused = False
sound_enabled = True

# Player
player_pos = [0, 0, 0]
player_angle = 0
player_move_step = 15
player_rotate_step = 2

# World parameters
fovY = 120

# Texture ID
texture_id = None

# Bushes
bushes = []

class Bush:
    def __init__(self, x, z, size):
        self.x = x
        self.z = z
        self.size = size

def generate_grass_texture(size=64, squares=8):
    texture_data = []
    base_color = [153, 230, 153]  # Light green (0.6, 0.9, 0.6)
    for i in range(size):
        for j in range(size):
            # Add slight variation for grass-like texture
            variation = random.randint(-20, 20)
            r = min(max(base_color[0] + variation, 0), 255)
            g = min(max(base_color[1] + variation, 0), 255)
            b = min(max(base_color[2] + variation, 0), 255)
            texture_data.extend([r, g, b])
    return texture_data

def load_texture(texture_data):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, bytearray(texture_data))
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    return texture_id

def init_bushes(num_bushes=100, max_distance=5000):
    global bushes
    bushes = []
    for _ in range(num_bushes):
        x = random.uniform(-max_distance, max_distance)
        z = random.uniform(-max_distance, max_distance)
        size = random.uniform(20, 40)
        bushes.append(Bush(x, z, size))

def draw_bushes():
    glColor3f(0.0, 0.5, 0.0)  # Dark green for bushes
    for bush in bushes:
        glPushMatrix()
        glTranslatef(bush.x, bush.size / 2, bush.z)
        glutSolidSphere(bush.size / 2, 10, 10)
        glPopMatrix()

def reset_game():
    global player_pos, player_angle, paused
    player_pos[0] = 0
    player_pos[1] = 0
    player_pos[2] = 0
    player_angle = 0
    paused = False
    glutSetCursor(GLUT_CURSOR_NONE)

def draw_text(x, y, text, font=GLUT_BITMAP_9_BY_15):
    glColor3f(1, 1, 1)  # White text for visibility
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    valid = glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID)
    if not valid:
        print(f"Invalid raster position at ({x}, {y})")
        glRasterPos2f(x + 1, y + 1)  # Slight offset to avoid clipping
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_ground():
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-10000, 0, -10000)
    glTexCoord2f(100, 0)
    glVertex3f(10000, 0, -10000)
    glTexCoord2f(100, 100)
    glVertex3f(10000, 0, 10000)
    glTexCoord2f(0, 100)
    glVertex3f(-10000, 0, 10000)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0)
    glTranslatef(0, 60, 0)
    torso_color = (0.0, 0.8, 0.0)
    leg_color = (0.0, 0.0, 1.0)
    skin_color = (1.0, 0.8, 0.6)
    glColor3f(*leg_color)
    glPushMatrix()
    glTranslatef(-10, -40, 0)
    glScalef(0.6, 2.0, 0.6)
    glutSolidCube(20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(10, -40, 0)
    glScalef(0.6, 2.0, 0.6)
    glutSolidCube(20)
    glPopMatrix()
    glColor3f(*torso_color)
    glPushMatrix()
    glScalef(1.5, 2.5, 1.0)
    glutSolidCube(30)
    glPopMatrix()
    glColor3f(*skin_color)
    glPushMatrix()
    glTranslatef(-12, 20, 15)
    glRotatef(90, 1, 0, 0)
    glScalef(0.5, 2.0, 0.5)
    glutSolidCube(20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(12, 20, 15)
    glRotatef(90, 1, 0, 0)
    glScalef(0.5, 2.0, 0.5)
    glutSolidCube(20)
    glPopMatrix()
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 50, 0)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()
    glPopMatrix()

def draw_settings_menu():
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor4f(0.2, 0.2, 0.2, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    for button in settings_menu_buttons:
        glColor3f(0.3, 0.8, 0.3)
        x = button['x']
        y = button['y']
        w = button['w']
        h = button['h']
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        text_x = x + 50 if button['action'] != 'toggle_sound' else x + 20
        text = button['text'] if button['action'] != 'toggle_sound' else f"Sound: {'On' if sound_enabled else 'Off'}"
        draw_text(text_x, y + 10, text)
    draw_text(450, 600, "SETTINGS", GLUT_BITMAP_9_BY_15)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

def keyboardListener(key, x, y):
    global player_angle, paused
    if key == b'\x1b':  # ESC key
        paused = not paused
        print(f"Settings menu toggled: paused = {paused}")
        glutSetCursor(GLUT_CURSOR_INHERIT if paused else GLUT_CURSOR_NONE)
        glutPostRedisplay()
        return
    if paused:
        return
    if key == b'w':
        player_pos[0] += player_move_step * math.sin(math.radians(player_angle))
        player_pos[2] += player_move_step * math.cos(math.radians(player_angle))
    if key == b's':
        player_pos[0] -= player_move_step * math.sin(math.radians(player_angle))
        player_pos[2] -= player_move_step * math.cos(math.radians(player_angle))
    if key == b'a':
        player_angle += player_rotate_step
    if key == b'd':
        player_angle -= player_rotate_step
    player_angle %= 360
    if key == b'r':
        reset_game()

def specialKeyListener(key, x, y):
    global camera_height, camera_rotation_angle
    if paused:
        return
    if key == GLUT_KEY_UP:
        camera_height += 10
    if key == GLUT_KEY_DOWN:
        camera_height -= 10
    if key == GLUT_KEY_LEFT:
        camera_rotation_angle -= 5
    if key == GLUT_KEY_RIGHT:
        camera_rotation_angle += 5

def mouseListener(button, state, x, y):
    global camera_follow, paused, sound_enabled
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if paused:
            for btn in settings_menu_buttons:
                if (btn['x'] <= x <= btn['x'] + btn['w'] and
                    800 - y >= btn['y'] and
                    800 - y <= btn['y'] + btn['h']):
                    print(f"Settings menu button clicked: {btn['action']}")
                    if btn['action'] == 'resume':
                        paused = False
                        glutSetCursor(GLUT_CURSOR_NONE)
                    elif btn['action'] == 'toggle_sound':
                        sound_enabled = not sound_enabled
                    elif btn['action'] == 'quit':
                        print("Quitting game")
                        glutSetCursor(GLUT_CURSOR_INHERIT)  # Restore cursor
                        glutPostRedisplay()
                        glutLeaveMainLoop()
                        return
                    glutPostRedisplay()
                    break
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not paused:
        camera_follow = not camera_follow

def idle():
    if not paused:
        glutPostRedisplay()

def setupCamera():
    if camera_follow:
        cam_x = player_pos[0] - camera_radius * math.sin(math.radians(player_angle))
        cam_z = player_pos[2] - camera_radius * math.cos(math.radians(player_angle))
    else:
        cam_x = player_pos[0] + camera_radius * math.cos(math.radians(camera_rotation_angle))
        cam_z = player_pos[2] + camera_radius * math.sin(math.radians(camera_rotation_angle))
    cam_y = player_pos[1] + camera_height
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(cam_x, cam_y, cam_z,
              player_pos[0], player_pos[1], player_pos[2],
              0, 1, 0)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_ground()
    draw_bushes()
    draw_player()
    draw_text(10, 770, "Infinite Ground Game")
    if paused:
        draw_settings_menu()
    glutSwapBuffers()

def main():
    global texture_id
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Infinite Ground Game")
    glClearColor(0.53, 0.81, 0.92, 1.0)  # Black background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)  # Enable texture mapping
    texture_data = generate_grass_texture()
    texture_id = load_texture(texture_data)
    glDisable(GL_TEXTURE_2D)  # Disable after setup
    init_bushes()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutMainLoop()

settings_menu_buttons = [
    {'text': 'Resume', 'x': 400, 'y': 500, 'w': 200, 'h': 50, 'action': 'resume'},
    {'text': 'Sound', 'x': 400, 'y': 400, 'w': 200, 'h': 50, 'action': 'toggle_sound'},
    {'text': 'Quit', 'x': 400, 'y': 300, 'w': 200, 'h': 50, 'action': 'quit'}
]

if __name__ == "__main__":
    main()