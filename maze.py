import turtle
import random


class ParamsError(Exception):
    """will be raised if getting a unexpected parameter
    """



class MazeWanderer:
    _character = None
    _character_x = 0
    _character_y = 0
    _character_speed = 10
    _mazeDrawer = None
    _screen = None
    _maze = None
    _distance = 0
    # 移送锁
    _movement_lock = False


    def __init__(self, mazeDrawer):
        if type(mazeDrawer) == MazeDrawer:
            self._mazeDrawer = mazeDrawer
        else:
            self._mazeDrawer = MazeDrawer()
            raise ParamsError
        self._screen = self._mazeDrawer.get_screen()
        self._maze = self._mazeDrawer.get_maze()
        self._distance = self._mazeDrawer.get_distance()
        self._character_x, self._character_y = self._maze.start_point()

        self._character = turtle.Pen()
        self._character.penup()
        self._character.shape('turtle')
        self._character.shapesize(self._distance / 50, self._distance / 50)
        self._character.color('red')
        self._character_move_to(self._character_x, self._character_y)
        self._character.speed(self._character_speed)

        self._screen.onkeypress(self._on_up_pree, 'Up')
        self._screen.onkeypress(self._on_down_pree, 'Down')
        self._screen.onkeypress(self._on_left_pree, 'Left')
        self._screen.onkeypress(self._on_right_pree, 'Right')
        self._screen.listen()
    
    # relative 模式下，只考虑x、y取值-1、0、1的情况，且其中之一为0
    def _able_to_move(self, x, y, relative = False):
        if relative:
            x_new = self._character_x + x
            y_new = self._character_y + y
        else:
            x_new = x
            y_new = y
        if x_new < 0 or x_new >= self._maze.get_num_row():
            return False
        elif y_new < 0 or y_new >= self._maze.get_num_col():
            return False
        else:
            if relative:
                map_x, map_y = self._maze.room_to_map_coordinate(self._character_x, self._character_y)
                map_x = map_x + x
                map_y = map_y + y
                if self._maze.mapMatrix[map_x][map_y]:
                    return True
                else:
                    return False
            else:
                return True
    
    def _change_character_xy(self, x, y, relative = False):
        if relative:
            x = self._character_x + x
            y = self._character_y + y
        self._character_x = x
        self._character_y = y
    
    def _character_move_to(self, x, y):
        if self._able_to_move(x, y):
            self._character.goto(self._mazeDrawer.get_cell_coordinate(x, y))
            self._change_character_xy(x, y)
    
    def _on_up_pree(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(-1, 0, True):
                self._character.setheading(-90)
                self._character.forward(self._distance)
                self._change_character_xy(-1, 0, True)
            
            self._movement_lock = False
    
    def _on_down_pree(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(1, 0, True):
                self._character.setheading(90)
                self._character.forward(self._distance)
                self._change_character_xy(1, 0, True)
            
            self._movement_lock = False
    
    def _on_left_pree(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(0, -1, True):
                self._character.setheading(180)
                self._character.forward(self._distance)
                self._change_character_xy(0, -1, True)
                
            self._movement_lock = False
    
    def _on_right_pree(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(0, 1, True):
                self._character.setheading(0)
                self._character.forward(self._distance)
                self._change_character_xy(0, 1, True)
                
            self._movement_lock = False



# 使用turtle绘制迷宫
class MazeDrawer:
    _screen = None
    _screen_width = 0
    _screen_height = 0
    _pen = None
    _maze = None
    _cell_width = 20
    _outer_wall_pensize = 8
    _inner_wall_pensize = 4
    # 一个单元格到旁边单元格的距离
    _distance = 0
    # 实际的padding比这多大概12
    _padding = 10
    # 迷宫在画面上的坐标长宽
    _maze_width = 0
    _maze_height = 0
    # 当前屏幕左上角的世界坐标
    _current_ulx = 0
    _current_uly = 0


    # 不考虑使用命名参数的方式调用了，那样验证太复杂、太罗嗦了
    # 这样排列参数可以直接使用行列数调用，也可以用命名参数放入迷宫调用
    def __init__(self, num_row = 0, num_col = 0, maze = None):
        if type(maze) == Maze:
            self._maze = maze
        else:
            if num_row < 1 and num_col < 1:
                num_row = 20
                num_col = 20
            elif num_col < 1:
                num_col = num_row
            self._maze = Maze_RPA(num_row, num_col)
        self._distance = self._cell_width + self._inner_wall_pensize
        self._screen = turtle.Screen()
        # 迷宫长宽为 房间数 * 房间宽度 + 墙数 * 墙宽
        self._maze_width = self._maze.get_num_col() * self._cell_width + (self._maze.get_num_col() - 1) * self._inner_wall_pensize
        self._maze_height = self._maze.get_num_row() * self._cell_width + (self._maze.get_num_row() - 1) * self._inner_wall_pensize
        # 屏幕大小为 迷宫长宽 + 2 个外边距 + 2 个外墙宽
        self._screen_width = int(self._maze_width + 2 * self._padding + 2 * self._outer_wall_pensize)
        self._screen_height = int(self._maze_height + 2 * self._padding + 2 * self._outer_wall_pensize)
        # 左上角的世界坐标
        self._current_ulx = - self._padding - self._outer_wall_pensize
        self._current_uly = - self._padding - self._outer_wall_pensize
        # 画布大小会自动变成窗口大小减20，原因不明，而且画布左上起点会自动离窗口有一点距离，右下却没有留白
        self._screen.setup(self._screen_width + 32, self._screen_height + 32)
        self._screen.screensize(self._screen_width + 12, self._screen_height + 12)
        # 设置坐标模式为世界坐标，迷宫左上角是坐标原点，x轴向右为正，y轴向下为正
        self._screen.mode('world')
        self._screen.setworldcoordinates(self._current_ulx, self._current_uly + self._screen.screensize()[1], self._current_ulx + self._screen.screensize()[0], self._current_uly)
        self._pen = turtle.Pen()
        self._pen.hideturtle()
        self._pen.speed(0)
        self._pen.penup()

    def drawMaze(self):
        self._screen.tracer(False)
        # 若使用screenclear则之后画出的第一个图形不显示，原因不明
        self._pen.clear()
        # 刷新世界坐标
        self._screen.setworldcoordinates(self._current_ulx, self._current_uly + self._screen.screensize()[1], self._current_ulx + self._screen.screensize()[0], self._current_uly)

        # 画外边框
        self._pen.pensize(self._outer_wall_pensize)
        self._pen.goto(-self._outer_wall_pensize / 2, -self._outer_wall_pensize / 2)
        self._pen.pendown()
        self._pen.setheading(0)
        self._pen.forward(self._maze_width + self._outer_wall_pensize)
        self._pen.setheading(90)
        self._pen.forward(self._maze_height + self._outer_wall_pensize)
        self._pen.setheading(180)
        self._pen.forward(self._maze_width + self._outer_wall_pensize)
        self._pen.setheading(270)
        self._pen.forward(self._maze_height + self._outer_wall_pensize)
        self._pen.penup()
        # 画内墙
        self._pen.pensize(self._inner_wall_pensize)
        # 纵向
        self._pen.goto(self._cell_width + self._inner_wall_pensize / 2, -self._inner_wall_pensize / 2)
        self._pen.setheading(90)
        for i in range(self._maze.get_num_col() - 1):
            for j in range(self._maze.get_num_row()):
                wall_flag = not self._maze.mapMatrix[2 * j][2 * i + 1]
                if wall_flag:
                    self._pen.pendown()
                self._pen.forward(self._distance)
                if wall_flag:
                    self._pen.penup()
            self._pen.goto(self._pen.xcor() + self._distance, -self._inner_wall_pensize / 2)
        # 横向
        self._pen.goto(-self._inner_wall_pensize / 2, self._cell_width + self._inner_wall_pensize / 2)
        self._pen.setheading(0)
        for i in range(self._maze.get_num_row() - 1):
            for j in range(self._maze.get_num_col()):
                wall_flag = not self._maze.mapMatrix[2 * i + 1][2 * j]
                if wall_flag:
                    self._pen.pendown()
                self._pen.forward(self._distance)
                if wall_flag:
                    self._pen.penup()
            self._pen.goto(-self._inner_wall_pensize / 2, self._pen.ycor() + self._distance)
        # 画起点、终点
        self._pen.goto(self.get_cell_coordinate(self._maze.start_point()))
        self._pen.dot(self._cell_width / 2, 'green')
        self._pen.goto(self.get_cell_coordinate(self._maze.goal_point()))
        self._pen.dot(self._cell_width / 2, 'blue')
        
        # self._screen.update()
        self._screen.tracer(True)

    # 暂不验证，让他报该报的错
    def get_cell_coordinate(self, x, y = None):
        if y == None:
            y = x[1]
            x = x[0]
        return (self._cell_width / 2 + y * self._distance, self._cell_width / 2 + x * self._distance)
    
    def get_screen(self):
        return self._screen
    
    def get_maze(self):
        return self._maze
    
    def get_distance(self):
        return self._distance



# 迷宫 类
class Maze:
    _num_row = 0
    _num_col = 0
    # 起点、终点 均为房间坐标
    _start_point = (0, 0)
    _goal_point = (0, 0)
    # True 此空间没有障碍 False 此空间有障碍
    mapMatrix = []


    def __init__(self, num_row, num_col = 0, start_point = None, goal_point = None):
        self._num_row = num_row
        if num_col <= 0:
            num_col = num_row
        self._num_col = num_col
        if start_point == None or not self._is_valid_coordinate(start_point):
            # 默认迷宫入口在左上角
            self._start_point = (0, 0)
        else:
            self._start_point = start_point
        if goal_point == None or not self._is_valid_coordinate(goal_point):
            # 默认迷宫出口在右下角
            self._goal_point = (num_row - 1, num_col - 1)
        else:
            self._goal_point = goal_point
        self.createInitialMaze()
        self.createMaze()

    # 生成初始地图矩阵
    def createInitialMaze(self):
        self.mapMatrix = []
        for i in range(self._num_row * 2 - 1):
            self.mapMatrix.append([])
            for j in range(self._num_col * 2 - 1):
                if i % 2 == 0 and j % 2 == 0:
                    self.mapMatrix[i].append(True)
                else:
                    self.mapMatrix[i].append(False)
    
    # 写一个空函数，假装虚函数
    def createMaze(self):
        pass
    
    # 验证是否为合法坐标
    def _is_valid_coordinate(self, point, in_map = False):
        if type(point) != tuple:
            return False
        if len(point) != 2:
            return False
        if type(point[0]) != int or type(point[1]) != int:
            return False
        if in_map:
            # 在整个矩阵中
            if point[0] >= self._num_row * 2 or point[1] >= self._num_col * 2:
                return False
        else:
            # 不考虑墙
            if point[0] >= self._num_row or point[1] >= self._num_col:
                return False
        return True

    # 房间坐标转换为全矩阵坐标
    def room_to_map_coordinate(self, *var_point):
        point = None
        if len(var_point) == 1 and self._is_valid_coordinate(var_point[0]):
            point = var_point[0]
        elif len(var_point) == 2 and self._is_valid_coordinate((var_point[0], var_point[1])):
            point = (var_point[0], var_point[1])
        return (point[0] * 2, point[1] * 2)
    
    # 全矩阵坐标转换为房间坐标
    def map_to_room_coordinate(self, *var_point):
        point = None
        if len(var_point) == 1 and self._is_valid_coordinate(var_point[0], True):
            point = var_point[0]
        elif len(var_point) == 2 and self._is_valid_coordinate((var_point[0], var_point[1]), True):
            point = (var_point[0], var_point[1])
        return (point[0] / 2, point[1] / 2)
    
    def get_num_row(self):
        return self._num_row
    
    def get_num_col(self):
        return self._num_col

    # 设置/获取起点
    def start_point(self, start_point = None):
        if start_point == None:
            return self._start_point
        if self._is_valid_coordinate(start_point):
            self._start_point = start_point
            return True
        else:
            return False

    def goal_point(self, goal_point = None):
        if goal_point == None:
            return self._goal_point
        if self._is_valid_coordinate(goal_point):
            self._goal_point = goal_point
            return True
        else:
            return False

    # 以控制台输出方式，展示地图矩阵效果
    def showMazeAsMatrix(self):
        for row_number, row in enumerate(self.mapMatrix):
            for col_number, cell in enumerate(row):
                if self._start_point == self.map_to_room_coordinate(row_number, col_number):
                    print('S', end = ' ')
                elif self._goal_point == self.map_to_room_coordinate(row_number, col_number):
                    print('G', end = ' ')
                elif cell:
                    print(' ', end = ' ')
                else:
                    print('*', end = ' ')
            print()



'''
Randomized Prim's algorithm
随机Prim算法
1. 初始化，建立所有单元格都被墙隔开的迷宫
使用集合表示路径，集合中的元素就是单元格的编号
一开始每个单元格都是一个单独的路径
2. 随机选择一个内部的墙壁
如果墙壁两边的单元格都属于同一个路径集合，则没必要打通这面墙
如果两边的单元格属于不同的路径集合，则打通墙壁，使两侧连通，对应的集合合并
重复这一步骤
直到最终合并为一个集合，或入口和出口属于同一个集合，即入口到出口有可达路径
（可以使用并查集优化速度）
'''
class Maze_RPA(Maze):
    _node_parent = []
    _node_rank = []
    _edges = []


    # 在基类中加入了createMaze这个空函数之后，不再需要
    # def __init__(self, num_row, num_col = 0, start_point = None, goal_point = None):
    #     Maze.__init__(self, num_row, num_col, start_point, goal_point)
    #     self.createMaze()

    def createInitialMaze(self):
        self.mapMatrix = []
        for i in range(self._num_row * 2 - 1):
            self.mapMatrix.append([])
            for j in range(self._num_col * 2 - 1):
                if i % 2 == 0 and j % 2 == 0:
                    self.mapMatrix[i].append(True)
                    self._node_parent.append(-1)
                    self._node_rank.append(0)
                # 阻断上下的横向墙壁
                elif i % 2 == 0:
                    self.mapMatrix[i].append(False)
                    self._edges.append((self.point_to_num(i / 2, (j - 1) / 2), self.point_to_num(i / 2, (j + 1) / 2)))
                # 阻断左右的纵向墙壁
                elif j % 2 == 0:
                    self.mapMatrix[i].append(False)
                    self._edges.append((self.point_to_num((i - 1) / 2, j / 2), self.point_to_num((i + 1) / 2, j / 2)))
                else:
                    self.mapMatrix[i].append(False)
        print('Maze initializing done!')
    
    # 将房间的坐标点转换为单个数字的房间号，每行的房间号是连续的
    def point_to_num(self, row_num, col_num):
        return int(row_num * self._num_col + col_num)
    
    def num_to_point(self, num):
        return (int(num / self._num_col), num % self._num_col)

    def createMaze(self):
        i = self._num_row * self._num_col - 1
        while i > 0:
            # 没合并成功就继续合并，合并成功了，开始下一次合并
            flag_union_successfully = False
            while not flag_union_successfully:
                edge = self._edges[random.randint(0, len(self._edges) - 1)]
                flag_union_successfully = self._union_vertices(edge[0], edge[1])
                if flag_union_successfully:
                    point_a = self.num_to_point(edge[0])
                    point_a = (point_a[0] * 2, point_a[1] * 2)
                    point_b = self.num_to_point(edge[1])
                    point_b = (point_b[0] * 2, point_b[1] * 2)
                    point_wall = (int((point_a[0] + point_b[0]) / 2), int((point_a[1] + point_b[1]) / 2))
                    self.mapMatrix[point_wall[0]][point_wall[1]] = True
                self._edges.remove(edge)
            i = i - 1
        print('Maze creating with RPA done!')
    
    def _find_root(self, room_num):
        root = room_num
        while self._node_parent[root] != -1:
            root = self._node_parent[root]
        return root

    def _union_vertices(self, x, y):
        root_x = self._find_root(x)
        root_y = self._find_root(y)
        if root_x == root_y:
            return False
        elif self._node_rank[root_x] > self._node_rank[root_y]:
            self._node_parent[root_y] = root_x
        elif self._node_rank[root_x] < self._node_rank[root_y]:
            self._node_parent[root_x] = root_y
        else:
            self._node_parent[root_y] = root_x
            self._node_rank[root_x] += 1
        return True



if __name__ == '__main__':
    maze_drawer = MazeDrawer(30, 50)
    # maze_drawer._maze.showMazeAsMatrix()
    maze_wanderer = MazeWanderer(maze_drawer)
    maze_drawer.drawMaze()
    turtle.mainloop()