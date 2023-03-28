from __future__ import annotations
from typing import Tuple, List, Sequence
from random import random, randint

NORD = 'N'
SUD = 'S'
OUEST = 'O'
EST = 'E'

class Point:

    def __init__(self, x: int, y: int) -> None:
        """Modélise un point.

        Args:
            - x (int): abscisse
            - y (int): ordonnée
        """

        if x < 0 or y < 0:
            raise ValueError(f'Les coordonnées doivent être positives : Point({x}, {y})')
        self.x = x
        self.y = y

    def __eq__(self, __o: object) -> bool:

        return type(__o) == Point and self.x == __o.x and self.y == __o.y

    def __str__(self) -> str:

        return f'({self.x}, {self.y})'

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

    def __contains__(self, __o: Tuple[int, int] | Point) -> bool:

        match __o:
            case tuple():
                abscisse = self.x <= __o[0] <= self.right
                ordoonee = self.y <= __o[1] <= self.bottom
            case Point():
                abscisse = self.x <= __o.x <= self.right
                ordoonee = self.y <= __o.y <= self.bottom
            case _:
                raise TypeError(f'type(__o) -> {type(__o)}')
        if abscisse and ordoonee:
            return True
        return False

    def __eq__(self, __o) -> bool:

        return type(__o) == Rectangle and self.x == __o.x and self.y == __o.y and self.width == __o.width and self.height == __o.height

    def __str__(self) -> str:

        return f'[from ({self.x}, {self.y}) to ({self.right}, {self.bottom}) size({self.width} x {self.height})]'

class Hall(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int, doors: List[Door]) -> None:
        """Modélise un couloir entre deux salles.

        Args:
            - x (int): abscisse
            - y (int): ordonnée
            - width (int): largeur
            - height (int): hauteur
            - doors (List[Door]): les deux portes du couloir
        """

        if len(doors) != 2:
            raise ValueError(f'Il doit y avoir deux portes : Hall(..., {doors})')
        super().__init__(x, y, width, height)
        self.doors_list: List[Door] = doors

    def __str__(self) -> str:

        return super().__str__()

class Door(Point):

    def __init__(self, x: int, y: int) -> None:
        """Modélise la porte d'une salle.

        Args:
            x (int): abscisse
            y (int): ordonnée
        """

        super().__init__(x, y)

    def is_around(self, x: int, y: int) -> bool:
        """Méthode booléenne pour savoir si la porte est à côté du point en (x, y).

        Args:
            x (int): abscisse
            y (int): ordonnée

        Returns:
            bool: si la porte est à côté
        """

        for x_ in range(x-1, x+2):
            for y_ in range(y-1, y+2):
                if x_ == self.x or y_ == self.y:
                    return True
        return False

