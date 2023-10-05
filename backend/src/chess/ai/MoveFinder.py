import random

from Utilities import Color
from Piece import Knight, King, Pawn, Queen, Bishop, Rook

pieceScore = {King: 0, Queen: 10, Knight: 3, Bishop: 3, Rook: 5, Pawn: 1}
knightScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]
kingScore = [[4, 4, 3, 3, 3, 3, 4, 4],
             [4, 3, 2, 2, 2, 2, 3, 4],
             [2, 1, 1, 1, 1, 1, 1, 2],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [2, 1, 1, 1, 1, 1, 1, 2],
             [4, 3, 2, 2, 2, 2, 3, 4],
             [4, 4, 3, 3, 3, 3, 4, 4]]
queenScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]
rookScore = [[4, 4, 4, 4, 4, 4, 4, 4],
             [2, 2, 2, 2, 2, 2, 2, 2],
             [1, 1, 1, 3, 3, 1, 1, 1],
             [1, 1, 3, 4, 4, 3, 1, 1],
             [1, 1, 3, 4, 4, 3, 1, 1],
             [1, 1, 1, 3, 3, 1, 1, 1],
             [2, 2, 2, 2, 2, 2, 2, 4],
             [4, 4, 4, 4, 4, 4, 4, 4]]
bishopScore = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]
blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 0, 0, 1, 1, 1],
             [1, 1, 3, 3, 3, 3, 1, 1],
             [2, 3, 4, 4, 4, 4, 3, 2],
             [3, 5, 5, 5, 5, 5, 5, 3],
             [5, 6, 6, 6, 6, 6, 6, 5],
             [7, 7, 7, 7, 7, 7, 7, 7],
             [8, 8, 8, 8, 8, 8, 8, 8]]

whitePawnScore = [
             [8, 8, 8, 8, 8, 8, 8, 8],
             [7, 7, 7, 7, 7, 7, 7, 7],
             [5, 6, 6, 6, 6, 6, 6, 5],
             [3, 5, 5, 5, 5, 5, 5, 3],
             [2, 3, 4, 4, 4, 4, 3, 2],
             [1, 1, 3, 3, 3, 3, 1, 1],
             [1, 1, 1, 0, 0, 1, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0]]

pawnScores = {Color.WHITE: whitePawnScore, Color.BLACK: blackPawnScore}
piecePositionScores = {Knight: knightScore, Queen: queenScore, Bishop: bishopScore, King: kingScore, Rook: rookScore, Pawn: pawnScores}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


def findBestMove(gs, validMoves, returnQueue):
    global counter
    counter = 0
    bestScore, bestMove = findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1, -CHECKMATE, CHECKMATE)
    # bestScore, bestMove = findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    print(counter)
    returnQueue.put(bestMove)
    

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, turnMultiplier, alpha, beta):
    global counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs), None
    
    #move ordering - no need to look at bad branches (evaluate checks/captures first)
    
    bestMove = None
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score, _ = findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, turnMultiplier * -1, -beta, -alpha)
        score = -score
        # if score returns CHECKMATE (for white), then it becomes -CHECKMATE for our score, then the if condition
        # would not pass. we only consider a move if it is higher than our current score
        if score > maxScore:
            maxScore = score
            bestMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        
        if alpha >= beta:
            break
    
    return maxScore, bestMove
    


'''
Score the board based on material
'''
def scoreMaterial(board):
    score = 0
    for r in range(len(board)):
        for c in range(len(board[0])):
            square = board[r][c]
            if square != "--":
                #scoring positionally
                piecePositionScore = 0
                if not isinstance(square, King):
                    if isinstance(square, Pawn):
                        piecePositionScore = piecePositionScores[Pawn][square.getColor()][r][c]
                    else:
                        piecePositionScore = piecePositionScores[type(square)][r][c]
   
                if square.getColor() == Color.WHITE:
                    score += pieceScore[type(square)] + piecePositionScore*.1
                else:
                    score -= pieceScore[type(square)] + piecePositionScore*.1
    
    return score

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    
    score = scoreMaterial(gs.board)
    
    return score