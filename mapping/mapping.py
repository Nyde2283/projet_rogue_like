from typing import Tuple
from random import random, randint


class Rectangle:

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Modélise une forme rectangulaire basique.

        Args:
            - x (int): abscisse du rectangle
            - y (int): ordonnée du rectangle
            - width (int): largeur du rectangle
            - height (int): hauteur du rectangle
        """

        if x < 0 or y < 0 or width < 0 or height < 0:
            raise ValueError(f'Les coordoonées et les dimensions doivent être positive : Rectangle({x}, {y}, {width}, {height})')
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
        """Modélise une salle contenue dans une `Section`.

        Args:
            - x (int): abscisse de la salle
            - y (int): ordonnée de la salle
            - width (int): largeur de la salle
            - height (int): hauteur de la salle
        """

        super().__init__(x, y, width, height)


class Section(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int, minRoomSize: int, maxRoomSize: int, marge: int) -> None:

        leftChild et rightChild sont équivalents à topChild et bottomChild

        Args:
            - x (int): abscisse de la section
            - y (int): ordonnée de la section
            - width (int): largeur de la section
            - height (int): hauteur de la section
            - minRoomSize (int): taille (largeur ou hauteur) minimale d'une salle contenue dans une section
            - marge (int): espace entre une salle et le bord d'une section
        """

        super().__init__(x, y, width, height)
        self.minRoomSize = minRoomSize
        self.maxRoomSize = maxRoomSize
        self.marge = marge
        self.minSize = minRoomSize +marge*2
        self.maxSize = maxRoomSize +marge*2
        self.leftChild: Section = None
        self.rightChild: Section = None
        self.room: Room = None
    
    def split(self) -> bool:
        """Sépare self en deux Section qui deviennent ses noeuds enfants si cela est possible.

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
        if max <= self.maxSize and random() > 0.1:
            return False

        cut = randint(self.minSize, max) # split location

        if split_horiz:
            self.leftChild = Section(self.x, self.y, self.width, cut, self.minRoomSize, self.maxRoomSize, self.marge)
            self.rightChild = Section(self.x, self.y + cut, self.width, self.height - cut, self.minRoomSize, self.maxRoomSize, self.marge)
        else:
            self.leftChild = Section(self.x, self.y, cut, self.height, self.minRoomSize, self.maxRoomSize, self.marge)
            self.rightChild = Section(self.x + cut, self.y, self.width - cut, self.height, self.minRoomSize, self.maxRoomSize, self.marge)

        return True

    def create_rooms(self):
        """Génère les salles de la Section ou de ses enfants.
        """

        if self.leftChild != None:
            self.leftChild.create_rooms()
            self.rightChild.create_rooms()
        else:
            # la taille d'une room varie de minRoomSize x minRoomSize à la taille de la Section - la marge
            roomWidth = randint(self.minRoomSize, self.width - self.marge*2)
            roomHeight = randint(self.minRoomSize, self.height - self.marge*2)
            # place la map de façon à ce qu'elle ne colle pas les bords de la Section
            roomX = randint(self.marge, self.width - roomWidth - self.marge)
            roomY = randint(self.marge, self.height - roomHeight - self.marge)

            self.room = Room(self.x + roomX, self.y + roomY, roomWidth, roomHeight)

class Map:

    def __init__(self, width: int, height: int, minRoomSize: int = 4, maxRoomSize: int = 10, marge: int = 1) -> None:
        """Représente la map d'un niveau.

        Args:
            - width (int): largeur de la map
            - height (int): hauteur de la map
            - minRoomSize (int): taille (largeur ou hauteur) minimale d'une salle contenue dans une section
            - maxRoomSize (int): taille (largeur ou hauteur) maximale d'une salle contenue dans une section
            - marge (int): espace entre une salle et le bord d'une section
        """

        self.width = width
        self.height = height
        self.minRoomSize = minRoomSize
        self.maxRoomSize = maxRoomSize
        self.minSize = minRoomSize +marge*2
        self.maxSize = maxRoomSize +marge*2
        if self.maxSize <= self.minSize or width <= self.maxSize or height <= self.maxSize:
            raise ValueError

        self.root = Section(0, 0, width, height, self.minRoomSize, self.maxRoomSize, marge)
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