class Room(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int, parentSection: Section) -> None:
        """Modélise une salle contenue dans une `Section`.

        Args:
            - x (int): abscisse de la salle
            - y (int): ordonnée de la salle
            - width (int): largeur de la salle
            - height (int): hauteur de la salle
            - parentSection (Section): Section contenant la salle
        """

        if type(parentSection) != Section:
            raise TypeError(f'Not a Section : Room(..., {parentSection})')
        super().__init__(x, y, width, height)
        self.parentSection = parentSection

    def can_place_door(self, x: int, y: int) -> bool:
        """Méthode booléenne donnant la possibilité ou non de placer une porte au coordoonées (x, y) pour la salle.

        Args:
            - x (int): abscisse de la supposée porte
            - y (int): ordonnée de la supposée porte

        Returns:
            bool: possibilité de placer une porte en (x, y)
        """

        abscisse = self.x < x < self.right # est-ce que x est "à l'intérieur" de la salle
        ordonnee = self.y < y < self.bottom # --------- y -------------------------------
        for door in self.parentSection.doors_list:
            if door.is_around(x, y) == True: # on vérifie qu'il n'y a pas déjà une porte à côté
                return False

        if abscisse and (y == self.y -1 or y == self.bottom +1):
            return True
        if ordonnee and (x == self.x -1 or x == self.right +1):
            return True
        return False

    def linear_search(self, root: Section, x: int, y: int, direction: str, maxLenth: int) -> Point | None:

        if maxLenth <= 0: # couloir trop long
            return None

        if root.is_hall(x-1, y) or root.is_hall(x-1, y+1) or root.is_hall(x, y+1) or root.is_hall(x+1, y+1) or root.is_hall(x+1, y) or root.is_hall(x+1, y-1) or root.is_hall(x, y-1) or root.is_hall(x-1, y-1):
            return None

        if x < root.x or x > root.right or y < root.y or y > root.bottom: # en dehors de la Map
            return None

        N = root.is_room(x, y-1)
        E = root.is_room(x+1, y)
        S = root.is_room(x, y+1)
        O = root.is_room(x-1, y)
        match direction:
            case 'N':
                if O or E: # si il y a une salle à côté du couloir
                    return None
                if N: # si il y a une salle au dessus du couloir
                    if root.get_room(x, y-1).can_place_door(x, y):
                        return Point(x, y)
                    return None
                return self.linear_search(root, x, y-1, direction, maxLenth -1)
            case 'S':
                if O or E:
                    return None
                if S:
                    if root.get_room(x, y+1).can_place_door(x, y):
                        return Point(x, y)
                    return None
                return self.linear_search(root, x, y+1, direction, maxLenth -1)
            case 'O':
                if N or S:
                    return None
                if O:
                    if root.get_room(x-1, y).can_place_door(x, y):
                        return Point(x, y)
                    return None
                return self.linear_search(root, x-1, y, direction, maxLenth -1)
            case 'E':
                if N or S:
                    return None
                if E:
                    if root.get_room(x+1, y).can_place_door(x, y):
                        return Point(x, y)
                    return None
                return self.linear_search(root, x+1, y, direction, maxLenth -1)

