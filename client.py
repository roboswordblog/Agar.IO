import sys, random
import pygame, socket, json

# from numpy.ma.core import append


pygame.init()

window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Agar.io")

foodlist, enemylist = [], {}
names = ["Bob", "James", "Dom", "Goat", "Cook"]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.0.155", 5555))

server_players = {}
buffer = ""


def receive():
    global server_players, buffer
    while True:
        try:
            data = client.recv(4096).decode()
            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                server_players = json.loads(msg)




        except:
            break


import threading

threading.Thread(target=receive, daemon=True).start()


def text(x, y, text, size, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.actualX = random.randint(0, 800)
        self.actualY = random.randint(0, 600)
        self.size = 50
        self.actualSize = 50
        self.name = random.choice(names)
        self.rect = None
        self.score = 0
        self.speed = 1
        self.player = random.randint(0,
                                     100000000000891233128123089128903890238901238902890123890123089090812389012389012389038901238901238012380123890)
        self.dx = 0
        self.dy = 0
        self.color = (255, random.randint(0, 255), random.randint(0, 255))

    def draw(self):
        self.rect = pygame.draw.circle(window, self.color, (self.x, self.y), self.size)
        text(int(self.x - self.size / 3), self.y, f"{self.name}:{self.actualSize}", int(self.size / 3), (255, 255, 255))

    def update(self):
        self.dx = 0
        self.dy = 0
        collisionId = None
        for _,i in enemylist.items():
            if i.rect and self.rect and i.rect.colliderect(self.rect) and i.size < self.actualSize:
                self.size += 50
                collisionId = str(i.id)
        try:
            data = json.dumps(
                {"actualX": self.actualX, "actualY": self.actualY, "playerid": self.player, "size": self.actualSize,
                 "color": self.color, "id": collisionId})
            client.send((data + "\n").encode())
        except:
            print("Disconnected from server")
            sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

            if self.actualX < 0:
                pass
            else:
                self.dx = -int(self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

            if self.actualX > 1000:
                pass
            else:
                self.dx = int(self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.actualY < 0:
                pass
            else:
                self.dy = -int(self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.actualY  > 1000:
                pass
            else:
                self.dy = int(self.speed)

        self.actualX += self.dx
        self.actualY += self.dy
        self.size = 50 + (self.actualSize / 10)


class Food:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 600)
        foodlist.append(self)
        self.rect = None
        self.size = random.randint(10, 15)
        self.color = (random.randint(0, 255), random.randint(0, 255), 255)

    def draw(self):
        self.rect = pygame.draw.circle(window, self.color, (self.x, self.y), self.size)

    def update(self, player):
        self.x -= player.dx
        self.y -= player.dy
        if self.rect.colliderect(player.rect):
            foodlist.remove(self)
            player.actualSize += 1

            for _, i in enemylist.items():
                if i.size < 10:
                    i.size = 10
                else:
                    i.size -= 1
            for i in foodlist:

                if i.size < 10:
                    i.size = 10
                else:
                    i.size -= 1
    # self.size = max(5, int(20 - player.actualSize * 0.1))





class Enemies:
    def __init__(self, x, y, id, size, color):
        self.x = x
        self.y = y
        #   enemylist.append(self)
        self.id = id
        self.size = size
        self.color = color
        self.rect = pygame.Rect(0, 0, 0, 0)
        # self.rect = None
    def update(self, player):
        #self.x -= player.dx
        #self.y -= player.dy
        pass

    def draw(self, player):
        screen_x = int(self.x - player.actualX + 400)
        screen_y = int(self.y - player.actualY + 300)

        self.rect = pygame.draw.circle(window, self.color, (screen_x, screen_y), int(self.size))


x, y = 400, 300
player = Player(x, y)
titler, titleg, titleb = 30, 110, 125

for i in range(30):
    Food()
clock = pygame.time.Clock()
while True:
    if random.randint(0, 50) == 10:
        Food()
    window.fill((255, 255, 255))
    text(310, 50, "Agar.IO by Robosword", 30, (titler, titleb, titleg))
    text(10, 20, f"{player.actualX}, {player.actualY}", 20, (0, 0, 0))
    player.draw()

    for i in foodlist:
        i.draw()
        i.update(player)
    for key, value in enemylist.items():
        value.draw(player)
        value.update(player)
    player.update()
    enemylist.clear()
    for pid, p in server_players.items():

        if str(pid) == str(player.player):
            continue

        #if not all(k in p for k in ("x", "y", "size")):
         #   continue

        x = int(p["x"])
        y = int(p["y"])
        size = int(p["size"])
        color = tuple(p["color"])
        enemylist[pid] = Enemies(x, y, pid, size, color)
        if p.get("dead"):
            if str(pid) == str(player.player):
                print("YOU DIED")
                pygame.quit()
                sys.exit()
                break
                print(0/100)
                print(100/0)
            continue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    clock.tick(120)
    pygame.display.update()
