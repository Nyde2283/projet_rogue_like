from __future__ import annotations
from typing import Tuple, List, Iterator, Dict
from random import random, randint

from PIL import Image

import assets.map_bg as map_bg

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

        try:
            return isinstance(__o, Point) and self.x == __o.x and self.y == __o.y
        except:
            return False

    def __str__(self) -> str:

        return f'({self.x}, {self.y})'

    def __iter__(self) -> Iterator:

        return iter([self.x, self.y])

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

        try:
            return isinstance(__o, Rectangle) and self.x == __o.x and self.y == __o.y and self.width == __o.width and self.height == __o.height
        except:
            return False

    def __str__(self) -> str:

        return f'[from ({self.x}, {self.y}) to ({self.right}, {self.bottom}) size({self.width} x {self.height})]'

class Hall(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int, doors: List[Door], rooms: List[Room]) -> None:
        """Modélise un couloir entre deux salles.

        Args:
            - x (int): abscisse
            - y (int): ordonnée
            - width (int): largeur
            - height (int): hauteur
            - doors (List[Door]): les deux portes du couloir
            - rooms (List[Room]): les deux salles reliées par le couloir
        """

        if len(doors) != 2:
            raise ValueError(f'Il doit y avoir deux portes : Hall(..., {doors})')
        super().__init__(x, y, width, height)
        self.doors_list: List[Door] = doors
        self.rooms_list: List[Room] = rooms

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

