from enum import Enum
import pygame as p

class BoardConfig():
    IMAGES = {}
    BOARD_WIDTH = BOARD_HEIGHT = 512 # window size
    MOVE_LOG_PANEL_WIDTH = 250
    MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
    DIMENSION = 8 # board dimension
    SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
    MAX_FPS = 15 
    EMPTY_SQUARE = "--"
    
    
    '''
    Load images. Only called once
    '''
    @classmethod
    def loadImages(cls):
        pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
        for piece in pieces:
            cls.IMAGES[piece] = p.transform.scale(p.image.load("../../images/" + piece + ".png"), (cls.SQUARE_SIZE, cls.SQUARE_SIZE))

