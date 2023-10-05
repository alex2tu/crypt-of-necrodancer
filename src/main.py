import random
from operator import truediv

from pillowgraphics import *


class Player():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        pass

    def move(self,dx,dy):
        self.x += dx
        self.y += dy
    
class Enemy():
    def __init__(self,x,y,status,hasMoved):
        self.x = x
        self.y = y
        self.status = status #true = alive
        self.hasMoved = hasMoved

    def move(self,dx,dy):
        self.x += dx
        self.y += dy

def moveEnemy(app,movements,entity):
    if abs(entity.x-app.player.x) + abs(entity.y-app.player.y) <=1: #if the enemy is right next to player when making its move
        entity.move(app.player.x-entity.x,app.player.y-entity.y) #move enemy to player (they're not that dumb!)
        app.enemyMoved = True
        return 
    movementDir = movements[random.randint(0,3)]
    dx,dy = movementDir
    entity.move(dx,dy)
    for person in app.enemyList:
        if entity.x == person.x and entity.y == person.y and entity != person:
            entity.move(-dx,-dy)
            return moveEnemy(app,movements,entity)
    checkLegalSquare(app,entity.x,entity.y,dx,dy,entity)
    app.enemyMoved = True 

def appendEnemies(app,enemyList):
    enemyX = 0
    enemyY = 0
    while(True):
        enemyX = random.randint(0,app.dungeonLength-1)
        enemyY = random.randint(0,app.dungeonLength-1)
        if not app.dungeon[enemyX][enemyY]: #check if valid square for enemy to spawn on
            continue
        if abs(app.player.x-enemyX) < 2 or abs(app.player.y-enemyY) < 2: #not too close to player
            continue
        if len(enemyList) != 0:
            for entity in enemyList:
                if enemyX == entity.x and enemyY == entity.y:
                    continue
        break
    enemyList.append(Enemy(enemyX,enemyY,True,False))
    pass

def appStarted(app): 
    '''GRID APP STARTED'''
    app.dungeonLength = 15
    app.startingX = random.randint(app.dungeonLength/3,2*app.dungeonLength/3)
    app.startingY = random.randint(app.dungeonLength/3,2*app.dungeonLength/3)
    app.dungeon = terrainGenerator(app.startingX,app.startingY,app.dungeonLength)
    app.player = Player(app.startingX,app.startingY)
    app.enemyList = []
    for i in range(4):
        appendEnemies(app,app.enemyList)
    app.cellSize = app.height/len(app.dungeon)
    app.cellIndent = app.cellSize/20
    app.movements = [(1,0),(0,1),(-1,0),(0,-1)]
    app.totalPlayerHealth = 5 #max health/health started with
    app.playerHealth = 5 #current health
    app.moveCount = 0 #number of times player has moved
    app.playerDamaged = False #checks if player has already been damaged in a cycle
    app.gameOver = False
    app.enemyMoved = True #checks if enemy has moved yet in curr cycle
    app.enemyWins = False
    app.instructions = False
    app.ben = app.loadImage('ben.png') #pixel art of ben made by me
    #pixel art style inspired by Pokemon Gold Trainer https://www.spriters-resource.com/game_boy_gbc/pokemongoldsilver/sheet/9077/
    app.benScaled = app.scaleImage(app.ben,33/16)

    '''SLIDING BLOCK APP STARTED'''
    app.waitingForKeyPress = True
    app.pressedCorrect = False
    app.pressedIncorrect = False
    app.slidingBlockHeight = app.height/15
    app.slidingBlockWidth = app.width/25
    app.rectangleBounds = app.width/2-app.slidingBlockWidth*6,app.slidingBlockHeight/2,app.width/2+app.slidingBlockWidth*6,3*app.slidingBlockHeight/2
    app.deltaX = 11
    app.slidingBlockX = app.rectangleBounds[0]
    app.slidingBlockY = app.rectangleBounds[1]
    app.timerDelay = 9
    app.timePassed = 0
    app.slidingBlockIncrements = 0 #num of cycles
    app.blockIncremented = False #var to keep track if slidingblockincrements has already been incremented in a cycle
    pass

def slidingBlockIncrement(app):
    if app.slidingBlockX > app.width/2-3*app.slidingBlockWidth/2 and app.slidingBlockX < app.width/2+app.slidingBlockWidth/2 and not app.blockIncremented:
        app.slidingBlockIncrements +=1
        app.blockIncremented = True
        app.playerDamaged = False
        app.enemyMoved = False #resets enemyMoved
        return True
    elif app.slidingBlockX < app.width/2-3*app.slidingBlockWidth/2 or app.slidingBlockX > app.width/2+app.slidingBlockWidth/2:
        app.blockIncremented = False
        return False
    return False


