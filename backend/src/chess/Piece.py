from abc import ABC, abstractmethod
from Utilities import PieceMove, Color, MovementUtil

class Piece(ABC):
    def __init__(self, color):
        self.color = color

    def getColor(self):
        return self.color

    @abstractmethod
    def getSymbol(self):
        pass
    
    @abstractmethod
    def getPieceMoves(self, r, c, moves, board):
        pass
    
    @abstractmethod
    def isOpponent(self, piece):
        return piece and piece.color != self.color

    @staticmethod
    def getPin(pins, pieceR, pieceC):
        pinDirection = None
        if pins:
            for pin in pins:
                if pin.pieceLocation == (pieceR, pieceC):
                    pinDirection = pin.direction
                    break
        return pinDirection
        
class Pawn(Piece):

    type = 'p'
        
    def getPieceMoves(self, r, c, moveContext):
        moves = []
        board, checks, pins, inCheck, canEnpassant, _, kingPosition = moveContext.values()
        direction = -1 if self.getColor() == Color.WHITE else 1
        kingR, kingC = kingPosition
        
        if not MovementUtil.isWithinGrid(r+direction, c): return moves

        if len(checks) == 2: return moves

        pinDirection = Piece.getPin(pins, r, c)
        
        # movement
        if not pinDirection and not inCheck and MovementUtil.isEmpty(board[r+direction][c]):
            moves.append(PieceMove((r, c), (r+direction, c), board))
            if self.isFirstMove(r) and board[r+(2*direction)][c] == "--":
                moves.append(PieceMove((r, c), (r+(2*direction), c), board))
        elif inCheck and MovementUtil.isEmpty(board[r+direction][c]):
            kingSqr = checks[0].kingLocation
            attackerSqr = checks[0].pieceLocation
            mvtSqrOne = (r+direction, c)
            mvtSqrTwo = (r+direction*2, c)
            if MovementUtil.liesBetween(kingSqr, attackerSqr, mvtSqrOne):
                moves.append(PieceMove((r, c), (r+direction, c), board))
            if MovementUtil.liesBetween(kingSqr, attackerSqr, mvtSqrTwo):
                if self.isFirstMove(r) and board[r+(2*direction)][c] == "--":
                    moves.append(PieceMove((r, c), (r+(2*direction), c), board))
        
        
        # Define pin directions for capturing left and right based on pawn's color
        leftCaptureDir = (-1, -1) if self.getColor() == Color.WHITE else (1, -1)
        rightCaptureDir = (-1, 1) if self.getColor() == Color.WHITE else (1, 1)
        
        # capture to the left
        if MovementUtil.isWithinGrid(r, c-1) and (not pinDirection or pinDirection == leftCaptureDir):
            if not MovementUtil.isEmpty(board[r+direction][c-1]) and self.isOpponent(board[r+direction][c-1]):
                moves.append(PieceMove((r, c), (r+direction, c-1), board))
            elif (r+direction, c-1) == canEnpassant:
                attackingPiece = blockingPiece = False
                pawnCol = c
                if kingR == r:
                    if kingC < pawnCol:
                        blockingPiece = self.hasBlockingPiece(board, r, kingC, pawnCol - 1)
                        attackingPiece = self.hasAttackingPiece(board, r, pawnCol + 1, 7)
                        
                    else:
                        blockingPiece = self.hasBlockingPiece(board, r, pawnCol, kingC)
                        attackingPiece = self.hasAttackingPiece(board, r, 0, pawnCol - 1)
                
                if not (attackingPiece and not blockingPiece):
                    moves.append(PieceMove((r, c), (r+direction, c-1), board, enPassant=True))
            
        # capture to the right
        if MovementUtil.isWithinGrid(r, c+1) and (not pinDirection or pinDirection == rightCaptureDir):           
            if not MovementUtil.isEmpty(board[r+direction][c+1]) and self.isOpponent(board[r+direction][c+1]):
                moves.append(PieceMove((r, c), (r+direction, c+1), board))
            elif (r+direction, c+1) == canEnpassant:
                attackingPiece = blockingPiece = False
                pawnCol = c
                if kingR == r:
                    if kingC < pawnCol:
                        blockingPiece = self.hasBlockingPiece(board, r, kingC, pawnCol)
                        attackingPiece = self.hasAttackingPiece(board, r, pawnCol + 2, 7)

                    else:
                        blockingPiece = self.hasBlockingPiece(board, r, pawnCol + 1, kingC)
                        attackingPiece = self.hasAttackingPiece(board, r, 0, pawnCol - 1)    
                                    
                if not (attackingPiece and not blockingPiece):
                    moves.append(PieceMove((r, c), (r+direction, c+1), board, enPassant=True))
        
        return moves
    
    def hasBlockingPiece(self, board, row, start_col, end_col):
        for col in range(start_col + 1, end_col):  # Adjust as needed
            if not MovementUtil.isEmpty(board[row][col]):
                return True
        return False

    def hasAttackingPiece(self, board, row, start_col, end_col):
        for col in range(start_col, end_col + 1):  # Adjust as needed
            if isinstance(board[row][col], (Queen, Rook)):
                return True
        return False 
        
    def isFirstMove(self, startRow):
        return (self.getColor() ==  Color.WHITE and startRow == 6) or \
               (self.getColor() == Color.BLACK and startRow == 1)
    
    def getSymbol(self):
        return self.color.value + self.type
    
    def isOpponent(self, piece):
        return piece and piece.color != self.color

