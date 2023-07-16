import pygame
from pygame.locals import *
import random
import time
import csv
import math

pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()



width = pygame.display.Info().current_w
height = pygame.display.Info().current_h

screen = pygame.display.set_mode((width,height))





clock = pygame.time.Clock()
fps = 100


font = pygame.font.SysFont(None,100)

global current_level 
current_level = -1
global level_finished
global player_action
player_action = 'idle'
global level_states
level_states = {}


            
            
                
global move_sound
move_sound = pygame.mixer.Sound('music/move.mp3')





global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'

        animation_image = pygame.image.load(img_loc).convert_alpha()
        #animation_image.set_colorkey((0,0,0))
        
        
        
        
        animation_frames[animation_frame_id] = animation_image
        
        
        
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
        
        
    return animation_frame_data



def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
        

animation_database = {}


#player animation
animation_database['idle'] = load_animation('images/player/idle',[7,7,7,7,7,7,7,7,7,7,7,7,5,5,5,7,7,7,7,7])
animation_database['swim'] = load_animation('images/player/swim',[2,2,2,2,2,2,2,2,2,2,2,2])
#bubble animation
animation_database['bubble_pop'] = load_animation('images/bubble_pop',[13,13,13,13,13,13])
animation_database['bubble_unpop'] = load_animation('images/bubble',[1])

#enemy animation
animation_database['enemy_green'] = load_animation('images/enemy/enemy_green',[7,7,7,7,7,7])
animation_database['enemy_red'] = load_animation('images/enemy/enemy_red',[2,2,2,2,2,2,2,2,2,2,2,2])
animation_database['enemy_black'] = load_animation('images/enemy/enemy_black',[2,2,2,2,2,2,2,2,2,2,2,2])

#images
effect_img = pygame.image.load('images/others/text_img_bubble1.png').convert_alpha()










class Player():
    def __init__(self,x,y,action,frame,angle,flip_y):
        self.x = x
        self.y = y
        self.x_vel= 0
        self.y_vel = 0
        self.action = action
        self.frame = frame
        self.angle = angle
        self.flip_y = flip_y
        self.rect = None
        self.mask = None
        
    def draw(self):
        screen.blit(self.player_image,(self.x,self.y))
        
    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel
        
        player_img_id = animation_database[self.action][self.frame]
        player_img = animation_frames[player_img_id]
        p_image = pygame.transform.scale(player_img,(int(player_img.get_width()/3),int(player_img.get_height()/3)))
        
        player_img_copy = pygame.transform.flip(p_image,False,self.flip_y)
        self.player_image = pygame.transform.rotate(player_img_copy,self.angle)
        
        self.rect = pygame.Rect(self.x,self.y,self.player_image.get_width(),self.player_image.get_height())
        self.mask = pygame.mask.from_surface(self.player_image)
        

        
class Enemy():
    def __init__(self,x,y,action,frame,target_x,target_y,flip_x):
        self.x = x
        self.y = y
        self.action = action
        self.frame = frame
        self.target_x = target_x
        self.target_y = target_y
        self.x_vel= 0
        self.y_vel = 0
        self.angle = 0
        self.speed = 10
        self.flip_x = flip_x
        self.rect = None
        self.mask = None

    def update(self):
        self.angle = -math.atan2(self.target_y,self.target_x)*(180/math.pi)

        self.x_vel = math.cos(self.angle)*self.speed
        self.y_vel = math.sin(self.angle)*self.speed
        
        self.x += self.x_vel
        self.y += self.y_vel


        enemy_img_id = animation_database[self.action][self.frame]
        enemy_img = animation_frames[enemy_img_id]
        
        self.e_image = pygame.transform.scale(enemy_img,(int(enemy_img.get_width()/3),int(enemy_img.get_height()/3)))
        
        self.enemy_img_copy = pygame.transform.flip(self.e_image,self.flip_x,False)
        self.enemy_image = pygame.transform.rotate(self.enemy_img_copy,0)
        
        
        self.rect = pygame.Rect(self.x,self.y,self.enemy_image.get_width(),self.enemy_image.get_height())
        self.mask = pygame.mask.from_surface(self.enemy_image)
        
     
        
    def draw(self):
        screen.blit(self.enemy_image,(self.x,self.y))
        
    
        
