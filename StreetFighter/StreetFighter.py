#Street Fighter Solo Project
#Brodie Milne
#todo:
'''
-add health bars and timer
'''


import pygame,random,time,math
from pygame.locals import *
from sys import exit
pygame.init()
pygame.joystick.init()

#create screen
windowSurfaceObj = pygame.display.set_mode((1024,490))
pygame.display.set_caption('Street Fight')
BG = pygame.image.load("TitleBG.png") 
windowSurfaceObj.blit(BG,(0,0))


Winner = [(pygame.font.SysFont("Bahnshrift semibold",45).render(("WINNER WINNER CHICKEN DINNER!!"),10,(0,0,0))),(pygame.font.SysFont("monospace",45).render((""),10,(0,255,0)))]


#create general variables
FPSclock = pygame.time.Clock()
RunGame = False
LoadGame = False
LoadTimer = pygame.time.get_ticks()
Player = []
joystick_count = pygame.joystick.get_count()
WinState = 0
print (joystick_count)
#create sprite group names
HeadGroup = pygame.sprite.Group()
BodyGroup = pygame.sprite.Group()
PunchGroup = pygame.sprite.Group()
KickGroup = pygame.sprite.Group()


#---Player character class---#
class Controls:
	def __init__(self, num):
	#-General Variables-#
		self.joystick = pygame.joystick.Joystick(num) 
		self.joystick.init()
		self.ID = num
	#-Movement Variables-#
		self.X = (1000/pygame.joystick.get_count()) * num
		self.Y = 295
		self.speed = 8
		self.VelocityY = 0
		self.VelocityX = 0
		self.GravityY = 0.5 # change this to increase or decrese the speed/ rate of fall
		self.GravityX = 0.25 #change this to speed up or slow down recovery from knock back
		self.Xprev = self.X
		
		self.counterp = 0
		self.counterk = 0
		
		self.HP = 100
		self.last_punch = pygame.time.get_ticks()
		self.PunchCoolDown = 250
		self.last_kick = pygame.time.get_ticks()
		self.KickCoolDown = 1000
		self.lastjump = pygame.time.get_ticks()
		self.jumpcooldown = 600
		
	#-image variables-#
		self.flip = False
		self.Moving1 =pygame.image.load("FighterMovingA" + str(num) + ".png").convert_alpha()
		self.Moving2 =pygame.image.load("FighterMovingB" + str(num) + ".png").convert_alpha()
		self.Move = []
		self.PunchAnimate = []
		self.KickAnimate = []
		self.Playeri = pygame.image.load("FighterStandStill" + str(num) + ".png").convert_alpha()
		self.punch = pygame.image.load("FighterPunch"+str(num)+".png").convert_alpha()
		self.kick = pygame.image.load("FighterKick"+str(num)+".png").convert_alpha()
		self.state = 0
		self.action = "none"
		self.direction = 1
		self.frame = 0
		self.atkframe = 0

