import Config as Config
import pygame as p
import sys
sys.path.append('C:/Users/Tom Huang/Desktop/CPSC/Chess/backend/src/util')
sys.path.append('C:/Users/Tom Huang/Desktop/CPSC/Chess/backend/src/chess/ai')
from Utilities import PieceMove, Color
from Board import ChessBoard
import MoveFinder
from multiprocessing import Process, Queue
'''
Main driver
'''
# class Game:
#     def __init__(self):
#         self.config = Config.BoardConfig()
#         self.config.loadImages()
#         self.screen = p.display.set_mode((self.config.BOARD_WIDTH, self.config.BOARD_HEIGHT))
#         self.clock = p.time.Clock()
#         self.gs = ChessBoard(self.config)
#         self.validMoves = self.getMoves()
#         self.moveMade = False
#         self.running = True
#         self.sqSelected = () 
#         self.playerClicks = []
#         self.playerOne = True
#         self.playerTwo = False        
#         self.moveLogFont = p.font.SysFont('timesnewroman', 14, False, False)

#     def play(self):
#         while self.running:
#             self.handleEvents()
#             self.updateGameState()
#             self.drawBoard()
#             self.clock.tick(self.config.MAX_FPS)
#             p.display.flip()

#     def handleEvents(self):
#         isHumanTurn = (self.gs.whiteToMove and self.playerOne) or (not self.gs.whiteToMove and self.playerTwo)
        
#         for e in p.event.get():
#             if e.type == p.QUIT:
#                 self.running = False
#             elif e.type == p.MOUSEBUTTONDOWN and not self.isGameOver() and isHumanTurn:
#                 self.handleMouseClick(e)
#             elif e.type == p.KEYDOWN:
#                 self.handleKeyPress(e)

#     def handleMouseClick(self, event):
#         location = p.mouse.get_pos()
#         col = location[0] // self.config.SQUARE_SIZE
#         row = location[1] // self.config.SQUARE_SIZE
#         # if same square is selected
#         if (row, col) == self.sqSelected:
#             self.sqSelected = ()
#             self.playerClicks = []
#         else: 
#             # if first square is not a piece
#             if len(self.playerClicks) == 0 and self.gs.board[row][col] == "--":
#                 return
            
#             self.sqSelected = (row, col)
#             self.playerClicks.append(self.sqSelected)
            
#         # two valid squares have been clicked
#         if len(self.playerClicks) == 2:

#             sqrOne, sqrTwo = self.playerClicks[0], self.playerClicks[1]
#             pieceOne, pieceTwo = self.gs.board[sqrOne[0]][sqrOne[1]], self.gs.board[sqrTwo[0]][sqrTwo[1]] 

#             # if both clicks are of the same color piece
#             if pieceOne != "--" and pieceTwo != "--" and pieceOne.color == pieceTwo.color:
#                 self.playerClicks[0], self.playerClicks[1] = self.playerClicks[1], self.playerClicks[0]
#                 self.playerClicks.pop()
#                 return 
            
#             move = PieceMove(sqrOne, sqrTwo, self.gs.board)
#             for i in range(len(self.validMoves)):
#                 if move == self.validMoves[i]:
#                     self.gs.makeMove(self.validMoves[i])
#                     self.gs.animateMove(self.gs.moveLog[-1], self.screen, self.clock, self.validMoves, self.sqSelected, self.moveLogFont)
#                     self.moveMade = True
#                     self.playerClicks = []
#                     self.sqSelected = ()
#                     break
                    
#             if not self.moveMade:
#                 self.playerClicks = [self.sqSelected]

#     def handleKeyPress(self, event):
#         if event.key == p.K_z:
#             self.gs.undoMove()
#             self.moveMade = True
#             self.setGameState(False)
#         elif event.key == p.K_r:
#             self.resetGame()

#     def updateGameState(self):
#         isHumanTurn = (self.gs.whiteToMove and self.playerOne) or (not self.gs.whiteToMove and self.playerTwo)
#         #AI
    
#         if not self.isGameOver() and not isHumanTurn:
#             AIMove = MoveFinder.findBestMove(self.gs, self.validMoves, returnQueue)
#             if not AIMove:
#                 MoveFinder.findRandomMove(self.validMoves)
#             self.gs.makeMove(AIMove)
#             self.moveMade = True
#             self.gs.animateMove(self.gs.moveLog[-1], self.screen, self.clock, self.validMoves, self.sqSelected)
            