class Bubble():
        def __init__(self,x,y,action,frame):
            self.x = x
            self.y = y
            self.action = action
            self.frame = frame
            self.y_vel = 8
            self.rect = None
            self.mask = None

        
        
        def draw(self):
            self.y -= self.y_vel
            self.rect = pygame.Rect(self.x,self.y,512,512)
            
            
            bubble_img_id = animation_database[self.action][self.frame]
            bubble_image = animation_frames[bubble_img_id]
            
            bubble_img = pygame.transform.scale(bubble_image,(int(bubble_image.get_width()/2),int(bubble_image.get_height()/2)))
            self.mask = pygame.mask.from_surface(bubble_img)
            
            screen.blit(bubble_img,(self.x,self.y))
        



class Button():
    def __init__(self,x, y, image, scaled_value,press_sound):
        self.img_width = image.get_width()
        self.img_height = image.get_height()
        self.image = pygame.transform.scale(image, (scaled_value))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.press_sound = press_sound


    def draw(self, surface):
        action = False
        
        
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            
                
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                self.press_sound.play()

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            

        
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action



effect_radius = 250

global m_x
global m_y
m_x,m_y = pygame.mouse.get_pos()

class Particle():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.init_x = random.randint(0,screen.get_width())
        self.init_y = random.randint(0,screen.get_height())
        self.size = 3
        self.speed = random.randint(10,50)
        self.distance = None
    def draw(self):
        if self.distance < effect_radius-5:
            self.size = 24
            #screen.blit(pygame.transform.scale(effect_img,(self.size*2,self.size*2)),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2))
            pygame.draw.circle(screen,(134,244,44),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2),self.size,width=3)
            
            pygame.draw.circle(screen,(254,255,255),(self.init_x-(effect_img.get_width()/2)-3,(self.init_y-effect_img.get_height()/2)-2),self.size/2.5)
            pygame.draw.circle(screen,(254,255,255),(self.init_x-(effect_img.get_width()/2)+7,self.init_y-(effect_img.get_height()/2)-1),self.size/3.5)
        elif self.distance <= effect_radius:
            self.size = 18
            #screen.blit(pygame.transform.scale(effect_img,(self.size*2,self.size*2)),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2))
            pygame.draw.circle(screen,(34,200,44),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2),self.size,width=2)
            pygame.draw.circle(screen,(254,255,255),(self.init_x-(effect_img.get_width()/2)-2,self.init_y-(effect_img.get_height()/2)-2),self.size/2.75)
        else:
            self.size = 14
            #screen.blit(pygame.transform.scale(effect_img,(self.size*2,self.size*2)),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2))
            pygame.draw.circle(screen,(34,244,114),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2),self.size,width=2)
            pygame.draw.circle(screen,(254,255,255),(self.init_x-effect_img.get_width()/2,self.init_y-effect_img.get_height()/2),self.size/3)
            
            
    def update(self):
        dx = m_x - self.init_x
        dy = m_y - self.init_y
        distance = math.sqrt(dx*dx + dy*dy)
        self.distance = distance
        force_direction_x = dx/distance
        force_direction_y = dy/distance
        max_distance = effect_radius
        force = (max_distance - distance) / max_distance
        direction_x = force_direction_x * force * self.speed
        direction_y = force_direction_y * force * self.speed
        if distance < effect_radius:
            self.init_x -= direction_x
            self.init_y -= direction_y
        else:
                #if self.x != self.base_x:
    #                dx = self.x - self.base_x
    #                self.x -= dx/5
    #            if self.y != self.base_y:
    #                dy = self.y - self.base_y
    #                self.y -= dy/5
                    
            if self.init_x != self.x:
                dx = self.init_x - self.x
                self.init_x -= dx/5
            if self.init_y != self.y:
                dy = self.init_y - self.y
                self.init_y -= dy/5




    



