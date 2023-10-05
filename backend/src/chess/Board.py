import pygame as p
from Piece import Rook, Pawn, Bishop, Knight, King, Queen
from Utilities import Color, MovementUtil, CastleMove



class ChessBoard():

    def __init__(self, config):
        self.config = config
        # board is 8x8 2D list. each element represents a board state
        self.board = [
            [Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK), Queen(Color.BLACK), King(Color.BLACK), Bishop(Color.BLACK), Knight(Color.BLACK), Rook(Color.BLACK)],
            [Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK)],
            [self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE],
            [self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE],
            [self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE],
            [self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE, self.config.EMPTY_SQUARE],
            [Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE), Pawn(Color.WHITE)],
            [Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE), Queen(Color.WHITE), King(Color.WHITE), Bishop(Color.WHITE), Knight(Color.WHITE), Rook(Color.WHITE)]
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.kingsPosition = {Color.WHITE: (7, 4), Color.BLACK: (0, 4)}
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.inPin = False
        self.canEnPassant = () # square that en passant is possible
        self.canEnPassantLog = [self.canEnPassant]
        self.currentCastlingRights = CastleMove()
        self.castleRightsLog = [self.currentCastlingRights.clone()]
        self.checkMate = False
        self.staleMate = False
        self.moveLogFont = None

        p.init()



    '''
    Board representation
    '''
    def draw(self, screen, gs, validMoves, sqSelected, moveLogFont):
        self.drawSquares(screen)
        self.highlightSquares(screen, gs, validMoves, sqSelected)
        self.drawPieces(screen)
        self.drawMoveLog(screen, gs, moveLogFont)

    def drawSquares(self, screen):
        colors = [p.Color(118,150,86), p.Color(238,238,210)]
        for r in range(self.config.DIMENSION):
            for c in range(self.config.DIMENSION):
                color = colors[(r+c)%2]
                p.draw.rect(screen, color, p.Rect(c*self.config.SQUARE_SIZE, r*self.config.SQUARE_SIZE, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))

    def drawPieces(self, screen):
        for r in range(self.config.DIMENSION):
            for c in range(self.config.DIMENSION):
                piece = self.board[r][c]
                if MovementUtil.isEmpty(piece): continue
                pieceSymbol = piece.getSymbol()
                screen.blit(self.config.IMAGES[pieceSymbol], p.Rect(c*self.config.SQUARE_SIZE, r*self.config.SQUARE_SIZE, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))

    def drawEndGameText(self, screen, text):
        font = p.font.SysFont("timesnewroman", 32, True, False)
        textObject = font.render(text, 0, p.Color("Black"))
        textLocation = p.Rect(0, 0, self.config.BOARD_WIDTH//2, self.config.BOARD_HEIGHT//2).move(self.config.BOARD_WIDTH/2 - textObject.get_BOARD_WIDTH()/2, self.config.BOARD_HEIGHT/2 - textObject.get_BOARD_HEIGHT()/2)
        screen.blit(textObject, textLocation)
        p.display.flip()
    
    def drawMoveLog(self, screen, gs, font):
        moveLogRect = p.Rect(self.config.BOARD_WIDTH, 0, self.config.MOVE_LOG_PANEL_WIDTH, self.config.MOVE_LOG_PANEL_HEIGHT)
        p.draw.rect(screen, p.Color('black'), moveLogRect)
        moveLog = self.moveLog
        moveTexts = []
        
        for i in range(0, len(moveLog), 2):
            moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
            if i + 1 < len(moveLog):
                moveString += str(moveLog[i+1]) + " "
            moveTexts.append(moveString)
            
        movesPerRow = 3
        padding = 5
        textY = padding
        lineSpacing = 2
        
        for i in range(0, len(moveTexts), movesPerRow):
            text = ""
            for j in range(movesPerRow):
                if i + j < len(moveTexts):
                    text += moveTexts[i+j]
            textObject = font.render(text, True, p.Color("white"))
            textLocation = moveLogRect.move(padding, textY)
            screen.blit(textObject, textLocation)
            textY += textObject.get_height() + lineSpacing
      
    '''
    Animating Moves
    '''

    def animateMove(self, move, screen, clock, validMoves, sqSelected, moveLogFont):
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        framesPerSquare = 1 #frames to move 1 square 
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        colors = [p.Color(118,150,86), p.Color(238,238,210)]
        
        for frame in range(frameCount + 1):
            r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))  # the coords that the piece will move through per frame
            self.draw(screen, self, validMoves, sqSelected, moveLogFont)
            
            #erase the piece moved from its ending square
            color = colors[(move.endRow + move.endCol) % 2]
            endSquare = p.Rect(move.endCol*self.config.SQUARE_SIZE, move.endRow*self.config.SQUARE_SIZE, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE)
            p.draw.rect(screen, color, endSquare)
            
            # draw captured piece onto rectangle
            if move.pieceCaptured != self.config.EMPTY_SQUARE:
                if move.isEnPassant:
                    enPassantRow = move.endRow + 1 if move.pieceMoved.getColor() == Color.WHITE else move.endRow - 1
                    endSquare = p.Rect(move.endCol*self.config.SQUARE_SIZE, enPassantRow*self.config.SQUARE_SIZE, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE) 
                screen.blit(self.config.IMAGES[move.pieceCaptured.getSymbol()], endSquare)
            
            
            #draw moving piece
            screen.blit(self.config.IMAGES[move.pieceMoved.getSymbol()], p.Rect(c*self.config.SQUARE_SIZE, r*self.config.SQUARE_SIZE, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
            p.display.flip()
            clock.tick(60)


    '''
    Highlight square selected and moves for piece selected
    '''
    def highlightSquares(self, screen, gs, validMoves, sqSelected):
        
        if sqSelected != ():
            r, c = sqSelected
            if not MovementUtil.isEmpty(gs.board[r][c]) and gs.board[r][c].getColor() == (Color.WHITE if gs.whiteToMove else Color.BLACK): #select a piece that can be moved
                s = p.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
                s.set_alpha(100) #transparency value -> 0 transparent
                s.fill(p.Color('blue'))
                screen.blit(s, (c*self.config.SQUARE_SIZE, r*self.config.SQUARE_SIZE))
                
                # possible moves
                circeSurface = p.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE), p.SRCALPHA)
                lightGrey = (192, 192, 192, 100)
                p.draw.circle(circeSurface, lightGrey, (self.config.SQUARE_SIZE//2, self.config.SQUARE_SIZE//2), self.config.SQUARE_SIZE//5)

                # capture moves
                s.fill(p.Color('red'))
                for move in validMoves:
                    moveStartR, moveStartC = move.startRow, move.startCol
                    moveEndR, moveEndC = move.endRow, move.endCol
                    if moveStartR == r and moveStartC == c:
                        if not MovementUtil.isEmpty(self.board[moveEndR][moveEndC]) and self.board[moveStartR][moveStartC].isOpponent(self.board[moveEndR][moveEndC]):
                            screen.blit(s, (moveEndC*self.config.SQUARE_SIZE, moveEndR*self.config.SQUARE_SIZE))
                        else:
                            screen.blit(circeSurface, (moveEndC*self.config.SQUARE_SIZE, moveEndR*self.config.SQUARE_SIZE))
        
        
        if self.moveLog:
            lastMove = self.moveLog[-1]
            moves = [(lastMove.startRow, lastMove.startCol), (lastMove.endRow, lastMove.endCol)]
            for move in moves:
                r, c = move
                s = p.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
                s.set_alpha(100) #transparency value -> 0 transparent
                s.fill(p.Color('yellow'))
                screen.blit(s, (c*self.config.SQUARE_SIZE, r*self.config.SQUARE_SIZE))
            
    '''
    Make move
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = self.config.EMPTY_SQUARE
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # logs move
        self.whiteToMove = not self.whiteToMove
       
        # update king's position if moved
        if isinstance(move.pieceMoved, King):
            self.kingsPosition[move.pieceMoved.getColor()] = (move.endRow, move.endCol)

        # pawn promotion (Can incorporate promotion to other pieces and write a GUI)
        if isinstance(move.pieceMoved, Pawn) and move.isPawnPromotion:
            self.handlePawnPromotion(move)
            
        
        # en passant move
        if move.isEnPassant:
            self.board[move.startRow][move.endCol] = self.config.EMPTY_SQUARE  #capturing
        
        if isinstance(move.pieceMoved, Pawn) and abs(move.startRow - move.endRow) == 2:
            self.canEnPassant = ((move.startRow + move.endRow // 2), move.startCol)
        else:
            self.canEnPassant = ()
            
        # castle move    
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = self.config.EMPTY_SQUARE
            else: # queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = self.config.EMPTY_SQUARE
            
        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(self.currentCastlingRights.clone())
        self.canEnPassantLog.append(self.canEnPassant)
        
        
 
    def undoMove(self):
        if not self.moveLog:
            return "First Move"
        
        lastMove = self.moveLog.pop()
        self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
        self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
        self.whiteToMove = not self.whiteToMove
        
        # update king position
        if isinstance(lastMove.pieceMoved, King):
            self.kingsPosition[lastMove.pieceMoved.getColor()] = (lastMove.startRow, lastMove.startCol)
        
        # undo enpassant
        if lastMove.isEnPassant:
            self.board[lastMove.endRow][lastMove.endCol] = "--"
            self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
            self.canEnPassant = ((lastMove.startRow + lastMove.endRow // 2), lastMove.startCol)
            
        self.canEnPassantLog.pop()
        self.canEnPassant = self.canEnPassantLog[-1]
        # undo castle rights
        self.castleRightsLog.pop()
        self.currentCastlingRights = self.castleRightsLog[-1]
   
        # undo castle move
        if lastMove.isCastleMove:
            if lastMove.endCol - lastMove.startCol == 2: #king side
                self.board[lastMove.endRow][lastMove.endCol + 1] = self.board[lastMove.endRow][lastMove.endCol - 1]
                self.board[lastMove.endRow][lastMove.endCol - 1] = self.config.EMPTY_SQUARE
            else:
                self.board[lastMove.endRow][lastMove.endCol - 2] = self.board[lastMove.endRow][lastMove.endCol + 1]
                self.board[lastMove.endRow][lastMove.endCol + 1] = self.config.EMPTY_SQUARE
        
        # undo pawn promotion

        if lastMove.isPawnPromotion:
            self.board[lastMove.startRow][lastMove.startCol] = Pawn(lastMove.pieceMoved.getColor())
            
        self.checkMate = False
        self.staleMate = False

    '''
    Castling
    '''
    
    def updateCastleRights(self, move):
        color = move.pieceMoved.getColor()
        
        if isinstance(move.pieceMoved, King):
            self.currentCastlingRights.kingSide[color] = False
            self.currentCastlingRights.queenSide[color] = False
        elif isinstance(move.pieceMoved, Rook):
            if (move.startRow == 7 and color == Color.WHITE) or \
            (move.startRow == 0 and color == Color.BLACK):
                if move.startCol == 0:  # Queenside rook
                    self.currentCastlingRights.queenSide[color] = False
                elif move.startCol == 7:  # Kingside rook
                    self.currentCastlingRights.kingSide[color] = False
        
        # Handle rook captures
        if isinstance(move.pieceCaptured, Rook):
            if move.endRow == 7 or move.endRow == 0:
                if move.endCol == 0:  # Queenside rook
                    self.currentCastlingRights.queenSide[move.pieceCaptured.getColor()] = False
                elif move.endCol == 7:  # Kingside rook
                    self.currentCastlingRights.kingSide[move.pieceCaptured.getColor()] = False   
    '''
    Pawn Promotion
    '''
    
    def handlePawnPromotion(self, move):
        promotedPieceType = self.promptUserPromotion()
        self.promotePawn(move.endRow, move.endCol, promotedPieceType)
    
    def promptUserPromotion(self):
        while True:
            userInput = input("Enter a promotion piece (Q/B/N/R): ").upper()
            if userInput in ['Q', 'R', 'B', 'N']:
                return userInput
            else:
                print("Invalid Input")
            
    def promotePawn(self, r, c, pieceType):
        color = self.board[r][c].getColor()
        if pieceType == 'Q':
            newPiece = Queen(color)
        elif pieceType == 'R':
            newPiece = Rook(color)
        elif pieceType == 'B':
            newPiece = Bishop(color)
        elif pieceType == 'N':
            newPiece = Knight(color)      
        

        self.board[r][c] = newPiece
    
    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        moves = []
        activeColor = Color.WHITE if self.whiteToMove else Color.BLACK
        kingPosition = self.kingsPosition[activeColor]
        kingR, kingC = kingPosition[0], kingPosition[1]
        self.checks, self.pins, self.inCheck = MovementUtil.detectThreatsAndPins(self.board, kingR, kingC, activeColor)

        for r in range(self.config.DIMENSION):
            for c in range(self.config.DIMENSION):
                piece = self.board[r][c]
                if MovementUtil.isEmpty(piece): continue
                if piece.color == activeColor:
                    context = {"board": self.board, "checks": self.checks, "pins": self.pins, "inCheck": self.inCheck, "enPassant": self.canEnPassant, "castleRights": self.currentCastlingRights, "kingPosition": kingPosition}
                    moves.extend(piece.getPieceMoves(r, c, context)) # avoids making a new object every time if i use string 'wb' board
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
              
        return moves
    
    

    

            
    
    
    

    

        
        