def timerFired(app):
    if app.gameOver or app.waitingForKeyPress or app.instructions:
        return
    if app.playerHealth == 0:
        app.gameOver = True
    moveBlock(app)
    slidingBlockIncrement(app)
    if not app.blockIncremented:
        if not app.enemyMoved: #if no enemies have moved yet
            for entity in app.enemyList: #move all enemies
                moveEnemy(app,app.movements,entity)
                checkEnemyOnPlayer(app,entity)
        if app.slidingBlockIncrements > app.moveCount+(app.totalPlayerHealth-app.playerHealth):
            if not app.playerDamaged:
                app.playerHealth -= 1
                app.playerDamaged = True #player has alr been damaged this cycle
    if app.pressedCorrect or app.pressedIncorrect:
        app.timePassed += app.timerDelay
        if app.timePassed >= 100:
            app.pressedCorrect = False
            app.pressedIncorrect = False
            app.timePassed = 0
    pass

def checkCorrectPress(app,x):
    if x > app.width/2-3*app.slidingBlockWidth/2 and x < app.width/2+app.slidingBlockWidth/2:
        app.pressedCorrect = True
        return True
    elif not app.playerDamaged: #checks if player has been damaged alr in cycle
        app.playerHealth -= 1
        app.playerDamaged = True
        return False
    else: 
        return False

'''SLIDING BLOCK'''
def moveBlock(app):
    app.slidingBlockX += app.deltaX
    if app.slidingBlockX > app.rectangleBounds[2]-app.slidingBlockWidth-app.deltaX or app.slidingBlockX < app.rectangleBounds[0]-app.deltaX:
        app.deltaX *= -1

def keyPressed(app,event):
    if event.key == 'r':
        appStarted(app)
    if event.key == 'i':
        app.instructions = not app.instructions
        return
    if app.gameOver:
        return
    if app.waitingForKeyPress:
        app.waitingForKeyPress = False
    if event.key == "Up":
        if not app.pressedCorrect and checkCorrectPress(app,app.slidingBlockX):
            app.player.move(0,-1)

            if checkLegalSquare(app,app.player.x,app.player.y,0,-1,app.player):
                app.moveCount +=1
                for entity in app.enemyList:
                    checkPlayerOnEnemy(app,entity)

    if event.key == "Down":
        if not app.pressedCorrect and checkCorrectPress(app,app.slidingBlockX):
            app.player.move(0,1)
            if checkLegalSquare(app,app.player.x,app.player.y,0,1,app.player):
                app.moveCount +=1
                for entity in app.enemyList:
                    checkPlayerOnEnemy(app,entity)

    if event.key == "Left":
        if not app.pressedCorrect and checkCorrectPress(app,app.slidingBlockX):
            app.player.move(-1,0)
            if checkLegalSquare(app,app.player.x,app.player.y,-1,0,app.player):
                app.moveCount +=1
                for entity in app.enemyList:
                    checkPlayerOnEnemy(app,entity)

    if event.key == "Right":
        if not app.pressedCorrect and checkCorrectPress(app,app.slidingBlockX): #cant move twice in one beat
            app.player.move(1,0)
            if checkLegalSquare(app,app.player.x,app.player.y,1,0,app.player):
                app.moveCount +=1
                for entity in app.enemyList:
                    checkPlayerOnEnemy(app,entity)

def checkPlayerOnEnemy(app,entity): #player moves onto enemy
    if app.player.x == entity.x:
        if app.player.y == entity.y:
            entity.status = False
            app.enemyList.remove(entity)
            if len(app.enemyList) == 0:
                app.gameOver = True

def checkEnemyOnPlayer(app,entity): #enemy moves onto player, player dies
    if app.player.x == entity.x:
        if app.player.y == entity.y:
            app.enemyWins = True
            app.gameOver = True

def checkLegalSquare(app,x,y,dx,dy,entity):
    if x < 0 or x > len(app.dungeon[0])-1:
        entity.move(-dx,-dy)
        x -= dx
        return False
    if y < 0 or y > len(app.dungeon)-1:
        entity.move(-dx,-dy)
        y -= dy
        return False
    if not app.dungeon[x][y]:
        entity.move(-dx,-dy)
        return False
    return True

