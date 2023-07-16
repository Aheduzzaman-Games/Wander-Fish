import pygame
from pygame.locals import *
import random
import time
import csv
import math
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()

width = 200
height = 200

screen = pygame.display.set_mode((width,height),pygame.FULLSCREEN)




clock = pygame.time.Clock()
fps = 100


font = pygame.font.SysFont(None,100)

global current_level 
current_level = 1
global level_finished
global player_rect
global p_rect
global player_action
player_action = 'idle'
player_rect = pygame.Rect(100,80,10,16)



game_map = []


	
	
	
global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global player_rect
    global p_rect
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc).convert()
        #animation_image.set_colorkey((255,255,255))
        
        
        p_rect = animation_image.get_rect()
        
        #print(player_action)
        if player_action == 'idle':
     
            player_rect = pygame.Rect(100,80,animation_image.get_width(),animation_image.get_height()+10)
        elif player_action == 'swim':
            player_rect = pygame.Rect(100,80,animation_image.get_width(),animation_image.get_height())
            print(player_action)
        animation_frames[animation_frame_id] = animation_image.copy()
        
        
        
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


animation_database['idle'] = load_animation('images/player/idle',[7,7,7,7,7,7,7,7,7,7,7,7,5,5,5,7,7,7,7,7])
animation_database['swim'] = load_animation('images/player/swim',[2,2,2,2,2,2,2,2,2,2,2,2])
animation_database['bubble_pop'] = load_animation('images/bubble_pop',[13,13,13,13,13,13])
animation_database['bubble_unpop'] = load_animation('images/bubble',[1])


#animation_database['swim'] = load_animation('images/player/swimR',[2,2,2,2,2,2,2,2,2,2,2,2])









class Player():
    def __init__(self,rect,action,frame):
        self.rect = rect
        
        self.action = action
        self.frame = frame
        self.flip_x = False
        self.flip_y = False
       
    def draw(self,angle):
        player_img_id = animation_database[self.action][self.frame]
        player_img = animation_frames[player_img_id]
        
        player_img_copy = pygame.transform.flip(player_img,self.flip_x,self.flip_y)
        
        self.player_image = pygame.transform.rotate(player_img_copy,angle)
        self.p_img_rect= self.player_image.get_rect()
        self.p_img_rect.center
        
        screen.blit(self.player_image,self.rect)
        
        
        
class Bubble():
        def __init__(self,x,y,action,frame):
            self.x = x
            self.y = y
            self.action = action
            self.frame = frame
            self.y_vel = 15
            self.rect = None
            
        def draw(self):
            self.y -= self.y_vel
            self.rect = pygame.Rect(self.x,self.y,512,512)
            bubble_img_id = animation_database[self.action][self.frame]
            bubble_image = animation_frames[bubble_img_id]
            screen.blit(bubble_image,(self.x,self.y))
        
        

def collision_test(rect,tiles):
	hit_list = []
	for tile in tiles:
		if rect.colliderect(tile):
			hit_list.append(tile)
	return hit_list
	
def move(rect,movement,tiles):
	collision_types = {'top' : False,'bottom' : False,'right' : False,'left' : False}
	rect.x += movement[0]
	hit_list = collision_test(rect,tiles)
	for tile in hit_list:
		if movement[0] > 0:
			rect.right = tile.left
			collision_types['right'] == True
		if movement[0] < 0:
			rect.left = tile.right
			collision_types['left'] == True
	rect.y += movement[1]
	hit_list = collision_test(rect,tiles)
	for tile in hit_list:
		if movement[1] > 0:
			rect.bottom = tile.top
			collision_types['bottom'] = True
		if movement[1] < 0:
			collision_types['top'] = True
			rect.top = tile.bottom
	return rect,collision_types
	





def main_menu():
	play_button = pygame.Rect(100,100,100,40)

	a = True
	
	while a:
		screen.fill((255,124,50))
		
		
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				if play_button.collidepoint(event.pos):
					a = False
		
		
		pygame.draw.rect(screen,(255,0,0),play_button)
		pygame.display.update()
		
	main()
		
def level_finished_congrats(screen):
	global current_level
	
	#screen.fill((0,255,0))
	congrats_text = font.render('CONGRATULATIONS\nYou Passed The Level',True,(255,255,0))
	next_text = font.render('Next', True,(255,255,255))
	screen.blit(congrats_text,(screen.get_width()/2-(congrats_text.get_width()/2),200))
	
	next_button = pygame.Rect(100,200,200,100)
	next_button.center = (screen.get_width()/2,400)
	
	pygame.draw.rect(screen,(144,255,24),next_button)
	screen.blit(next_text,(screen.get_width()/2-next_text.get_width()/2,400-next_text.get_height()/2))
	
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			if next_button.collidepoint(event.pos):
				level_finished = False
				current_level += 1
				main()
		
		
