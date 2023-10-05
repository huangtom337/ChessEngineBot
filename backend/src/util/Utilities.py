from enum import Enum

class PieceMove():
    # converting chess notation to indexing chess board
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    # conver to PGN potentially
    def __init__(self, startSq, endSq, board, enPassant=False, isCastleMove=False):
        self.startRow, self.startCol = startSq[0], startSq[1]
        self.endRow, self.endCol = endSq[0], endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # moveID between 0 and 7000
        
        self.isPawnPromotion = False
        if not MovementUtil.isEmpty(self.pieceMoved) and self.pieceMoved.type == 'p':
            if (self.pieceMoved.getColor() == Color.WHITE and self.endRow == 0) or \
                (self.pieceMoved.getColor() == Color.BLACK and self.endRow == 7):
                self.isPawnPromotion = True

        self.isEnPassant = enPassant
        
        if self.isEnPassant:
            self.pieceCaptured = board[self.startRow][self.endCol]  # Captured piece is at startRow but endCol
        else:
            self.pieceCaptured = board[self.endRow][self.endCol] 
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        
    '''
    Overriding the equals method
    '''
    
    def __eq__(self, other):
        if isinstance(other, PieceMove):
            return self.moveID == other.moveID
        return False
        
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    # overriding str function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankFile(self.endRow, self.endCol)
        
        if self.pieceMoved.type == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
                

            #pawn promotion
        
        #two of the same type of piece moving to the same square
        
        #adding + for checkmove and # for checkmate
        
        #piece moves
        
        moveString = self.pieceMoved.type
        if self.isCapture:
            moveString += 'x'
        
        return moveString + endSquare
        
class Color(Enum):
    WHITE = "w"
    BLACK = "b"

class Check():
    def __init__(self, kingLocation, pieceLocation, direction):
        self.kingLocation = kingLocation
        self.pieceLocation = pieceLocation
        self.direction = direction

class Pin():
    def __init__(self, kingLocation, pieceLocation, direction):
        self.kingLocation = kingLocation
        self.pieceLocation = pieceLocation
        self.direction = direction