def percent(number,percentage,padding=0):
    num = int((number*percentage)/100)+padding
    return num


def level_finished_menu():
    global current_level
    
    #screen.fill((0,255,0))
    congrats_text = font.render('CONGRATULATIONS\nYou Passed The Level',True,(255,255,0))
    next_text = font.render('Next', True,(255,255,255))
    
    
    next_button = pygame.Rect(100,200,200,100)
    next_button.center = (screen.get_width()/2,400)
    level_finished_menu_running = True
    

    while level_finished_menu_running:
        
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(event.pos):
                    
                    current_level +=1
                    with open('level_states.ahed','w') as file:
                        if current_level == 2:
                            file.write('unlocked,unlocked,locked,locked')
                        elif current_level == 3:
                            file.write('unlocked,unlocked,unlocked,locked')
                        elif current_level == 4:
                            file.write('unlocked,unlocked,unlocked,unlocked')
                            
                            
                    main()

        pygame.draw.rect(screen,(144,255,24),next_button)
        screen.blit(next_text,(screen.get_width()/2-next_text.get_width()/2,400-next_text.get_height()/2))
        screen.blit(congrats_text,(screen.get_width()/2-(congrats_text.get_width()/2),200))
        
        
        print('level_finished ',clock.get_fps())
        
        pygame.display.update()
        clock.tick(60)

        
        
def game_over():
    #screen.fill((255,0,0))
    pygame.mixer.music.fadeout(1000)
    game_over_text = font.render('Game Over....You Lose',True,(255,255,0))
    retry_text = font.render('Retry :)', True,(255,255,255))
    screen.blit(game_over_text,(screen.get_width()/2-(game_over_text.get_width()/2),200))
    
    retry_button = pygame.Rect(100,200,200,100)
    retry_button.center = (screen.get_width()/2,400)
    
    pygame.draw.rect(screen,(0,255,0),retry_button)
    screen.blit(retry_text,(screen.get_width()/2-retry_text.get_width()/2,400-retry_text.get_height()/2))
    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if retry_button.collidepoint(event.pos):
                main()



def loading_screen(func):
    screen.fill((0,0,0))
    loading_text = font.render('Loading...',True,(255,24,52))
    screen.blit(loading_text,((screen.get_width()/2)-(loading_text.get_width()/2),(screen.get_height()/2)-(loading_text.get_height()/2)))
    
    func()
    


def tutorial_menu():
    background_image = pygame.image.load('images/others/icon.png').convert()
    background_image = pygame.transform.scale(background_image,(width,height))
    tutorial_menu_running = True
    
    while tutorial_menu_running:
        screen.fill((50,150,255))
        screen.blit(background_image,(0,0))
        
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                
                
            if ev.type== KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    main_menu()
                    
                    
        pygame.display.update()
        clock.tick(60)
       


def credits_menu():
    background_image = pygame.image.load('images/others/icon.png').convert()
    background_image = pygame.transform.scale(background_image,(width,height))
    credits_menu_running = True
    
    while credits_menu_running:
        screen.fill((50,150,255))
        screen.blit(background_image,(0,0))
        
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                
                
            if ev.type== KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    main_menu()
                    
                    
        pygame.display.update()
        clock.tick(60)
        
        
        
def about_menu():
    background_image = pygame.image.load('images/others/icon.png').convert()
    background_image = pygame.transform.scale(background_image,(width,height))
    about_menu_running = True
    
    while about_menu_running:
        screen.fill((50,150,255))
        screen.blit(background_image,(0,0))
        
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                
                
            if ev.type== KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    main_menu()
                    
                    
        pygame.display.update()
        clock.tick(60)
    
    