def game_over(screen):
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

	

def main():
	global player_rect
	global p_rect
	global player_action
	ang = 0
	mx,my = 0,0
	target_x,target_y = 0, 0
	
	bubble_time_counter = 0

	#sounds
	bubble_sound = pygame.mixer.Sound('music/bubble.wav')
	
	move_sound = pygame.mixer.Sound('music/move.mp3')

	
#	music = pygame.mixer.music.load('music.wav')
#	pygame.mixer.music.play(1)
#	pygame.mixer.music.set_volume(0.5)
		
		
	#buttons
	left_btn = pygame.Rect(20,screen.get_height()-70,50,50)
	right_btn = pygame.Rect(screen.get_width()-70,screen.get_height()-70,50,50)

	
	
	true_scroll = [0,0]

	screen_shake = 0
	

	moving = False
	
	
	moving_right = False
	moving_left = False
	jumping = False
	attack = False

	
	
#	weapon = 'gun'
	
	player_action = 'idle'
	bubble_action = 'bubble_unpop'
	player_flip_x = False
	player_flip_y = False
	player_frame = 0
	bubble_frame = 0
	
	
	bubbles = []

	
	last_time = time.time()
	
	
	keep_alive = True
	
	
	while keep_alive:
		
		screen.fill((50,150,255))
		
		dt = time.time() - last_time
		dt *= 20
		last_time = time.time()
	
	
		move_sound.set_volume(0.2)
		#jump_sound.set_volume(0.2)
		#point_sound.set_volume(0.2)
		


		true_scroll[0] += (player_rect.x-true_scroll[0]-152)#/parallax_value*dt
		true_scroll[1] += (player_rect.y-true_scroll[1]-106)#/parallax_value*dt
		
		scroll = true_scroll.copy()
		scroll[0] = int(scroll[0])
		scroll[1] = int(scroll[1])
		
		if screen_shake:
			scroll[0] += random.randint(0,4)-4
			scroll[1] += random.randint(0,4)-4
	



		#player_rect,collisions = move(player_rect,player_movement,tile_rects)
		
		bubble_time_counter += 1
		if bubble_time_counter >= 100:
		    bubbles.append(Bubble(random.randint(0,screen.get_width()),screen.get_height(),bubble_action,bubble_frame))
		    bubble_time_counter = 0
		    
		    
		for bubble in bubbles:
		    bubble.draw()
		    #screen.fill((25,34,44),bubble.rect)
		    
		    
		    if player_rect.colliderect(bubble.rect):
		        bubbles.remove(bubble)
		    if bubble.y <= -100:
		        bubbles.remove(bubble)
	
		player_frame += 1
		if player_frame >= len(animation_database[player_action]):
			player_frame = 0
			
		bubble_frame += 1
		if bubble_frame >= len(animation_database[bubble_action]):
			bubble_frame = 0
			
		player = Player(player_rect,player_action,player_frame)
		
		
        
		for ev in pygame.event.get():
			if ev.type == QUIT:
			   pygame.quit()
	
			if ev.type== MOUSEBUTTONDOWN:
				mx,my = pygame.mouse.get_pos()
				
				
				
				moving = True
				
			    
		if moving:
			mx,my = pygame.mouse.get_pos()
			t_x = player_rect.center[0]- mx
			t_y = player_rect.center[1]- my
			ang = (180/math.pi)*-math.atan2(t_y,t_x)
			
			
			
		    
		if mx > player_rect.center[0]:
		    player.flip_x = False
		    player.flip_y = True
		if mx < player_rect.center[0]:
		    player.flip_y = False
		    player.flip_x = False

		if player_rect.center[0] != mx:
		    player_rect.x -= target_x/20
		        
		if player_rect.center[1] != my:
		    player_rect.y -= target_y/20
		
		
		        
		screen.fill((255,44,33),player_rect)
		
		
		player.draw(ang)
		

		   
		if screen_shake > 0:
			screen_shake -= 1
			
			
		
		#screen.fill((253,55,77),player_rect)
				
		#drawing buttons
		screen.fill((255,255,0),right_btn)
		screen.fill((255,0,0,),left_btn)
		
		
			

		pygame.display.update()
		clock.tick(60)

main_menu()
	