class Rook(Piece):

    type = 'R'
  
    def getPieceMoves(self, r, c, moveContext):
        moves = []
        directions = [(0,1), (1,0), (-1,0), (0,-1)]
        checks = moveContext['checks']
        pins = moveContext['pins']

        if len(checks) == 2: return moves
        
        pinDirection = Piece.getPin(pins, r, c)
        
        for direction in directions:
            nextR, nextC = direction  
               
            if pinDirection:
                oppositePinDirection = (-pinDirection[0], -pinDirection[1])
                if direction != pinDirection and direction != oppositePinDirection:
                    continue
         
            moves.extend(MovementUtil.getLongMoves(r, c, nextR, nextC, moveContext))
            
        return moves
    
    def getSymbol(self):
        return self.color.value + self.type
    
    def isOpponent(self, piece):
        return piece and piece.color != self.color
    
class Knight(Piece):

    type = 'N'
    
    def getPieceMoves(self, r, c, moveContext):
        moves = []
        directions = [(2,1), (2,-1), (1,2), (-1,2), (1,-2), (-2,-1), (-2,1), (-1,-2)]
        board, checks, pins, inCheck, _, _, _ = moveContext.values()
        
        if len(checks) == 2: return moves
        
        pinDirection = Piece.getPin(pins, r, c)

        if pinDirection: return moves
        
        for direction in directions:
            nextR, nextC = direction[0] + r, direction[1] + c

            if inCheck:
                kingSqr = checks[0].kingLocation
                attackerSqr = checks[0].pieceLocation
                mvtSqr = (nextR, nextC)
                if MovementUtil.liesBetween(kingSqr, attackerSqr, mvtSqr):
                    moves.append(PieceMove((r, c), (nextR, nextC), board))
            elif not inCheck:
                if MovementUtil.isWithinGrid(nextR, nextC):
                    if MovementUtil.isEmpty(board[nextR][nextC]) or self.isOpponent(board[nextR][nextC]):
                        moves.append(PieceMove((r, c), (nextR, nextC), board))
            
        return moves
    
    def getSymbol(self):
        return self.color.value + self.type

    def isOpponent(self, piece):
        return piece and piece.color != self.color
      