#get variable functions
	def get_X(self):
		return int(self.X)
	def get_Y(self):
		return int(self.Y)
	def get_HeadX(self):
		return int(self.X + 15)
	def get_HeadY(self):
		return int(self.Y +5)
	def get_BodyX(self):
		return int(self.X + 13)
	def get_BodyY(self):
		return int(self.Y +20)
	def get_action(self):
		return self.action
	def get_direction(self):
		if self.direction == 1:
			return 40
		elif self.direction == (-1):
			return -9


	def Flip(self):
	#this function will orient the players character correctly without having to make a bunch of new sprties
	#it does this by checking the direction inputed by the user and if its already been flipped or not
	#to add more images and to flip orientation jsut add more lines with pygame.transform.flip()
		if self.joystick.get_axis(0) >= 0.15 and self.flip == True:
			self.Moving1 = pygame.transform.flip(self.Moving1,True,False)
			self.Moving2 = pygame.transform.flip(self.Moving2,True,False)
			self.Playeri = pygame.transform.flip(self.Playeri,True,False)
			self.punch = pygame.transform.flip(self.punch,True,False)
			self.kick = pygame.transform.flip(self.kick,True,False)
			self.flip = False
			self.direction = (1)
		elif self.joystick.get_axis(0) < -0.15 and self.flip == False:
			self.Moving1 = pygame.transform.flip(self.Moving1,True,False)
			self.Moving2 = pygame.transform.flip(self.Moving2,True,False)
			self.Playeri = pygame.transform.flip(self.Playeri,True,False)
			self.punch = pygame.transform.flip(self.punch,True,False)
			self.kick = pygame.transform.flip(self.kick,True,False)
			self.flip = True
			self.direction = (-1)

	def movement(self):
		#gravity and jump checks
		#if the button is pressed and on ground jump!
		nowjump = pygame.time.get_ticks()
		if self.joystick.get_button(0) == 1 and self.Y ==295 and nowjump - self.lastjump >= self.jumpcooldown:
			self.lastjump = nowjump
			#make the velocity upawrds a number and move the character up that initial jump height
			self.VelocityY = 6	#change this to increase initial jump height
			self.Y-= self.VelocityY
		
		#depeneding on if there is any movement change the x value by that much
		if self.joystick.get_axis(0) > 0.15 or self.joystick.get_axis(0) < -0.15: #<> creates a dead zone equal on all controllers
			if self.X < 0 :
				self.X = 0
			elif self.X > 974:
				self.X = 974
			else:
				self.X += float(self.joystick.get_axis(0)*(self.speed)) #change value to increase or decrease speed of character movement
			self.action = "Move"
		else:
			self.X += 0
			self.action="none"


		if self.counterp >0:
			self.counterp -=1
			self.action="punch"
		elif self.counterk > 0:
			self.counterk -=1
			self.action = "kick"

	
	def Gravity(self):
		if self.Y <295: #apply gravity to the character if they are higher than the ground
			self.VelocityY -= self.GravityY
			self.Y -= self.VelocityY
		if self.Y >= 296:
			self.Y = 295
			self.VelocityY = 0
	
	def Knocked(self):
		if self.X < 0 :
			self.X = 0
			self.VelocityX = 0
		elif self.X > 974:
			self.X = 974
			self.VelocityX = 0
		else:
			self.VelocityX = self.VelocityX + self.GravityX
			self.X = self.X + self.VelocityX

		if self.VelocityX == 0:
			self.VelocityX = 0
			self.GravityX = 0
			self.action = "none"
			
	def KnockBackP(self,ATKX,PLRX):
		if self.X < 0 :
			self.X = 0
		elif self.X > 974:
			self.X = 974
		else:
			if ATKX >=PLRX:
				print("ATKX" + str(ATKX))
				print("PLRX" + str(PLRX))
				self.GravityX = 1
				self.VelocityX = (-13)
				self.VelocityY = 1
			elif ATKX < PLRX:
				print("ATKX" + str(ATKX))
				print("PLRX" + str(PLRX))
				self.GravityX = -1
				self.VelocityX = (12)
				self.VelocityY = 2
			self.X += self.VelocityX
			self.Y-= self.VelocityY
			self.action = "Knocked"
		
	def KnockBackK(self,ATKX,PLRX):
		if self.X < 0 :
			self.X = 0
		elif self.X > 974:
			self.X = 974
		else:
			if ATKX >=PLRX:
				print("ATKX" + str(ATKX))
				print("PLRX" + str(PLRX))
				self.GravityX = 1
				self.VelocityX = (-15)
				self.VelocityY = (3)
			elif ATKX < PLRX:
				print("ATKX" + str(ATKX))
				print("PLRX" + str(PLRX))
				self.GravityX = -1
				self.VelocityX = (15)
				self.VelocityY = (3)
			self.X += self.VelocityX
			self.Y-= self.VelocityY
			self.action = "Knocked"

	
	def attack(self):
	#function called for all types of attacks
	#this will check what button is pressed and draw its attack based on that
		Button = self.joystick
		nowPunch = pygame.time.get_ticks()
		nowKick = pygame.time.get_ticks()
		#section for punch command On button A on XBox controller
		if Button.get_button(2) == 1 and nowPunch - self.last_punch >= self.PunchCoolDown:
			print("punch")
			self.last_punch = nowPunch
			self.counterp = 4
			
		#section for Kick command on button B on XBox controller
		if Button.get_button(1) == 1 and nowKick - self.last_kick >= self.KickCoolDown:
			self.last_kick = nowKick
			print("kick")
			self.action = "kick"
			self.counterk = 6

	def Health(self,dmg,d):
	#takes health from players hit by attacks and if the player is at 0 removes them from the game
		self.HP -= dmg
		if self.HP <= 0:
			self.X = 10000
			self.Y = 10000
			Player.pop(d)
			

	def draw(self):

	#moving and stand still drawing
	#state is determined from the last action taken
	#depending on state draw a different image
		if self.action == "none" :#stand Still
			windowSurfaceObj.blit(self.Playeri, (self.X, self.Y))
			self.frame = 0
		elif self.action == "Move":#move animation
		#to attempt to animate, every run through o f the loop will blit the opposite walking frame if a walking frame is needed

			self.Move = [self.Moving1,self.Moving2]
			if self.frame  +1 >= 4:
				self.frame = 0
			windowSurfaceObj.blit(self.Move[self.frame//2],(self.X,self.Y))
			self.frame += 1
		
		
		elif self.action == "punch":#punch
			windowSurfaceObj.blit(self.punch,(self.X,self.Y))
		elif self.action == "kick":#kick
			windowSurfaceObj.blit(self.kick,(self.X,self.Y))
		elif self.action == "Knocked":
			windowSurfaceObj.blit(self.Playeri, (self.X, self.Y))
			self.frame = 0
		pygame.draw.line(windowSurfaceObj, (255,0,0),(self.X + 49,self.Y-2),(self.X + self.HP/2,self.Y-2), 5)#health taken
		pygame.draw.line(windowSurfaceObj, (0,255,0),(self.X,self.Y-2),(self.X + self.HP/2,self.Y-2), 5)#health remaining
		windowSurfaceObj.blit((pygame.font.SysFont("monospace",20).render("P" + str(self.ID +1),5,(0,255,255))),(self.X +13,self.Y-22))#player number icon

	#check for winner
		global WinState
		#Proccess for animation same for all animations in game
		if len(Player) == 1:
			if WinState +1 >= 128: #change number to speed up or slow down animation
				WinState = 0
			windowSurfaceObj.blit(Winner[WinState//64],(250,50)) #number after // must be a)divisable by the larger num above, b)the result must be within your sprite count 
			WinState += 1										  #(in my case i have 2 sprites therefore i must keep it within 2 as teh result)


#-create controlers-#
#create and add controllers to the list of available controllers plugged in
for d in range(joystick_count):
	Player.append(Controls(d)) # Controller(0),  Controller(1), Controller(2), Controller(3),







#----Map Selection Screen----#
Setup = False
CN = 0
Map = 0
pos = [0,0]
MapNum = []
PrevMap = 0
NextMap= 0
Black = (0,0,0)
BlankVar = 0
class MapSelect:
	def __init__(self,x):
		self.ID = x
	def Scroll (self,PrevID,NextID):
		pygame.draw.rect(windowSurfaceObj, (0,0,255), (410, 193, 258, 125), 20)
		windowSurfaceObj.blit(pygame.image.load("Thumb"+str(self.ID)+".png"),(412,195))#mid picture
		windowSurfaceObj.blit(pygame.image.load("Thumb"+str(PrevID)+".png"),(112,295))#left Picture
		windowSurfaceObj.blit(pygame.image.load("Thumb"+str(NextID)+".png"),(712,295))#right Ricture
		 

def SelectMap(Map):
	global Setup,LoadGame,BG
	Setup = True
	LoadGame = True
	RunGame = False
	LoadTimer = pygame.time.get_ticks()
	BG = pygame.image.load("Map" + str(Map) + ".png")

for b in range(6): #4 indicates number of avaliable maps ---change to ad more map options
	MapNum.append(MapSelect(b))

def RndMap():
	#select a random map
	SelectMap((random.randint(0,len(MapNum)-1)))	
		

while Setup == False:
	FPSclock.tick(5)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			Setup = True
	windowSurfaceObj.blit(BG,(0,0))
	#-display instructions for level select screen-#
	windowSurfaceObj.blit(pygame.font.SysFont("monospace",45).render(("Select A Map"),50,(255,125,0)),(380,100))
	windowSurfaceObj.blit(pygame.image.load("Ybtn.png").convert_alpha(),(800,50))
	windowSurfaceObj.blit(pygame.font.SysFont("monospace",20).render(("Random Map"),50,(255,125,0)),(830,52))
	windowSurfaceObj.blit(pygame.image.load("Leftbtn.png").convert_alpha(),(800,100))
	windowSurfaceObj.blit(pygame.font.SysFont("monospace",20).render(("Scroll Left"),50,(255,125,0)),(830,102))
	windowSurfaceObj.blit(pygame.image.load("Rightbtn.png").convert_alpha(),(800,150))
	windowSurfaceObj.blit(pygame.font.SysFont("monospace",20).render(("Scroll Right"),50,(255,125,0)),(830,152))
	windowSurfaceObj.blit(pygame.image.load("Abtn.png").convert_alpha(),(800,200))
	windowSurfaceObj.blit(pygame.font.SysFont("monospace",20).render(("Select Map"),50,(255,125,0)),(830,202))
	
	
	for d in range(joystick_count):
		joystick = pygame.joystick.Joystick(d)
		pos = list(joystick.get_hat(0))
		CN += pos[0]
		PrevMap = (CN -1)%6
		Map = (CN)%6
		NextMap = (CN +1)%6
		
		MapNum[Map].Scroll(PrevMap,NextMap)

		if joystick.get_button(0) == 1: #press A to select the current map
			SelectMap(Map)
		elif joystick.get_button(3) ==1: #press Y to select a random map
			RndMap()

	MapNum[Map].Scroll(PrevMap,NextMap)

	pygame.display.update()



#--Load screen--#
#Display a quick how to play screen while game "Loads"
LoadCounter = 0
while LoadGame == True:

	windowSurfaceObj.blit(pygame.image.load("LoadScreen.png").convert_alpha(),(0,0))
	if LoadCounter >= 200:
		windowSurfaceObj.blit(pygame.font.SysFont("monospace",20).render(("Continue..."),50,(255,125,0)),(400,302))
		for event in pygame.event.get():
			if event.type == pygame.JOYBUTTONDOWN:
				LoadGame = False
				RunGame = True
	else:
		LoadCounter += 1
	pygame.display.update()
	





#----------Sprite Collision------------#

#Classes for object sprite collision (only used when collision is reuired)
#each class will create a "hit box" to place on the screen as an area to compare to other "hitboxes"
#each class takes a colour and position to create the HB at
class Heads(pygame.sprite.Sprite):
	def __init__(self,color,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([20,13])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = pos

class Bodys(pygame.sprite.Sprite):
	def __init__(self,color,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([25,30])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = pos

class Punchs(pygame.sprite.Sprite):
	def __init__(self,color,X,Y,Loc):
		self.X = Loc
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([20,13])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = [X,Y]
	def get_X(self):
		return self.X

class Kicks(pygame.sprite.Sprite):
	def __init__(self,color,X,Y,Loc):
		self.X = Loc
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([20,18])
		self.image.fill(color)
		self.rect = self.image.get_rect()
		self.rect.topleft = [X,Y]
	def get_X(self):
		return self.X

def collision():
###this funcction is the main  part of the code for collision detection
	
	#step one: Clear the sprite groups of outdated sprites
	HeadGroup.empty()
	BodyGroup.empty()
	PunchGroup.empty()
	KickGroup.empty()

	BodyBox = []
	HeadBox = []
	PunchBox = []
	KickBox = []

	#step two: Create objects and add them to there respective group
	for d in range(len(Player)):
		#first is the head and body boxes
		#each head/body gets created as new object in there respective class
		#we send the colour of the HB, and the x and y locations of the players head/body
		#next add the created head/body HB to a sprite group
		#finaly also add the sprite to a list to be accesed based on indexes later
		Head =  Heads((255,0,0), [Player[d].get_HeadX(),Player[d].get_HeadY()])
		HeadGroup.add(Head)
		HeadBox.append(Head)
		Body =  Bodys((255,0,0), [Player[d].get_BodyX(),Player[d].get_BodyY()])
		BodyGroup.add(Body)
		BodyBox.append(Body)
		
		#Next is the punch and kick boxes if there are any to make
		#we repeat the eact same process as we did for head/body HB
		#only difference is that we check the sate set by the player input to see if an attack was made
		if Player[d].get_action() == "punch":
			Punch =  Punchs((255,0,0), (Player[d].get_X()+Player[d].get_direction()), (Player[d].get_Y()+19),(Player[d].get_X()))
			PunchGroup.add(Punch)
			PunchBox.append(Punch)
		if Player[d].get_action() == "kick":
			Kick =  Kicks((255,0,0), (Player[d].get_X()+Player[d].get_direction()), (Player[d].get_Y()+25),(Player[d].get_X()))
			KickGroup.add(Kick)
			KickBox.append(Kick)


	#to draw hit boxes uncomment below
		#HeadGroup.draw(windowSurfaceObj)
		#BodyGroup.draw(windowSurfaceObj)
		#PunchGroup.draw(windowSurfaceObj)
		#KickGroup.draw(windowSurfaceObj) 


	#step three: check collision with each body/head and take damage accordingly
	for d in range(len(Player)):
		#for each player go through each check
		#step 1: check for a collision between the current players head/body and any punch/kick box
		#step 2: go through all avaliable punch/kick boxes and determine which one collided from which player
		#step 3 send the respective knockback function both the player that got hit (Player[d]) and the player that hit (Plyaer[f]) X position
		#Step 4: subtract health from the player hit
		#repeat for all cases of collision
		
		#Body + Punch
		if  pygame.sprite.spritecollideany(BodyBox[d],PunchGroup):	
			for f in range(len(PunchBox)):
				if pygame.sprite.collide_rect(BodyBox[d],PunchBox[f]):
					Player[d].KnockBackP(PunchBox[f].get_X(), Player[d].get_X())
					Player[d].Health(4,d)
					#print ("Body Shot")
					
		#Body + Kick
		if  pygame.sprite.spritecollideany(BodyBox[d],KickGroup):
			for f in range(len(KickBox)):
				if pygame.sprite.collide_rect(BodyBox[d],KickBox[f]):
					Player[d].KnockBackK(KickBox[f].get_X(), Player[d].get_X())
					Player[d].Health(6,d)
					#print ("Body Shot")
					
		#Head + Punch
		if  pygame.sprite.spritecollideany(HeadBox[d],PunchGroup):
			for f in range(len(PunchBox)):
				if pygame.sprite.collide_rect(HeadBox[d],PunchBox[f]):
					Player[d].KnockBackP(PunchBox[f].get_X(), Player[d].get_X())
					Player[d].Health(8,d)
					#print ("Head Shot")
					
		#Head + Kick	
		if  pygame.sprite.spritecollideany(HeadBox[d],KickGroup):
			for f in range(len(KickBox)):
				if pygame.sprite.collide_rect(HeadBox[d],KickBox[f]):
					Player[d].KnockBackK(KickBox[f].get_X(), Player[d].get_X())
					Player[d].Health(16,d)
					#print ("Head Shot")






#---Main Loop---#
while RunGame == True:

#-general application things-#
	windowSurfaceObj.blit(BG,(0,0))
	FPSclock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			RunGame = False
			
#-character control-#
	#go through each character and update there states based on player input
	for d in range(len(Player)):
		Player[d].Flip()
		Player[d].Gravity()
		#print(Player[d].get_action())
		if Player[d].get_action() == "Knocked":
			Player[d].Knocked()
		else:
			Player[d].movement()
			if event.type == pygame.JOYBUTTONDOWN:
				Player[d].attack()

#-Collision-#
	#report to the collision function and figure if any collisions between players have occured
	collision()
	

#-Draw-#
	#draw characters with what ever action
	for d in range(len(Player)):
		Player[d].draw()

#-miscolanious-#
	#update the screen, slow down the game etc.
	pygame.display.update()
	#time.sleep(0.05)