class MovementUtil():
    
    @staticmethod
    def isWithinGrid(endRow, endCol):
        return 0 <= endRow <= 7 and 0 <= endCol <= 7
    
    @staticmethod
    def getLongMoves(r, c, nextR, nextC, moveContext):
        moves = []
        board, checks, _, inCheck, _, _, _ = moveContext.values()
        currPiece = board[r][c]
        i, j = r + nextR, c + nextC
        allyPiece = False
        
        while MovementUtil.isWithinGrid(i, j):
            if not MovementUtil.isEmpty(board[i][j]) and not board[i][j].isOpponent(currPiece):
                allyPiece = True
                
            if inCheck:
                kingSqr = checks[0].kingLocation
                attackerSqr = checks[0].pieceLocation
                mvtSqr = (i, j)
                if MovementUtil.liesBetween(kingSqr, attackerSqr, mvtSqr) and not allyPiece:
                    moves.append(PieceMove((r, c), (i, j), board))
            elif not inCheck: 
                if MovementUtil.isEmpty(board[i][j]):
                    moves.append(PieceMove((r, c), (i, j), board))
                elif board[i][j].isOpponent(currPiece):
                    moves.append(PieceMove((r, c), (i, j), board))
                    break
                else:
                    break
            i, j = i + nextR, j + nextC
        
        return moves
        
        
        
        
    @staticmethod
    def isEmpty(piece):
        return piece == "--"
    
    @staticmethod
    def liesBetween(kingSqr, attackerSqr, pieceSqr):
        kingToAttacker = [attackerSqr[0] - kingSqr[0] , attackerSqr[1] - kingSqr[1]] 
        kingToPiece = [pieceSqr[0] - kingSqr[0], pieceSqr[1] - kingSqr[1]]
        
        
        dotProduct = kingToAttacker[0]*kingToPiece[0] + kingToAttacker[1]*kingToPiece[1]
        crossProduct = kingToAttacker[0]*kingToPiece[1] - kingToAttacker[1]*kingToPiece[0]
        magnitudeKingPiece = kingToAttacker[0]**2 + kingToAttacker[1]**2

        if crossProduct != 0: return False
        
        return 0 < dotProduct <= magnitudeKingPiece
    
  
    def detectStraightThreats(board, color, r, c):
        checks = []
        pins = []
        inCheck = False
        straightDirections = [(0,1), (1,0), (-1,0), (0,-1)]
        for straightDirection in straightDirections:
                allyPiece = 0
                nextR, nextC = straightDirection            
                i, j = r + nextR, c + nextC
                potentialPin = None  # This will store the position of the potentially pinned piece
                while MovementUtil.isWithinGrid(i, j):
                    if MovementUtil.isEmpty(board[i][j]):
                        pass
                    elif board[i][j].getColor() != color:
        
                        if board[i][j].type == "Q" or board[i][j].type == 'R':
                            if allyPiece == 0:
                                check = Check((r, c), (i, j), straightDirection)
                                checks.append(check)
                                inCheck = True
                            if potentialPin and allyPiece == 1:  # We have a pin
                                pins.append(potentialPin)
                        break
                    else:
                        if not potentialPin:
                            potentialPin = Pin((r, c), (i, j), straightDirection)
                        
                        allyPiece += 1
                        
                    i, j = i + nextR, j + nextC
        return checks, pins, inCheck
        
        
    def detectDiagonalThreats(board, color, r, c):
        checks = []
        pins = []
        inCheck = False
        diagonalDirections = [(1,1), (-1,1), (1,-1), (-1,-1)]
        for diagonalDirection in diagonalDirections:
            allyPiece = 0
            nextR, nextC = diagonalDirection            
            i, j = r + nextR, c + nextC
            potentialPin = None  # This will store the position of the potentially pinned piece
            while MovementUtil.isWithinGrid(i, j):
                if MovementUtil.isEmpty(board[i][j]):
                    pass
                elif board[i][j].getColor() != color:
                    
                    # For white pawn threatening
                    if board[i][j].type == 'p' and board[i][j].getColor() == Color.BLACK and (i - r == -1) and abs(j - c) == 1:
                        inCheck = True
                        check = Check((r, c), (i, j), diagonalDirection)
                        checks.append(check)
                        
                        
                    # For black pawn threatening
                    elif board[i][j].type == 'p'and board[i][j].getColor() == Color.WHITE and (i - r == 1) and abs(j - c) == 1:
                        inCheck = True
                        check = Check((r, c), (i, j), diagonalDirection)
                        checks.append(check)
                    
                    
                    elif board[i][j].type == 'Q' or board[i][j].type == 'B':
                        if allyPiece == 0:
                            check = Check((r, c), (i, j), diagonalDirection)
                            checks.append(check)
                            inCheck = True
                        if potentialPin and allyPiece == 1:  # We have a pin
                            pins.append(potentialPin)
                    
                    break
                else:
                    if not potentialPin:
                        potentialPin = Pin((r, c), (i, j), diagonalDirection)
                    
                    allyPiece += 1
                    
                i, j = i + nextR, j + nextC  
        return checks, pins, inCheck 

    def detectKnightThreats(board, color, r, c):
        checks = []
        inCheck = False
        knightDirections = [(2,1), (2,-1), (1,2), (-1,2), (1,-2), (-2,-1), (-2,1), (-1,-2)]
        for knightDirection in knightDirections:
            nextR, nextC = knightDirection[0] + r, knightDirection[1] + c
            
            if MovementUtil.isWithinGrid(nextR, nextC):
                if MovementUtil.isEmpty(board[nextR][nextC]):
                    pass
                elif board[nextR][nextC].getColor() != color:
                    if board[nextR][nextC].type == 'N':
                        check = Check((r, c), (nextR, nextC), knightDirection)
                        checks.append(check)
                        inCheck = True
        
        return checks, inCheck
    
    def detectKingThreats(board, color, r, c):
        checks = []
        inCheck = False
        # Separate loop just for King's threats
        
        kingDirections = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for kingDirection in kingDirections:
            nextR, nextC = kingDirection[0] + r, kingDirection[1] + c
            if MovementUtil.isWithinGrid(nextR, nextC) and not MovementUtil.isEmpty(board[nextR][nextC]):
                if board[nextR][nextC].type == 'K' and board[nextR][nextC].getColor() != color:
                    check = Check((r, c), (nextR, nextC), kingDirection)
                    checks.append(check)
                    inCheck = True
        
        return checks, inCheck
    
    @staticmethod
    def detectThreatsAndPins(board, r, c, color):
    
        checks = [] # (pieceLocation, checkingPieceLocation, direction)
        pins = [] # (pieceLocation, checkingPieceLocation, direction)
        inCheck = False
    
        straightChecks, straightPins, straightInCheck = MovementUtil.detectStraightThreats(board, color, r, c)
        diagonalChecks, diagonalPins, diagonalInCheck = MovementUtil.detectDiagonalThreats(board, color, r, c)
        knightChecks, knightInCheck = MovementUtil.detectKnightThreats(board, color, r, c)
        kingChecks, kingInCheck = MovementUtil.detectKingThreats(board, color, r, c)
        
        checks.extend(straightChecks + diagonalChecks + knightChecks + kingChecks)
        pins.extend(straightPins + diagonalPins)
        inCheck = straightInCheck or diagonalInCheck or knightInCheck or kingInCheck

        
        return checks, pins, inCheck
    
class CastleMove():
    def __init__(self):
        self.kingSide = {Color.WHITE: True, Color.BLACK: True}
        self.queenSide = {Color.WHITE: True, Color.BLACK: True}
        
        
    def clone(self):
        newCastleMove = CastleMove()
        newCastleMove.kingSide = self.kingSide.copy()
        newCastleMove.queenSide = self.queenSide.copy()
        
        return newCastleMove
    