class King(Piece):

    type = 'K'

    def getPieceMoves(self, r, c, moveContext):
        moves = []
        directions = [(0,1), (1,0), (-1,0), (0,-1), (1,1), (-1,-1), (-1,1), (1,-1)]
        board = moveContext['board']
        inCheck = moveContext['inCheck']

        for direction in directions:
            nextR, nextC = direction[0] + r, direction[1] + c
            if MovementUtil.isWithinGrid(nextR, nextC):
                if not MovementUtil.isEmpty(board[nextR][nextC]) and not self.isOpponent(board[nextR][nextC]):
                    continue
                
                # check if the squares around the king is attacked
                _, _, inCheck = MovementUtil.detectThreatsAndPins(board, nextR, nextC, board[r][c].getColor())
    
                if inCheck: 
                    continue

                if MovementUtil.isEmpty(board[nextR][nextC]) or self.isOpponent(board[nextR][nextC]):
                    moves.append(PieceMove((r, c), (nextR, nextC), board))
        
        moves.extend(self.getCastleMoves(r, c, moveContext))
        
        return moves
    
    def getCastleMoves(self, r, c, moveContext):
        moves = []
        inCheck = moveContext['inCheck']
        castlingRights = moveContext['castleRights']
        board = moveContext['board']
    
        color = board[r][c].getColor()
        # can't castle when in check
        if inCheck: return moves
        
        if castlingRights.kingSide[color]:
            moves.extend(self.getKingSideCastleMoves(r, c, board, color))
        
        if castlingRights.queenSide[color]:
            moves.extend(self.getQueenSideCastleMoves(r, c, board, color))
        
        return moves
        
    def getKingSideCastleMoves(self, r, c, board, color):
        moves = []
        if MovementUtil.isEmpty(board[r][c+1]) and MovementUtil.isEmpty(board[r][c+2]):
            squares = [(r, c+1), (r, c+2)]
            sqrAttacked = False
            for square in squares:
                x, y = square
                _, _, inCheck = MovementUtil.detectThreatsAndPins(board, x, y, color)
                sqrAttacked = sqrAttacked or inCheck
            
            if not sqrAttacked:
                moves.append(PieceMove((r, c), (r, c+2), board, isCastleMove=True))
            
        return moves
        
    
    def getQueenSideCastleMoves(self, r, c, board, color):
        moves = []
        if MovementUtil.isEmpty(board[r][c-1]) and MovementUtil.isEmpty(board[r][c-2]) and MovementUtil.isEmpty(board[r][c-3]):
            squares = [(r, c-1), (r, c-2)]
            sqrAttacked = False
            for square in squares:
                x, y = square
                _, _, inCheck = MovementUtil.detectThreatsAndPins(board, x, y, color)
                sqrAttacked = sqrAttacked or inCheck
            
            if not sqrAttacked:
                moves.append(PieceMove((r, c), (r, c-2), board, isCastleMove=True))
            
        return moves
        
    def getSymbol(self):
        return self.color.value + self.type

    def isOpponent(self, piece):
        return piece and piece.color != self.color

class Queen(Piece):
    
    type = 'Q'

    def getPieceMoves(self, r, c, moveContext):
        moves = []
 
        directions = [(0,1), (1,0), (-1,0), (0,-1),(1,1), (-1,1), (1,-1), (-1,-1)]
        pins = moveContext['pins']
        
        pinDirection = Piece.getPin(pins, r, c)

        for direction in directions:
            nextR, nextC = direction
            if pinDirection:
                oppositePinDirection = (-pinDirection[0], -pinDirection[1])
                if direction != pinDirection and direction != oppositePinDirection:
                    continue    
            moves.extend(MovementUtil.getLongMoves(r, c, nextR, nextC, moveContext))
            

        return moves
    
    def getSymbol(self):
        return self.color.value + self.type

    def isOpponent(self, piece):
        return piece and piece.color != self.color
    
class Bishop(Piece):
    
    type = 'B'
    
    def getPieceMoves(self, r, c, moveContext):
        moves = []
        directions = [(1,1), (-1,1), (1,-1), (-1,-1)]
        pins = moveContext['pins']
        
        pinDirection = Piece.getPin(pins, r, c)
        for direction in directions:
            nextR, nextC = direction   
            if pinDirection:
                oppositePinDirection = (-pinDirection[0], -pinDirection[1])
                if direction != pinDirection and direction != oppositePinDirection:
                    continue          
            moves.extend(MovementUtil.getLongMoves(r, c, nextR, nextC, moveContext))
            
        return moves
    
    def getSymbol(self):
        return self.color.value + self.type

    def isOpponent(self, piece):
        return piece and piece.color != self.color