class Section(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int, minRoomSize: int, maxRoomSize: int, marge: int) -> None:
        """Modélise une section de map, implémentée sous la forme d'un noeud d'un arbre binaire.

        leftChild et rightChild sont équivalents à topChild et bottomChild

        Args:
            - x (int): abscisse de la section
            - y (int): ordonnée de la section
            - width (int): largeur de la section
            - height (int): hauteur de la section
            - minRoomSize (int): taille (largeur ou hauteur) minimale d'une salle contenue dans une section
            - marge (int): espace entre une salle et le bord d'une section
        """

        if minRoomSize <= 2 or maxRoomSize < minRoomSize or marge < 0:
            raise ValueError(f'Il y un problème dans les valeurs : Section(..., {minRoomSize}, {maxRoomSize}, {self.marge})')

        super().__init__(x, y, width, height)
        self.minRoomSize = minRoomSize
        self.maxRoomSize = maxRoomSize
        self.marge = marge
        self.minSize = minRoomSize +marge*2
        self.maxSize = maxRoomSize +marge*2
        self.leftChild: Section = None
        self.rightChild: Section = None
        self.room: Room = None
        self.doors_list: List[Door] = []
        self.halls_list: List[Hall] = []
    
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

            self.room = Room(self.x + roomX, self.y + roomY, roomWidth, roomHeight, self)

    def get_room(self, x: int, y: int) -> Room | None:
        """Retourne la Room en (x, y) si elle existe sinon elle retourne None

        Args:
            x (int): abscisse
            y (int): ordonnée

        Returns:
            Room | None
        """

        last = self.get_leafSection(x, y)
        if (x, y) in last.room:
            return last.room
        return None

    def is_room(self, x: int, y: int) -> bool:
        """Indique si le bloque en (x, y) appartient à une salle.

        Args:
            x (int): abscisse du bloque
            y (int): ordonnée du bloque

        Returns:
            bool: le bloque appartient à une salle
        """

        last = self.get_leafSection(x, y)
        return (x, y) in last.room

    def get_leafSection(self, x: int, y: int) -> Section | None:
        """Retourne la section la plus basse de l'arbre au coordonnées (x, y).

        Args:
            x (int): abscisse
            y (int): ordonnée

        Returns:
            Section | None
        """

        if self.leftChild == None:
            return self
        if self.width == self.leftChild.width: # split horizontal
            if y >= self.rightChild.y:
                return self.rightChild.get_leafSection(x, y)
            return self.leftChild.get_leafSection(x, y)
        else:
            if x >= self.rightChild.x:
                return self.rightChild.get_leafSection(x, y)
            return self.leftChild.get_leafSection(x, y)

    def is_hall(self, x: int, y: int):

        last = self.get_leafSection(x, y)
        for hall in last.halls_list:
            if (x, y) in hall:
                return True
        return False

    def _create_verti_halls(self, root: Section, maxLenth: int):

        tradDirection = {NORD: -1, SUD: 1}

        for y, direction in zip((self.room.y -1, self.room.bottom +1), (NORD, SUD)): # au dessus et en dessous de la salle
            for x in range(self.room.x +1, self.room.right): # "à l'intérieur" de la salle
                search = self.room.linear_search(root, x, y, direction, maxLenth)

                if search == None: # recherche infructueuse
                    continue

                foundSection = root.get_leafSection(search.x, search.y +tradDirection[direction]) # section où se trouve la salle cible
                canPlace = True
                for hall in self.halls_list:
                    if hall in foundSection.halls_list: # empêche de placer plusieurs couloirs entre 2 salles
                        canPlace = False
                if not canPlace:
                    continue

                P1 = Point(x, y)
                P2 = search
                door1 = Door(P1.x, P1.y)
                door2 = Door(P2.x, P2.y)
                if P1.y < P2.y: # si P1 est au dessus de P2
                    newHall = Hall(
                        P1.x,
                        P1.y,
                        1,
                        P2.y - P1.y +1,
                        [door1, door2]
                    )
                else: # si P1 est en dessous de P2
                    newHall = Hall(
                        P2.x,
                        P2.y,
                        1,
                        P1.y - P2.y +1,
                        [door2, door1]
                    )
                self.doors_list.append(door1)
                foundSection.doors_list.append(door2)

                lastSectionCrossed = None
                for y_ in range(newHall.y, newHall.bottom +1): # ajout du couloir aux sections traversées
                    sectionTested = root.get_leafSection(x, y_) # le x vient de la boucle plus haute
                    if sectionTested == lastSectionCrossed:
                        continue
                    sectionTested.halls_list.append(newHall)
                    lastSectionCrossed = sectionTested

    def _create_horiz_halls(self, root: Section, maxLenth: int):

        tradDirection = {OUEST: -1, EST: 1}

        for x, direction in zip((self.room.x -1, self.room.right +1), (OUEST, EST)): # à droite et à gauche de la salle
            for y in range(self.room.y +1, self.room.bottom): # "à l'intérieur" de la salle
                search = self.room.linear_search(root, x, y, direction, maxLenth)

                if search == None:
                    continue

                foundSection = root.get_leafSection(search.x +tradDirection[direction], search.y)
                canPlace = True
                for hall in self.halls_list:
                    if hall in foundSection.halls_list:
                        canPlace = False
                if not canPlace:
                    continue

                P1 = Point(x, y)
                P2 = search
                door1 = Door(P1.x, P1.y)
                door2 = Door(P2.x, P2.y)
                if P1.x < P2.x: # si P1 est à gauche de P2
                    newHall = Hall(
                        P1.x,
                        P1.y,
                        P2.x - P1.x +1,
                        1,
                        [door1, door2]
                    )
                else:
                    newHall = Hall(
                        P2.x,
                        P2.y,
                        P1.x - P2.x +1,
                        1,
                        [door2, door1]
                    )
                self.doors_list.append(door1)
                foundSection.doors_list.append(door2)

                lastSectionCrossed = None
                for x_ in range(newHall.x, newHall.right +1):
                    sectionTested = root.get_leafSection(x_, y)
                    if sectionTested == lastSectionCrossed:
                        continue
                    sectionTested.halls_list.append(newHall)
                    lastSectionCrossed = sectionTested

    def create_linear_halls(self, root: Section, maxLenth: int):

        if self.room != None:
            self._create_verti_halls(root, maxLenth)
            self._create_horiz_halls(root, maxLenth)
        else:
            self.leftChild.create_linear_halls(root, maxLenth)
            self.rightChild.create_linear_halls(root, maxLenth)

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
        self.root.create_linear_halls(self.root, 20)