class Wall(Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Modélise un mur.

        Args:
            - x (int): abscisse
            - y (int): ordonnée
            - width (int): largeur
            - height (int): hauteur
        """

        super().__init__(x, y, width, height)

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

        abscisse = self.x+1 < x < self.right-1 # est-ce que x est "à l'intérieur" de la salle
        ordonnee = self.y+1 < y < self.bottom-1 # --------- y -------------------------------

        if abscisse and (y == self.y -1 or y == self.bottom +1):
            return True
        if ordonnee and (x == self.x -1 or x == self.right +1):
            return True
        return False

    def linear_search(self, root: Section, x: int, y: int, direction: str, maxLenth: int) -> Point | None:

        if maxLenth <= 0: # couloir trop long
            return None

        for deltaX in (-1, 0, 1):
            for deltaY in (-1, 0, 1):
                if deltaX == 0 and deltaY == 0:
                    continue
                if root.is_hall(x +deltaX, y +deltaY): # si il y un couloir trop proche
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
            - maxRoomSize (int): --------------------------- maximale -------------------------------------
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
        self.walls_list: List[Wall] = []
    
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
            - x (int): abscisse
            - y (int): ordonnée

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
            - x (int): abscisse du bloque
            - y (int): ordonnée du bloque

        Returns:
            bool: le bloque appartient à une salle
        """

        last = self.get_leafSection(x, y)
        return (x, y) in last.room

    def get_leafSection(self, x: int, y: int) -> Section | None:
        """Retourne la section la plus basse de l'arbre au coordonnées (x, y).

        Args:
            - x (int): abscisse
            - y (int): ordonnée

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

    def is_hall(self, x: int, y: int) -> bool:
        """Indique si le bloque en (x, y) appartient à un couloir.

        Args:
            - x (int): abscisse du bloque
            - y (int): ordonnée du bloque

        Returns:
            bool: le bloque appartient à une salle
        """

        last = self.get_leafSection(x, y)
        for hall in last.halls_list:
            if (x, y) in hall:
                return True
        return False

    def _create_verti_halls(self, root: Section, maxLenth: int):
        """Génère des couloirs verticaux.

        Args:
            - root (Section): Section racine (l'origine)
            - maxLenth (int): longueur maximum d'un couloir
        """

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
                door1 = Door(*P1)
                door2 = Door(*P2)
                if P1.y < P2.y: # si P1 est au dessus de P2
                    newHall = Hall(
                        P1.x,
                        P1.y,
                        1,
                        P2.y - P1.y +1,
                        [door1, door2],
                        [self.room, foundSection.room]
                    )
                else: # si P1 est en dessous de P2
                    newHall = Hall(
                        P2.x,
                        P2.y,
                        1,
                        P1.y - P2.y +1,
                        [door2, door1],
                        [foundSection.room, self.room]
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
        """Génère des couloirs horizontaux.

        Args:
            - root (Section): Section racine (l'origine)
            - maxLenth (int): longueur maximum d'un couloir
        """

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
                door1 = Door(*P1)
                door2 = Door(*P2)
                if P1.x < P2.x: # si P1 est à gauche de P2
                    newHall = Hall(
                        P1.x,
                        P1.y,
                        P2.x - P1.x +1,
                        1,
                        [door1, door2],
                        [self.room, foundSection.room]
                    )
                else: # si P1 est à droite de P2
                    newHall = Hall(
                        P2.x,
                        P2.y,
                        P1.x - P2.x +1,
                        1,
                        [door2, door1],
                        [foundSection.room, self.room]
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

    def create_halls(self, root: Section, maxLenth: int):
        """Génère les couloirs.

        Args:
            - root (Section): Section racine (l'origine)
            - maxLenth (int): longueur maximum d'un couloir
        """

        if self.room != None:
            self._create_verti_halls(root, maxLenth)
            self._create_horiz_halls(root, maxLenth)
        else:
            self.leftChild.create_halls(root, maxLenth)
            self.rightChild.create_halls(root, maxLenth)

    def _create_room_walls(self):
        """Génère les murs des salles.
        """

        if self.room != None:
            doorsN = []
            doorsS = []
            doorsO = []
            doorsE = []
            for door in self.doors_list:
                if door.x == self.room.x -1:
                    doorsO += [door]
                if door.x == self.room.right +1:
                    doorsE += [door]
                if door.y == self.room.y -1:
                    doorsN += [door]
                if door.y == self.room.bottom +1:
                    doorsS += [door]

            def check_walls_verti(doors: List[Door]):
                """Sépare les murs verticaux en plusieurs parties pour ne pas couper les portes.

                Args:
                    - doors (List[Door]): liste des portes de la salle
                """

                for door in sorted(doors, key=lambda obj: obj.y): # tri les portes de haut en bas
                    wrongWall = self.walls_list[-1] # le dernier mur coupe forcément une porte
                    topWall = Wall(wrongWall.x, wrongWall.y, 1, door.y - wrongWall.y)
                    bottomWall = Wall(wrongWall.x, door.y +1, 1, wrongWall.bottom - door.y)
                    self.walls_list[-1] = topWall
                    self.walls_list += [bottomWall]

            self.walls_list += [Wall(self.room.x -1, self.room.y -2, 1, self.room.height +3)] # mur de gauche
            check_walls_verti(doorsO)
            self.walls_list += [Wall(self.room.right +1, self.room.y -2, 1, self.room.height +3)] # mur de droite
            check_walls_verti(doorsE)

            def check_walls_horiz(doors: List[Door]):
                """Sépare les murs horizontaux en plusieurs parties pour ne pas couper les portes.

                Args:
                    - doors (List[Door]): liste des portes de la salle
                """

                for door in sorted(doors, key=lambda obj: obj.x): # tri les portes de gauche à droite
                    wrongWall = self.walls_list[-1] # le dernier mur coupe forcément une porte
                    leftWall = Wall(wrongWall.x, wrongWall.y, door.x - wrongWall.x, wrongWall.height)
                    rightWall = Wall(door.x +1, wrongWall.y, wrongWall.right - door.x, wrongWall.height)
                    self.walls_list[-1] = leftWall
                    self.walls_list += [rightWall]

            self.walls_list += [Wall(self.room.x -1, self.room.y -2, self.room.width +2, 2)] # mur du haut
            check_walls_horiz(doorsN)
            self.walls_list += [Wall(self.room.x -1, self.room.bottom +1, self.room.width +2, 1)] # mur du bas
            check_walls_horiz(doorsS)

        else:
            self.leftChild._create_room_walls()
            self.rightChild._create_room_walls()

    def _create_hall_walls(self):
        """Génère les murs des couloirs.
        """

        if self.room != None:
            for hall in self.halls_list:
                if hall.width == 1: # vertical
                    leftWall = Wall(hall.x -1, hall.y, 1, hall.height)
                    rightWall = Wall(hall.x +1, hall.y, 1, hall.height)
                    self.walls_list += [leftWall, rightWall]

                else: # horizontal
                    topWall = Wall(hall.x, hall.y -2, hall.width, 2)
                    bottomWall = Wall(hall.x, hall.y +1, hall.width, 1)
                    self.walls_list += [topWall, bottomWall]

        else:
            self.leftChild._create_hall_walls()
            self.rightChild._create_hall_walls()

    def create_walls(self):
        """Génère les murs.
        """

        self._create_room_walls()
        self._create_hall_walls()

    def get_bg_block(self, *args: Point | Tuple(int, int)) -> map_bg.TextureBlock:
        """Retourne le bloque aux coordonnées (x, y).

        Args:
            - *args(Point | Tuple(int, int)): point de recherche

        Returns:
            map_bg.TextureBlock: bloque
        """

        match args:
            case int(), int():
                p = Point(*args)
            case Point():
                p = args[0]
            case _:
                raise TypeError

        last = self.get_leafSection(*p)
        if p in last.room:
            return map_bg.GROUND
        for door in last.doors_list:
            if p == door:
                return map_bg.GROUND_DOOR
        for wall in last.walls_list:
            if p in wall:
                return map_bg.RAW_WALL
        for hall in last.halls_list:
            if p in hall:
                return map_bg.GROUND_HALL
        return map_bg.VIDE

    def get_rooms(self) -> List[Room]:
        """Retourne la liste de toute les salles contenues dans la section.

        Returns:
            List[Room]: liste des salles
        """

        if self.room != None:
            return [self.room]
        return self.leftChild.get_rooms() + self.rightChild.get_rooms()

class Map:

    def __init__(self, width: int, height: int, minRoomSize: int = 6, maxRoomSize: int = 15, marge: int = 3) -> None:
        """Représente la map d'un niveau.

        Args:
            - width (int): largeur de la map
            - height (int): hauteur de la map
            - minRoomSize (int): taille (largeur ou hauteur) minimale d'une salle contenue dans une section
            - maxRoomSize (int): --------------------------- maximale -------------------------------------
            - marge (int): espace entre une salle et le bord d'une section
        """

        self.width = width
        self.height = height
        self.minRoomSize = minRoomSize
        self.maxRoomSize = maxRoomSize
        self.minSize = minRoomSize +marge*2
        self.maxSize = maxRoomSize +marge*2
        self.marge = marge
        if self.maxSize <= self.minSize or width <= self.maxSize or height <= self.maxSize:
            raise ValueError

        self._create()
        while not self._is_no_bug():
            self._create()
        self.root.create_walls()

    def _create(self):
        """Génère la map.
        """

        self.root = Section(0, 0, self.width, self.height, self.minRoomSize, self.maxRoomSize, self.marge)
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
        self.root.create_halls(self.root, 20)

    def _get_matrice(self) -> List[List[map_bg.TextureBlock]]:
        """Retourn la matrice représentant le map.

        Returns:
            List[List[map_bg.TextureBlock]]: matrice
        """

        matrice = [[...]*self.width for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                matrice[x][y] = self.root.get_bg_block(x, y)
        return matrice

    def _wall_filter(self, setup: List[List[map_bg.TextureBlock]]) -> map_bg.TextureBlock:
        """Retourne le mur correctement orienté en fonction du contexte.

        Args:
            - setup (List[List[map_bg.TextureBlock]]): contexte autour du bloque

        Returns:
            TextureBlock: bloque
        """

        id_setup = [[block.id for block in ligne] for ligne in setup]
        if setup[1][1].id != 10:
            raise ValueError

        match id_setup:
            case (_, map_bg.RAW_WALL.id, _), (_, _, _), (_, map_bg.GROUND.id, _):
                return map_bg.WALL_BASE
            case (_, map_bg.VIDE.id, _), (map_bg.RAW_WALL.id, _, map_bg.RAW_WALL.id), (_, map_bg.RAW_WALL.id, _):
                return map_bg.WALL_N
            case (_, map_bg.GROUND.id, _), (_, _, _), (_, map_bg.VIDE.id, _):
                return map_bg.WALL_S
            case (_, map_bg.RAW_WALL.id, _), (map_bg.VIDE.id, _, _), (_, map_bg.RAW_WALL.id, _):
                return map_bg.WALL_O
            case (_, map_bg.RAW_WALL.id, _), (_, _, map_bg.VIDE.id), (_, map_bg.RAW_WALL.id, _):
                return map_bg.WALL_E

            case (map_bg.VIDE.id, map_bg.VIDE.id, _), (map_bg.VIDE.id, _, _), (_, _, _):
                return map_bg.WALL_NO
            case (_, map_bg.VIDE.id, map_bg.VIDE.id), (_, _, map_bg.VIDE.id), (_, _, _):
                return map_bg.WALL_NE
            case (_, _, _), (_, _, map_bg.VIDE.id), (_, map_bg.VIDE.id, map_bg.VIDE.id):
                return map_bg.WALL_SE
            case (_, _, _), (map_bg.VIDE.id, _, _), (map_bg.VIDE.id, map_bg.VIDE.id, _):
                return map_bg.WALL_SO

            case (map_bg.VIDE.id, map_bg.RAW_WALL.id, _), (map_bg.RAW_WALL.id, _, _), (_, _, _):
                return map_bg.WALL_NO_INT
            case (_, map_bg.RAW_WALL.id, map_bg.VIDE.id), (_, _, map_bg.RAW_WALL.id), (_, _, _):
                return map_bg.WALL_NE_INT
            case (_, _, _), (_, _, map_bg.RAW_WALL.id), (_, map_bg.RAW_WALL.id, map_bg.VIDE.id):
                return map_bg.WALL_SE_INT
            case (_, _, _), (map_bg.RAW_WALL.id, _, _), (map_bg.VIDE.id, map_bg.RAW_WALL.id, _):
                return map_bg.WALL_SO_INT
            case _:
                return map_bg.RAW_WALL

    def _orientation_filter(self, matrice: List[List[map_bg.TextureBlock]]):
        """Oriente correctement les murs.

        Args:
            - matrice (List[List[map_bg.TextureBlock]]): matrice représentant la map
        """

        for x in range(1, self.width -1):
            for y in range(1, self.height -1):
                match matrice[x][y].id:
                    case 10:
                        setup = [
                            [matrice[x-1][y-1], matrice[x][y-1], matrice[x+1][y-1]],
                            [matrice[x-1][y], matrice[x][y], matrice[x+1][y]],
                            [matrice[x-1][y+1], matrice[x][y+1], matrice[x+1][y+1]]
                        ]
                        matrice[x][y] = self._wall_filter(setup)

    def get_layers(self) -> Dict[str, Image.Image]:
        """Retourne les couche d'images composant la map.

        Returns:
            Dict[str, Image.Image]: dictionnaire d'images
        """

        matrice = self._get_matrice()
        self._orientation_filter(matrice)
        result = {
            'bg': Image.new('RGBA', (16*self.width, 16*self.height), (0, 0, 0, 0))
        }

        for x in range(self.width):
            for y in range(self.height):
                x_img = 16*x
                y_img = 16*y
                block = matrice[x][y]
                result['bg'].paste(map_bg.textures[block.key], (x_img, y_img))
        return result

    def _check_link_between_rooms(self, startRoom: Room, crossedRooms: List[Room]) -> list[Room]:
        """Détermine les salles reliées à `startRoom`.

        Args:
            - startRoom (Room): salles de départ
            - crossedRooms (List[Room]): salles déjà visitées (automatiquement initialisée)

        Returns:
            list[Room]: salles trouvées
        """

        if startRoom in crossedRooms:
            return crossedRooms

        crossedRooms += [startRoom]
        otherRooms = []
        for hall in startRoom.parentSection.halls_list:
            if hall.rooms_list[0] == startRoom:
                otherRooms += [hall.rooms_list[1]]
            else:
                otherRooms += [hall.rooms_list[0]]
        for room in otherRooms:
            crossedRooms = self._check_link_between_rooms(room, crossedRooms)
        return crossedRooms

    def _is_no_bug(self) -> bool:
        """Détermine si la map s'est correctement générée.

        Returns:
            bool: la map s'est correctement générée.
        """

        rooms_list = self.root.get_rooms()
        foundedRooms = self._check_link_between_rooms(rooms_list[0], [])
        if len(rooms_list) == len(foundedRooms):
            return True
        return False
