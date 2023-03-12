from typing import Tuple
from random import random, randint


class Rectangle:

    def __init__(self, x: int, y: int, width: int, height: int) -> None:

        self.x = x
        self.y = y
        self.right = x + width -1
        self.bottom = y + height -1
        self.width = width
        self.height = height

    def __contains__(self, other: Tuple[int, int]) -> bool:

        abscisse = self.x <= other[0] <= self.right
        ordoonee = self.y <= other[1] <= self.bottom
        if abscisse and ordoonee:
            return True
        return False

class Room(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int) -> None:

        super().__init__(x, y, width, height)

class Map_Base:

    def __init__(self, x: int, y: int, width: int, height: int, minRoomSize: int, marge: int) -> None:
        """Représente une section de map, implémentée sous la forme d'un noeud d'un arbre binaire.

        leftChild et rightChild sont équivalents à topChild et bottomChild

        Args:
            - x (int): abscisse de la section
            - y (int): ordonnée de la section
            - width (int): largeur de la section
            - height (int): hauteur de la section
            - minSize (int): taille (largeur ou hauteur) minimale d'une section
        """

        self.x = x
        self.y = y
        self.right = x + width -1
        self.bottom = y + height -1
        self.width = width
        self.height = height
        self.minRoomSize = minRoomSize
        self.marge = marge
        self.minSize = minRoomSize +marge
        self.leftChild = None
        self.rightChild = None
        self.room: Room = None
    
    def split(self) -> bool:
        """Sépare self en deux Map_Base qui deviennent ses noeuds enfants si cela est possible.

        Returns:
            - bool: split réussi
        """

        if self.leftChild != None:
            return False
        if (self.height / self.width) >= 1.25: # hauteur 25% plus grande que la largeur
            split_horiz = True
        elif (self.width / self.height) >= 1.25: # largeur 25% plus grande que la hauteur
            split_horiz = False
        else:
            split_horiz = random() > 0.5

        match split_horiz:
            case True:
                max = self.height - self.minSize
            case False:
                max = self.width - self.minSize
        if max <= self.minSize: # plus assez de place
            return False

        cut = randint(self.minSize, max) # split location

        if split_horiz:
            self.leftChild = Map_Base(self.x, self.y, self.width, cut, self.minRoomSize, self.marge)
            self.rightChild = Map_Base(self.x, self.y + cut, self.width, self.height - cut, self.minRoomSize, self.marge)
        else:
            self.leftChild = Map_Base(self.x, self.y, cut, self.height, self.minRoomSize, self.marge)
            self.rightChild = Map_Base(self.x + cut, self.y, self.width - cut, self.height, self.minRoomSize, self.marge)

        return True

    def create_rooms(self):

        if self.leftChild != None:
            self.leftChild.create_rooms()
            self.rightChild.create_rooms()
        else:
            # la taille d'une room varie de minRoomSize x minRoomSize à la taille de la Map_base -2
            roomWidth = randint(self.minRoomSize, self.width -2)
            roomHeight = randint(self.minRoomSize, self.height -2)
            # place la map de façon à ce qu'elle ne colle pas les bords de la Map_Base
            roomX = randint(1, self.width - roomWidth)
            roomY = randint(1, self.height - roomHeight)

            self.room = Room(self.x + roomX, self.y + roomY, roomWidth, roomHeight)

class Map:

    def __init__(self, width: int, height: int, minRoomSize: int = 4, maxRoomSize: int = 10, marge: int = 4) -> None:
        """Représente la map d'un niveau.

        Args:
            width (int): largeur de la map
            height (int): hauteur de la map
            minSize (int): taille (largeur ou hauteur) minimale d'une section de la map
            maxSize (int): taille (largeur ou hauteur) maximale d'une section de la map
        """

        self.width = width
        self.height = height
        self.minRoomSize = minRoomSize
        self.maxRoomSize = maxRoomSize
        self.minSize = minRoomSize +marge
        self.maxSize = maxRoomSize +2
        assert self.maxSize > self.minSize and width > self.maxSize and height > self.maxSize

        self.root = Map_Base(0, 0, width, height, self.minRoomSize, marge)
        self.maps_list = [self.root]

        did_split = True
        while did_split:
            did_split = False
            for map in self.maps_list:
                if map.leftChild != None: # map déjà splited
                    pass
                elif map.width > self.maxSize or map.height > self.maxSize or random() > 0.25:
                    if map.split():
                        self.maps_list.append(map.leftChild)
                        self.maps_list.append(map.rightChild)
                        did_split = True
        self.root.create_rooms()