def redrawAll(app,canvas):
    if app.waitingForKeyPress:
        drawBackground(app,canvas)
        drawWaitingForPress(app,canvas)
        return
    if app.gameOver:
        if app.enemyWins:
            drawGameOverLossEnemy(app,canvas)
        elif app.playerHealth == 0:
            drawGameOverLossHealth(app,canvas)
        else:
            drawGameOverWin(app,canvas)
        return
    elif app.instructions:
        drawBackground(app,canvas)
        drawInstructions(app,canvas)
        return
    drawBackground(app,canvas)
    drawGrid(app,canvas)
    drawPlayer(app,canvas)
    drawEnemy(app,canvas)
    drawHealth(app,canvas)
    drawInfo(app,canvas)

    drawRectangleOutline(app,canvas)
    drawTargetRectangle(app,canvas)
    drawSlidingBlock(app,canvas)
    # drawPressed(app,canvas)

def drawInfo(app,canvas):
    canvas.create_text(5,5,text = "Press 'i' for instructions", fill = 'White', anchor = 'nw')

def drawWaitingForPress(app,canvas):
    canvas.create_text(app.width/2,app.height/2,text = 'Press any key to begin.',font = 'Arial 20 bold', fill = 'White')
    # Use the arrow keys on beat to move, you are the red dot \nMove onto the enemy before they move onto you!
    pass

def drawBackground(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = 'grey10')
    pass

def drawInstructions(app,canvas):
    canvas.create_text(app.width/2,5,anchor = 'n', text = 'Instructions:',font = 'Arial 35 bold', fill = 'white')
    instructionText = '''You play as the red dot!\n 
    You use the arrow keys to move, and you must time your key presses with the beat/sliding block\n
    The objective is to faint (kill) all the Ben Nguyens on the board (they hate kpop!)\n
    Also look one of Ben's eyes are higher than the other lol\n
    Anyways you faint the Ben by moving onto Ben's position \n
    However, Ben can faint you by moving over you instead\n
    Whoever makes the move to intersect the other first is the winner\n
    the enemy moves at the end of every beat, so you have an advantage by moving before them\n
    However, if you move directly next to a Ben before they make their move, then they will move onto you and faint you\n
    (ben isn't that stupid!)\n
    So be cautious as to how you make your next move (and don't forget to time it with the beat!)
    '''
    canvas.create_text(app.width/2,app.height/2,text = instructionText,fill = 'white')

'''GAME OVER DRAWS'''

def drawGameOverWin(app,canvas):
    canvas.create_text(app.width/2,app.height/2, text = 'You killed all the enemies! You win! Press r to restart')
    accuracyPercentage = int(100*(app.moveCount/app.slidingBlockIncrements))
    canvas.create_text(app.width/2,2*app.height/3, text = f'accuracy: {accuracyPercentage}% of on beat clicks')

def drawGameOverLossEnemy(app,canvas):
    canvas.create_text(app.width/2,app.height/2, text = 'The enemy killed you! Game Over! Press r to restart')
    accuracyPercentage = int(100*(app.moveCount/app.slidingBlockIncrements))
    canvas.create_text(app.width/2,2*app.height/3, text = f'accuracy: {accuracyPercentage}% of on beat clicks')

def drawGameOverLossHealth(app,canvas):
    canvas.create_text(app.width/2,app.height/2, text = 'You lost all your health! Game Over! Press r to restart')
    accuracyPercentage = int(100*(app.moveCount/app.slidingBlockIncrements))
    canvas.create_text(app.width/2,2*app.height/3, text = f'accuracy: {accuracyPercentage}% of on beat clicks')

'''GRID DRAW'''
def drawGrid(app,canvas):
    for i in range(len(app.dungeon)):
        for j in range(len(app.dungeon[0])):
            if app.dungeon[i][j]:
                canvas.create_rectangle(i*app.cellSize,j*app.cellSize,
                                    (i+1)*app.cellSize,(j+1)*app.cellSize,fill = 'grey49',width = 0) #outer rect
                canvas.create_rectangle(i*app.cellSize+app.cellIndent,j*app.cellSize+app.cellIndent,
                                    (i+1)*app.cellSize-app.cellIndent,(j+1)*app.cellSize-app.cellIndent,fill = 'grey60',width = 0) #inner rect
                #lighter borders
                canvas.create_rectangle(i*app.cellSize+app.cellIndent,(j+1)*app.cellSize-app.cellIndent*2,
                                    (i+1)*app.cellSize-app.cellIndent,(j+1)*app.cellSize-app.cellIndent,fill = 'grey70',width = 0)
                canvas.create_rectangle((i+1)*app.cellSize-app.cellIndent*2,j*app.cellSize+app.cellIndent,
                                    (i+1)*app.cellSize-app.cellIndent,(j+1)*app.cellSize-app.cellIndent,fill = 'grey70',width = 0) 
                
                pass
            pass
    pass