#         if self.moveMade:
#             # print(self.gs.whiteToMove, self.sqSelected)
#             self.validMoves = self.getMoves()
#             if len(self.validMoves) == 0: 
#                 self.setGameState(True) 
#                 if self.gs.inCheck:
#                     endGameText = 'Black wins by check mate' if self.gs.whiteToMove else 'White wins by check mate'
#                 else:
#                     endGameText = 'Stale mate'
#                 self.gs.drawText(self.screen, endGameText)

#             self.moveMade = False
            


#     def drawBoard(self):
#         if not self.isGameOver():
#             self.gs.draw(self.screen, self.gs, self.validMoves, self.sqSelected, self.moveLogFont)

#     def isGameOver(self):
#         return not self.running

#     def setGameState(self, gameState):
#         self.running = not gameState

#     def getMoves(self):
#         return self.gs.getValidMoves()

#     def resetGame(self):
#         self.setGameState(False)
#         self.gs = ChessBoard(self.config)
#         self.validMoves = self.getMoves()
#         self.sqSelected = ()
#         self.playerClicks = []
#         self.moveMade = False

# if __name__ == "__main__":
#     game = Game()
#     game.play()
def main():
    
    config = Config.BoardConfig()
    config.loadImages()

    screen = p.display.set_mode((config.BOARD_WIDTH + config.MOVE_LOG_PANEL_WIDTH, config.BOARD_HEIGHT))
    clock = p.time.Clock()
    gs = ChessBoard(config)
    validMoves = gs.getValidMoves()
    moveMade = False # when valid move is made so we don't regenerate validMoves on every move attempt
    running = True
    gameOver = False
    sqSelected = () 
    playerClicks = [] # keep tracks of player clicks ([(6,4), (2,1)]) ([#first square, #second square])
    playerOne = True # if a human is playing white, then this will be True, if AI is playing this will be False
    playerTwo = False
    moveLogFont = p.font.SysFont('timesnewroman', 14, False, False)
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # mouse (x,y) 
                    col = location[0]//config.SQUARE_SIZE
                    row = location[1]//config.SQUARE_SIZE
                    
                    
                    # if same square is selected or click outside of game
                    if (row, col) == sqSelected or col > 7:
                        sqSelected = ()
                        playerClicks = []
                    else: 
                        # if first square is not a piece
                        if len(playerClicks) == 0 and gs.board[row][col] == "--":
                            continue
                        
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                        
                    # two valid squares have been clicked
                    if len(playerClicks) == 2 and isHumanTurn:

                        sqrOne, sqrTwo = playerClicks[0], playerClicks[1]
                        pieceOne, pieceTwo = gs.board[sqrOne[0]][sqrOne[1]], gs.board[sqrTwo[0]][sqrTwo[1]] 

                        # if both clicks are of the same color piece
                        if pieceOne != "--" and pieceTwo != "--" and pieceOne.color == pieceTwo.color:
                            playerClicks[0], playerClicks[1] = playerClicks[1], playerClicks[0]
                            playerClicks.pop()
                            continue 
                        
                        move = PieceMove(sqrOne, sqrTwo, gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                gs.animateMove(gs.moveLog[-1], screen, clock, validMoves, sqSelected, moveLogFont)
                                moveMade = True
                                playerClicks = []
                                sqSelected = ()
                                
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r: # reset board when press r
                    gameOver = False
                    gs = ChessBoard(config)
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        
        #AI
     
        if not gameOver and not isHumanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue() # used to pass data between threads
                moveFinderProcess = Process(target=MoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()
            
            if not moveFinderProcess.is_alive():
                print("done thinking")
                AIMove = returnQueue.get()
                if not AIMove:
                    MoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                gs.animateMove(gs.moveLog[-1], screen, clock, validMoves, sqSelected, moveLogFont)
                AIThinking = False
                
        if moveMade:
            validMoves = gs.getValidMoves()
            if len(validMoves) == 0: 
                gameOver = True
                if gs.inCheck:
                    endGameText = 'Black wins by check mate' if gs.whiteToMove else 'White wins by check mate'
                else:
                    endGameText = 'Stale mate'
                gs.drawEndGameText(screen, endGameText)
            
            moveUndone = False
            moveMade = False
        
        if not gameOver:
            gs.draw(screen, gs, validMoves, sqSelected, moveLogFont)
        

        clock.tick(config.MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()