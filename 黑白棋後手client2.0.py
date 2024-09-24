import pygame, sys, random, time, socket, threading
from pygame.locals import *

HOST = '127.0.0.1'
PORT = 7000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

#client.setblocking(False)
 
BACKGROUNDCOLOR = (255, 255, 255)
BLACK = (255, 255, 255)
BLUE = (0, 0, 255)
CELLWIDTH = 50
CELLHEIGHT = 50
PIECEWIDTH = 47
PIECEHEIGHT = 47
BOARDX = 35
BOARDY = 35
FPS = 40
gameOver = False
 
# 退出
def terminate():
    pygame.quit()
    sys.exit()

def update():
    while True:
        time.sleep(1)
        pygame.display.update()

def myturn(gameOver,turn):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if gameOver == False and turn == 'player' and event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                col = int((x-BOARDX)/CELLWIDTH)
                row = int((y-BOARDY)/CELLHEIGHT)
                if makeMove(mainBoard, playerTile, col, row) == True:
                    if getValidMoves(mainBoard, computerTile) != []:
                        outdata = str(col)+str(row)
                        client.send(outdata.encode())
                        print('send'+str(count)+': '+outdata)
                        count += 1
                        turn = 'computer'
         
        windowSurface.fill(BACKGROUNDCOLOR)
        windowSurface.blit(boardImage, boardRect, boardRect)
        for x in range(8):
            for y in range(8):
                rectDst = pygame.Rect(BOARDX+x*CELLWIDTH+2, BOARDY+y*CELLHEIGHT+2, PIECEWIDTH, PIECEHEIGHT)
                if mainBoard[x][y] == 'black':
                    windowSurface.blit(blackImage, rectDst, blackRect)
                elif mainBoard[x][y] == 'white':
                    windowSurface.blit(whiteImage, rectDst, whiteRect)
         
        if isGameOver(mainBoard):
            print('gameover in 1')
            gameOver = True
            scorePlayer = getScoreOfBoard(mainBoard)[playerTile]
            scoreComputer = getScoreOfBoard(mainBoard)[computerTile]
            outputStr = gameoverStr + str(scorePlayer) + ":" + str(scoreComputer)
            text = basicFont.render(outputStr, True, BLACK, BLUE)
            textRect = text.get_rect()
            textRect.centerx = windowSurface.get_rect().centerx
            textRect.centery = windowSurface.get_rect().centery
            windowSurface.blit(text, textRect)
            time.sleep(10)

def otherturn(gameOver,turn):
    while True:
        if (gameOver == False and turn == 'computer'):
            indata = client.recv(1024)
            indata = indata.decode()
            print('recv: '+indata)
            x, y = int(indata[0]),int(indata[1])
            makeMove(mainBoard, computerTile, x, y)
            savex, savey = x, y
         
            # 玩家没有可行的走法了
            if getValidMoves(mainBoard, playerTile) != []:
                turn = 'player'
         
        windowSurface.fill(BACKGROUNDCOLOR)
        windowSurface.blit(boardImage, boardRect, boardRect)
            
        for x in range(8):
            for y in range(8):
                rectDst = pygame.Rect(BOARDX+x*CELLWIDTH+2, BOARDY+y*CELLHEIGHT+2, PIECEWIDTH, PIECEHEIGHT)
                if mainBoard[x][y] == 'black':
                    windowSurface.blit(blackImage, rectDst, blackRect)
                elif mainBoard[x][y] == 'white':
                    windowSurface.blit(whiteImage, rectDst, whiteRect)
         
        if isGameOver(mainBoard):
            print('gameover in 2')
            gameOver = True
            scorePlayer = getScoreOfBoard(mainBoard)[playerTile]
            scoreComputer = getScoreOfBoard(mainBoard)[computerTile]
            outputStr = gameoverStr + str(scorePlayer) + ":" + str(scoreComputer)
            text = basicFont.render(outputStr, True, BLACK, BLUE)
            textRect = text.get_rect()
            textRect.centerx = windowSurface.get_rect().centerx
            textRect.centery = windowSurface.get_rect().centery
            windowSurface.blit(text, textRect)
            time.sleep(10)
 
# 重置棋盘
def resetBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = 'none'
 
    # Starting pieces:
    board[3][3] = 'black'
    board[3][4] = 'white'
    board[4][3] = 'white'
    board[4][4] = 'black'
 
 