def level_menu():
    global current_level
    with open('level_states.ahed','r') as file:
        read_file = file.read()
        list = read_file.split(',')
        
        level_states['1'] = list[0]
        level_states['2'] = list[1]
        level_states['3'] = list[2]
        level_states['4'] = list[3]
        
    
    background_image = pygame.image.load('images/others/icon.png').convert()
    #cover_image = pygame.image.load('images/others/cover.png').convert_alpha()
    lock_image = pygame.image.load('images/others/lock2.png').convert_alpha()
    background_holder = pygame.image.load('images/background/level_background.png').convert_alpha()
    
    back_button_img = pygame.image.load('images/others/back_button.png').convert_alpha()
    
    
    level1_img = pygame.image.load('images/background/level1_button_background.png').convert()
    level2_img = pygame.image.load('images/background/level2_button_background.png').convert()
    level3_img = pygame.image.load('images/background/level3_button_background.png').convert()
    level4_img = pygame.image.load('images/background/level4_button_background.png').convert()




    level2_locked_img = pygame.image.load('images/background/level2_button_background_locked.png').convert()
    level3_locked_img = pygame.image.load('images/background/level3_button_background_locked.png').convert()
    level4_locked_img = pygame.image.load('images/background/level4_button_background_locked.png').convert()
    
    

    #level1_img = pygame.transform.scale(level1_img,(960,560))
    #background_holder = pygame.transform.scale(background_holder,(960,560))
    
    wrong_press = False
    #sounds
    bubble_sound = pygame.mixer.Sound('music/bubble.wav')
    bite_sound = pygame.mixer.Sound('music/bite.mp3')
    
    
    w_p_5 = percent(width,5)
    w_p_50 = percent(width,50)
    w_p_less = percent(width,2.5)
    
    
    if height > width:
        button_height = percent(height,15)
        h_p_pos1 = int(percent(height,50)-percent(height,30))
        h_p_pos2 = int(percent(height,50)-percent(height,10))
    else:
        button_height = percent(height,50)-percent(height,10)
        h_p_pos1 = percent(height,5)
        h_p_pos2 = int(percent(height,50)-percent(height,10))
        
    #buttons
    back_button = Button(20,20,back_button_img,(60,60),bubble_sound)
    
    
    level1_button = Button(w_p_5,h_p_pos1,level1_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
    
    if level_states['2'] == 'locked':
        level2_button = Button(int(w_p_50+w_p_less),h_p_pos1,level2_locked_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
    elif level_states['2'] == 'unlocked':
        level2_button = Button(int(w_p_50+w_p_less),h_p_pos1,level2_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
        
    if level_states['3'] == 'locked':
        level3_button = Button(w_p_5,h_p_pos2,level3_locked_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
    elif level_states['3'] == 'unlocked':
        level3_button = Button(w_p_5,h_p_pos2,level3_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
        
    if level_states['4'] == 'locked':
        level4_button = Button(int(w_p_50+w_p_less),h_p_pos2,level4_locked_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)
    elif level_states['4'] == 'unlocked':
        level4_button = Button(int(w_p_50+w_p_less),h_p_pos2,level4_img,(int(w_p_50-w_p_5*2+w_p_less),button_height),bubble_sound)

    msg_text = font.render(f'Play level {current_level} first',True,(34,90,221))

    
    running = True
    while running:
        screen.fill((0,0,0))
        screen.blit(pygame.transform.scale(background_image,(screen.get_width(),screen.get_height())),(0,0))
        #screen.blit(pygame.transform.scale(cover_image,(screen.get_width(),screen.get_height())),(0,0))

        





        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                
                
            if ev.type== KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    main_menu()
                    
            
 
        if level1_button.draw(screen):
                current_level = 1
                main()

        elif level2_button.draw(screen):
            if level_states['2'] == 'unlocked':
                    current_level = 2
                    main()
            elif level_states['2'] == 'locked':
                #level2_img = pygame.image.load('images/background/level2_button_background_locked.png')
                #screen.blit(pygame.transform.scale(lock_image,(int(w_p_50-w_p_5*2+w_p_less),button_height)),(700,100))
                wrong_press = True
                
        elif level3_button.draw(screen):
            if level_states['3'] == 'unlocked':
                current_level = 3
                main()

            elif level_states['3'] == 'locked':
                #screen.blit(pygame.transform.scale(lock_image,(int(w_p_50-w_p_5*2+w_p_less),button_height)),(200,400))
                wrong_press = True

        elif level4_button.draw(screen):
            if level_states['4'] == 'unlocked':
                current_level = 4
                main()

            elif level_states['4'] == 'locked':
                #screen.blit(pygame.transform.scale(lock_image,(int(w_p_50-w_p_5*2+w_p_less),button_height)),(700,400))
                wrong_press = True
                
                
                
        elif back_button.draw(screen):
            main_menu()
        
        
        screen.blit(pygame.transform.scale(background_holder,(int(w_p_50-w_p_5*2+w_p_less+15),button_height+10)),(w_p_5-10,h_p_pos1-10))

        
        if wrong_press == True:
            screen.blit(msg_text,(0,0))
            
            
        ###print('wrong press = ',wrong_press)
        print('level_menu ',clock.get_fps())

        pygame.display.update()
        clock.tick(60)

                


def main_menu():

    global player_action
    
    player_x,player_y = 200,200


    mx,my = 0,0
    pos = []

    
    scale = 0.35
    life = 3

    
    bubble_time_counter = 0
    enemy_time_counter = 0
    
    #images
    background_image = pygame.image.load('images/background/background_1.png').convert()
    #cover_image = pygame.image.load('images/others/cover.png').convert_alpha()

    play_button_image = pygame.image.load('images/others/play_button.png').convert_alpha()
    tutorial_button_image = pygame.image.load('images/others/tutorial_button.png').convert_alpha()
    about_button_image = pygame.image.load('images/others/about_button.png').convert_alpha()
    credits_button_image = pygame.image.load('images/others/credits_button.png').convert_alpha()
    
    
    #sounds
    bubble_sound = pygame.mixer.Sound('music/bubble.wav')
    move_sound = pygame.mixer.Sound('music/move.mp3')
    bite_sound = pygame.mixer.Sound('music/bite.mp3')
    
    
    music = pygame.mixer.music.load('music/music.mp3')
    pygame.mixer.music.play(1)
    pygame.mixer.music.set_volume(0.5)

    
    h_p_5 = percent(height,5)
    h_p_50 = percent(height,50)
    
    #buttons
    play_button = Button(screen.get_width()/2-((play_button_image.get_width()*scale)/2),h_p_50-350,play_button_image,(200,100),bubble_sound)
    tutorial_button = Button(screen.get_width()/2-((tutorial_button_image.get_width()*scale)/2),h_p_50-270,tutorial_button_image,(200,100),bubble_sound)
    credits_button = Button(screen.get_width()/2-((credits_button_image.get_width()*scale)/2),h_p_50-190,credits_button_image,(200,100),bubble_sound)
    about_button = Button(screen.get_width()/2-((about_button_image.get_width()*scale)/2),h_p_50-110,about_button_image,(200,100),bubble_sound)

    
    
#   music = pygame.mixer.music.load('music.wav')
#   pygame.mixer.music.play(1)
#   pygame.mixer.music.set_volume(0.5)
        
    
    
    
    
    
    
    player_action = 'idle'
    bubble_action = 'bubble_unpop'
    enemy_action = ['enemy_green','enemy_red','enemy_black']
    player_flip_y = False
    enemy_flip_x = False
    player_frame = 0
    bubble_frame = 0
    enemy_frame = 0
    

    counter = 0
    
    
    bubbles = []
    enemies = []

    

    
    last_time = time.time()
    
    keep_alive = True
    
    while keep_alive:
        
        screen.fill((50,150,255))

        counter += 1
        if counter >= 100:
            pos.append([random.randint(0,screen.get_width()),random.randint(0,screen.get_height())])
            counter = 0



        for p in pos:
            mx,my = p[0],p[1]


        rand_e_pos = random.choice([0,screen.get_width()])
        screen.blit(pygame.transform.scale(background_image,(screen.get_width(),screen.get_height())),(0,0))




        
        dt = time.time() - last_time
        dt *= 20
        last_time = time.time()

       
 
        #player_rect,collisions = move(player_rect,player_movement,tile_rects)

        
        bubble_time_counter += 1
        if bubble_time_counter >= random.randint(25,75):
            bubbles.append(Bubble(random.randint(0,screen.get_width()-50),screen.get_height(),bubble_action,bubble_frame))
            bubble_time_counter = 0 


        enemy_time_counter += 1
        if enemy_time_counter >= random.randint(100,150):
            enemies.append(Enemy(rand_e_pos,random.randint(0,screen.get_height()),random.choice(enemy_action),enemy_frame,random.randint(0,screen.get_width()),random.randint(0,screen.get_height()),enemy_flip_x))
            enemy_time_counter = 0
            
            
            
        
            
    
        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0


            
        
        target_x = player_x- mx
        target_y = player_y- my
        ang = (180/math.pi)*-math.atan2(target_y,target_x)
            
            
        player = Player(player_x,player_y,player_action,player_frame,ang,player_flip_y)
        
        player.update()
    
        
                
       
            
            #player_action,player_frame = change_action(player_action,player_frame,'swim')
            
            
            
            
            
    
            
        if mx > player.rect.center[0]:
            player_flip_y = True
           
        if mx < player.rect.center[0]:
            player_flip_y = False
            

        if player.rect.center[0] != mx:
            player_x -= target_x/15
                
        if player.rect.center[1] != my:
            player_y -= target_y/15
            


        #screen.fill((255,66,33),player.rect)
        
        
        player.draw()
        
        
        
        for bubble in bubbles:
            bubble.draw()
            if bubble.y < -300:
                bubbles.remove(bubble)
            
            if player.rect.colliderect(bubble.rect):
                
                if player.mask.overlap(bubble.mask,(int(bubble.x-player_x),int(bubble.y-player_y))):
                    
                    bubble_sound.play()
                    bubbles.remove(bubble)

        for enemy in enemies:
            enemy.update()
            enemy.draw()
            
            if enemy.x >= screen.get_width()+100 or enemy.x <= -100:
                enemies.remove(enemy)
                
            if player.rect.colliderect(enemy.rect):
                if player.mask.overlap(enemy.mask,(int(enemy.x-player_x),int(enemy.y-player_y))):
                    life -= 1
                    enemies.remove(enemy)
                

            
            if enemy.x_vel >= 0: 
                enemy.flip_x = True
            else:
                enemy.flip_x = False


            



              
        if play_button.draw(screen):
            level_menu()
        if tutorial_button.draw(screen):
            tutorial_menu()
        if credits_button.draw(screen):
            pass
        if about_button.draw(screen):
            pass

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()

            

        #screen.blit(pygame.transform.scale(cover_image,(screen.get_width(),screen.get_height())),(0,0))
#        play_button.draw(screen)
#        tutorial_button.draw(screen)
#        credits_button.draw(screen)
#        about_button.draw(screen)
        #screen.fill((253,55,77),player.rect)
                
        #drawing buttons
        #screen.fill((255,255,0),right_btn)
        #screen.fill((255,0,0,),left_btn)
        
        
        
        
        print('main_menu ',clock.get_fps())
        

        pygame.display.update()
        clock.tick(60)
    
    
    

        
        

def main():
    

                
                
    global m_x,m_y        
    global player_action
    global current_level
    particles = []
    ang = 0
    mx,my = 0,0
    target_x,target_y = 0, 0
    player_x,player_y = 200,200

    Font = pygame.font.SysFont(None,400)
    score = 0
    target = 0
    life = 3

    
    
    bubble_time_counter = 0
    enemy_time_counter = 0
    
    bubble_time_range =  (25,75)
    if height > width:
        bubble_time_range = (25,50)
    enemy_time_range = (30,100)
    
    #images
    background_image = pygame.image.load('images/background/background_'+str(current_level)+'.png').convert()
    
    back_button_img = pygame.image.load('images/others/back_button.png').convert_alpha()
    
    #lifebar_holder = pygame.image.load('images/others/lifebar_holder.png')
    
    
    
    #sounds
    bubble_sound = pygame.mixer.Sound('music/bubble.wav')
    bite_sound = pygame.mixer.Sound('music/bite.mp3')
    
    
    pygame.mixer.music.play(1)
    pygame.mixer.music.set_volume(0.5)


    #button
    back_button = Button(20,20,back_button_img,(60,60),bubble_sound)
    
    
    
    
    
    true_scroll = [0,0]

    screen_shake = 0
    

    moving = False
    
    
    
    jumping = False
    attack = False

    
    
    
    
    
    player_action = 'idle'
    bubble_action = 'bubble_unpop'
    enemy_action = ['enemy_green','enemy_red','enemy_black']
    player_flip_y = False
    enemy_flip_x = False
    player_frame = 0
    bubble_frame = 0
    enemy_frame = 0
    
    if current_level == 1:
        target = 20
    elif current_level == 2:
        target = 40

    elif current_level == 3:
        target = 20

    elif current_level == 4:
        target = 100
    
    target_text = font.render(str(target),True,(12,12,12))
    
    text = ['L','E','V','E ','L ',str(current_level)]
    
    
    bubbles = []
    enemies = []


    
    last_time = time.time()
    
    keep_alive = True
    
    while keep_alive:
        screen.fill((50,150,255))
        #m_x,m_y = pygame.mouse.get_pos()
        
        lifebar_img = pygame.image.load('images/others/lifebar_' + str(life) + '.png').convert_alpha()    
        lifebar_image = pygame.transform.scale(lifebar_img,(200,60))
        
        
        
        current_time = int(time.time() - last_time)
        
        
        
        
        
        rand_e_pos = random.choice([-50,screen.get_width()+50])
        rand_tx_pos = random.choice([-50,screen.get_width()+50])
        
        screen.blit(pygame.transform.scale(background_image,(screen.get_width(),screen.get_height())),(0,0))

        passed_time = font.render(str(current_time),True,(12,12,12))


        score_text = font.render(str(score),True,(12,12,12))
        


        


        
        #dt = time.time() - last_time
        #dt *= 20
        

        
        move_sound.set_volume(0.2)
        

        
        if screen_shake:
            scroll[0] += random.randint(0,4)-4
            scroll[1] += random.randint(0,4)-4
            
            
        

        #player_rect,collisions = move(player_rect,player_movement,tile_rects)

        
        bubble_time_counter += 1
        if bubble_time_counter >= random.randint(bubble_time_range[0],bubble_time_range[1]):
            bubbles.append(Bubble(random.randint(0,screen.get_width()-50),screen.get_height(),bubble_action,bubble_frame))
            bubble_time_counter = 0 

        #enemy controls
        if current_level == 1:
            enemy_time_range = (75,140)
        elif current_level == 2:
            enemy_time_range = (50,100)
        elif current_level == 3:
            enemy_time_range = (30,80)
        elif current_level == 4:
            enemy_time_range = (25,70)
            
        enemy_time_counter += 1
        if enemy_time_counter >= random.randint(enemy_time_range[0],enemy_time_range[1]):
            enemies.append(Enemy(rand_e_pos,random.randint(0,screen.get_height()),random.choice(enemy_action),enemy_frame,rand_tx_pos,random.randint(0,screen.get_height()),enemy_flip_x))
            enemy_time_counter = 0
            
            
            
    
        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0
            
        
            
            
        player = Player(player_x,player_y,player_action,player_frame,ang,player_flip_y)
        
        player.update()
        
        
        pygame.event.set_allowed([KEYDOWN,MOUSEBUTTONDOWN])
        for ev in pygame.event.get():
            if ev.type == QUIT:
               pygame.quit()
            
            
            if ev.type== MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                
                t_x = player.rect.center[0]- mx
                t_y = player.rect.center[1]- my
                ang = (180/math.pi)*-math.atan2(t_y,t_x)
                
                moving = True

            if ev.type== KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    main_menu()
                
        
        
        
        if moving:
            
            #player_action,player_frame = change_action(player_action,player_frame,'swim')
            
            target_x = player.rect.center[0]- mx
            target_y = player.rect.center[1]- my
            
            
            
    
            
        if mx > player.rect.center[0]:
            player_flip_y = True
           
        if mx < player.rect.center[0]:
            player_flip_y = False
            

        if player.rect.center[0] != mx:
            player_x -= target_x/15
                
        if player.rect.center[1] != my:
            player_y -= target_y/15
            


        #screen.fill((255,66,33),player.rect)
        
        
        player.draw()
        
        
        
        for bubble in bubbles:
            bubble.draw()
            if bubble.y < -300:
                score -= 5
                bubbles.remove(bubble)
            
            if player.rect.colliderect(bubble.rect):
                
                if player.mask.overlap(bubble.mask,(int(bubble.x-player_x),int(bubble.y-player_y))):
                    score += 10
                    bubble_sound.play()
                    bubbles.remove(bubble)

        for enemy in enemies:
            enemy.update()
            enemy.draw()
            
            if enemy.x >= screen.get_width()+100 or enemy.x <= -100:
                enemies.remove(enemy)
                
            if player.rect.colliderect(enemy.rect):
                if player.mask.overlap(enemy.mask,(int(enemy.x-player_x),int(enemy.y-player_y))):
                    life -= 1
                    bite_sound.play()
                    enemies.remove(enemy)
                

            
            if enemy.x_vel >= 0: 
                enemy.flip_x = True
            else:
                enemy.flip_x = False


            

        m_x,m_y = player.rect.x+player.player_image.get_width()/2,player.rect.y+player.player_image.get_height()/2
        
        for t in text:
            txt = Font.render(t,True,(255,35,36))
            mask = pygame.mask.from_surface(txt)
            
            #screen.blit(text,(300+160*txt.index(t),300))
            outline = [(p[0]+percent(width,5)+int((width/6.2))*text.index(t) ,p[1]+(screen.get_height()/2)-txt.get_height()/2) for p in mask.outline(27)]
            
            #pygame.draw.lines(screen,(0,35,250),False,outline,3)
            ###print(len(outline))
            
            for pos in outline:
                if len(particles)< 220:
                    particles.append(Particle(pos[0],pos[1]))
              
        for particle in particles:
            
            particle.update()
            particle.draw()
        
            
        




        if score >= target:
            level_finished_menu()
                    
                                         
                
        
        
           
        if screen_shake > 0:
            screen_shake -= 1

        if life <= 0:
            game_over()
            
        
    
        #drawing button
        if back_button.draw(screen):
            level_menu()
            
        screen.blit(score_text,((screen.get_width()/2)-2,0))
        screen.blit(passed_time,((screen.get_width())-passed_time.get_width()-10,0))
        
        screen.blit(lifebar_image,(150,20))
        screen.blit(target_text,((screen.get_width()/2)-2,screen.get_height()-target_text.get_height()-8))
        
        #print(current_level)
        ##print('last_time ',last_time)
        print('main ',clock.get_fps())
        
        
        pygame.display.update()
        clock.tick(100)

main_menu()
    
