import turtle
import random

class ParamsError(Exception):
    ''' will be raised if getting an unexpected parameter
    '''

'''
因为康威生命游戏，存储结构与逻辑联系紧密，
没有采用MVC的三层模式，而是使用了两层。
'''
class conway_life_game:
    map_matrix = []
    width = 0
    height = 0

    def __init__(self, width, height = 0):
        self.width = width
        if height == 0:
            self.height = width
        elif height > 0:
            self.height = height
        else:
            raise(ParamsError)
        for i in range(self.height):
            self.map_matrix.append([])
            for j in range(self.width):
                self.map_matrix[i].append(False)
    
    def evolve(self):
        new_map = []

        for y in range(self.height):
            new_map.append([])
            for x in range(self.width):
                num_surrounding_creatures = self.__num_surrounding_creatures(x, y)
                if self.map_matrix[y][x]:
                    if num_surrounding_creatures < 2 or num_surrounding_creatures > 3:
                        new_map[y].append(False)
                    else:
                        new_map[y].append(True)
                else:
                    if num_surrounding_creatures == 3:
                        new_map[y].append(True)
                    else:
                        new_map[y].append(False)
        self.map_matrix = new_map

    def __num_surrounding_creatures(self, x, y):
        num = 0
        i = -1
        while i < 2:
            j = -1
            while j < 2:
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and not (i == 0 and j == 0):
                    if self.map_matrix[y + j][x + i]:
                        num = num + 1
                j = j + 1
            i = i + 1
        return num
    
    def simple_illustrate(self):
        for j in range(self.height):
            for i in range(self.width):
                if self.map_matrix[j][i]:
                    print('*', end = '')
                else:
                    print(' ', end = '')
            print('|')
        print('_' * self.width)

if __name__ == '__main__':
    clg = conway_life_game(10)

    clg.map_matrix[5][5] = True
    clg.simple_illustrate()
    clg.evolve()
    clg.simple_illustrate()