# 开局时建立新棋盘
def getNewBoard():
    board = []
    for i in range(8):
        board.append(['none'] * 8)
 
    return board
 
 
# 是否是合法走法
def isValidMove(board, tile, xstart, ystart):
    # 如果该位置已经有棋子或者出界了，返回False
    if not isOnBoard(xstart, ystart) or board[xstart][ystart] != 'none':
        return False
 
    # 临时将tile 放到指定的位置
    board[xstart][ystart] = tile
 
    if tile == 'black':
        otherTile = 'white'
    else:
        otherTile = 'black'
 
    # 要被翻转的棋子
    tilesToFlip = []
    for xdirection, ydirection in [ [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1] ]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            # 一直走到出界或不是对方棋子的位置
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            # 出界了，则没有棋子要翻转OXXXXX
            if not isOnBoard(x, y):
                continue
            # 是自己的棋子OXXXXXXO
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    # 回到了起点则结束
                    if x == xstart and y == ystart:
                        break
                    # 需要翻转的棋子
                    tilesToFlip.append([x, y])
 
    # 将前面临时放上的棋子去掉，即还原棋盘
    board[xstart][ystart] = 'none' # restore the empty space
 
    # 没有要被翻转的棋子，则走法非法。翻转棋的规则。
    if len(tilesToFlip) == 0:   # If no tiles were flipped, this is not a valid move.
        return False
    return tilesToFlip
 
 
# 是否出界
def isOnBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <=7
 
 
# 获取可落子的位置
def getValidMoves(board, tile):
    validMoves = []
 
    for x in range(8):
        for y in range(8):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves
 
 
# 获取棋盘上黑白双方的棋子数
def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'black':
                xscore += 1
            if board[x][y] == 'white':
                oscore += 1
    return {'black':xscore, 'white':oscore}
 
 
# 将一个tile棋子放到(xstart, ystart)
def makeMove(board, tile, xstart, ystart):
    tilesToFlip = isValidMove(board, tile, xstart, ystart)
 
    if tilesToFlip == False:
        return False
 
    board[xstart][ystart] = tile
    for x, y in tilesToFlip:
        board[x][y] = tile
    return True
 
# 复制棋盘
def getBoardCopy(board):
    dupeBoard = getNewBoard()
 
    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]
 
    return dupeBoard
 
# 是否游戏结束
def isGameOver(board):
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'none':
                return False
    return True
 
# 初始化
pygame.init()
mainClock = pygame.time.Clock()
 
# 加载图片
boardImage = pygame.image.load('board.png')
boardRect = boardImage.get_rect()
blackImage = pygame.image.load('black.png')
blackRect = blackImage.get_rect()
whiteImage = pygame.image.load('white.png')
whiteRect = whiteImage.get_rect()
 
basicFont = pygame.font.SysFont(None, 48)
gameoverStr = 'Game Over Score '
 
mainBoard = getNewBoard()
resetBoard(mainBoard)
 
turn = 'computer'
if turn == 'computer':
    playerTile = 'white'
    computerTile = 'black'
else:
    playerTile = 'black'
    computerTile = 'white'
 
print(turn) 
 
# 设置窗口
windowSurface = pygame.display.set_mode((boardRect.width, boardRect.height))
pygame.display.set_caption('黑白棋')

a = threading.Thread(target=update)
a.start() 
windowSurface.fill(BACKGROUNDCOLOR)
windowSurface.blit(boardImage, boardRect, boardRect)

for x in range(8):
    for y in range(8):
        rectDst = pygame.Rect(BOARDX+x*CELLWIDTH+2, BOARDY+y*CELLHEIGHT+2, PIECEWIDTH, PIECEHEIGHT)
        if mainBoard[x][y] == 'black':
            windowSurface.blit(blackImage, rectDst, blackRect)
        elif mainBoard[x][y] == 'white':
            windowSurface.blit(whiteImage, rectDst, whiteRect)

pygame.display.update()

count = 0

b = threading.Thread(target=myturn,args=(gameOver,turn,))
c = threading.Thread(target=otherturn,args=(gameOver,turn,))
b.start()
c.start()
 
# 游戏主循环
mainClock.tick(FPS)