'''PLAYER AND ENEMY DRAW'''
def drawPlayer(app,canvas):
    x,y = app.player.x,app.player.y
    canvas.create_oval(x*app.cellSize+app.cellIndent,y*app.cellSize+app.cellIndent,
                    (x+1)*app.cellSize-app.cellIndent,(y+1)*app.cellSize-app.cellIndent,fill = 'Red', width = 0)

def drawEnemy(app,canvas):
    for entity in app.enemyList:
        if entity.status:
            x,y = entity.x,entity.y
            cellCenter = x*app.cellSize+app.cellSize/2,y*app.cellSize+app.cellSize/2
            #center var for image location
            canvas.create_image(cellCenter,image=ImageTk.PhotoImage(app.benScaled))


def drawHealth(app,canvas):
    canvas.create_text(5,app.height-25,anchor = 'w',text = "Health:", fill = 'White')
    for i in range(app.playerHealth):
        canvas.create_rectangle(i*10+5,app.height-15,(i+1)*10+5,app.height-5, fill = 'Red')

'''SLIDING BLOCK DRAWINGS'''
def drawPressed(app,canvas):
    if app.pressedCorrect:
        canvas.create_text(app.width/2,app.height/2,text = 'Pressed Correct!')
    elif app.pressedIncorrect:
        canvas.create_text(app.width/2,app.height/2,text = 'Pressed Incorrect')

def drawRectangleOutline(app,canvas):
    canvas.create_rectangle(app.rectangleBounds,width = 10)
    canvas.create_rectangle(app.rectangleBounds,fill = 'White')

def drawTargetRectangle(app,canvas):
    canvas.create_rectangle(app.width/2-app.slidingBlockWidth/2,app.rectangleBounds[1],app.width/2+app.slidingBlockWidth/2,app.rectangleBounds[3], fill = 'Blue')
    pass

def drawSlidingBlock(app,canvas):
    canvas.create_rectangle(app.slidingBlockX,app.slidingBlockY,app.slidingBlockX+app.slidingBlockWidth,app.slidingBlockY+app.slidingBlockHeight,fill = 'Red')

'''DUNGEON GENERATOR'''
def terrainGenerator(startingX,startingY,length):
    terrain = [[False] * length for i in range(length)]
    floorTileMax = 150
    movements = [(1,0),(0,1),(-1,0),(0,-1)]
    visited = []
    drunkardsWalk(terrain,startingX,startingY,floorTileMax,movements,visited)
    return terrain

#modified drunkard's walk idea from https://www.reddit.com/r/roguelikedev/comments/hhzszb/using_a_modified_drunkards_walk_to_generate_cave/
def drunkardsWalk(terrain,x,y,floorTileMax,movements,visited,tileCount = 0):
    if tileCount == floorTileMax:
        return
    if not terrain[x][y]:
        terrain[x][y] = True
        tileCount += 1
        visited.append((x,y))
    while not checkAdjacency(terrain,x,y):
        x,y = visited.pop()
    while True:
        movementDir = movements[random.randint(0,3)]
        dx,dy = movementDir
        newX = x + dx
        newY = y + dy
        if newX < 0 or newX > len(terrain)-1 or newY < 0 or newY > len(terrain[0])-1:
            continue
        elif not terrain[newX][newY]:
            break
    drunkardsWalk(terrain,newX,newY,floorTileMax,movements,visited,tileCount)
    

def checkAdjacency(board,x,y): #checks if has an available adjacency
    movements = [(1,0),(0,1),(-1,0),(0,-1)]
    for i in movements:
        dx,dy = i
        newX = x + dx
        newY = y + dy
        if newX < 0 or newX > len(board)-1 or newY < 0 or newY > len(board[0])-1:
            continue
        if not board[newX][newY]:
            return True
    return False

def print2dList(a): #copied from 15-112 notes july 18th
    if (a == []): print([]); return
    rows, cols = len(a), len(a[0])
    colWidths = [0] * cols
    for col in range(cols):
        colWidths[col] = max([len(str(a[row][col])) for row in range(rows)])
    print('[')
    for row in range(rows):
        print(' [ ', end='')
        for col in range(cols):
            if (col > 0): print(', ', end='')
            print(str(a[row][col]).ljust(colWidths[col]), end='')
        print(' ]')
    print(']')

def testTerrainGenerator():
    print2dList(terrainGenerator())

def main():
    runApp(width=750, height=750)
    # testTerrainGenerator()

if __name__ == '__main__':
    main()