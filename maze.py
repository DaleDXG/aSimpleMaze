import turtle
import random


class ParamsError(Exception):
    """will be raised if getting a unexpected parameter
    """



# 在迷宫中移动的角色，实际上是一个画笔
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


    def __init__(self, mazeDrawer, up_keycode = 'Up', down_keycode = 'Down', left_keycode = 'Left', right_keycode = 'Right', color = 'red', shape = 'turtle'):
        if type(mazeDrawer) == MazeDrawer:
            self._mazeDrawer = mazeDrawer
        else:
            # self._mazeDrawer = MazeDrawer()
            raise ParamsError
        self._screen = self._mazeDrawer.get_screen()
        self._maze = self._mazeDrawer.get_maze()
        self._distance = self._mazeDrawer.get_distance()
        self._character_x, self._character_y = self._maze.start_point()

        self._character = turtle.Pen()
        self._character.penup()
        self._character.shape(shape)
        self._character.shapesize(self._distance / 50, self._distance / 50)
        self._character.color(color)
        self._character_move_to(self._character_x, self._character_y)
        self._character.speed(self._character_speed)

        self._screen.onkeypress(self._on_up_press, up_keycode)
        self._screen.onkeypress(self._on_down_press, down_keycode)
        self._screen.onkeypress(self._on_left_press, left_keycode)
        self._screen.onkeypress(self._on_right_press, right_keycode)
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
    
    def _on_up_press(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(-1, 0, True):
                self._character.setheading(-90)
                self._character.forward(self._distance)
                self._change_character_xy(-1, 0, True)
            
            self._movement_lock = False
    
    def _on_down_press(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(1, 0, True):
                self._character.setheading(90)
                self._character.forward(self._distance)
                self._change_character_xy(1, 0, True)
            
            self._movement_lock = False
    
    def _on_left_press(self):
        if not self._movement_lock:
            self._movement_lock = True

            if self._able_to_move(0, -1, True):
                self._character.setheading(180)
                self._character.forward(self._distance)
                self._change_character_xy(0, -1, True)
                
            self._movement_lock = False
    
    def _on_right_press(self):
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
    
    # 将房间的坐标点转换为单个数字的房间号，每行的房间号是连续的
    def point_to_num(self, row_num, col_num):
        return int(row_num * self._num_col + col_num)
    
    def num_to_point(self, num):
        return (int(num / self._num_col), num % self._num_col)
    
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



"""
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

可使用并查集优化速度
可以通过拿掉特定的一些边，改变迷宫的形状、轮廓

适合生成复杂的标准迷宫
"""
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
        self._node_parent = []
        self._node_rank = []
        self._edges = []
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

    def createMaze(self):
        i = self._num_row * self._num_col - 1
        while i > 0:
            # 没合并成功就继续合并，合并成功了，开始下一次合并
            flag_union_successfully = False
            while not flag_union_successfully:
                random_edge_num = random.randint(0, len(self._edges) - 1)
                edge = self._edges[random_edge_num]
                flag_union_successfully = self._union_vertices(edge[0], edge[1])
                if flag_union_successfully:
                    point_a = self.num_to_point(edge[0])
                    point_a = (point_a[0] * 2, point_a[1] * 2)
                    point_b = self.num_to_point(edge[1])
                    point_b = (point_b[0] * 2, point_b[1] * 2)
                    point_wall = (int((point_a[0] + point_b[0]) / 2), int((point_a[1] + point_b[1]) / 2))
                    self.mapMatrix[point_wall[0]][point_wall[1]] = True
                # pop 用索引号而 remove 用值删除元素，可能pop要更快？
                # self._edges.remove(edge)
                self._edges.pop(random_edge_num)
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



"""
Recursive backtracker
递归回溯
1.初始化，建立所有单元格都被墙可开的迷宫，选择一个起始点
2.从当前单元格的没有到达过的邻居中，随机选择一个，打通墙壁
重复这个步骤
3.若当前单元格的邻居都已经到达过
则退回上一个有未到达邻居的单元格
或者 退回随机的有未到达邻居的单元格
4.结束，没有可退回的单元格

记忆中，递归问题最好转化为用堆栈解决，递归比较吃资源，并且层数有限制
可增加一个标记单元格有没有被访问过的列表优化，这样堆栈中可以只保存有未访问邻居的单元格，而不用保存所有访问过的单元格
可以产生广钻和深钻两种形式，描述中的直到没有未访问邻居是深钻形式，还可以每次破墙都从访问过的里面随机选一个，形成广钻
深钻又能产生两种形式，退回上一个有未到达邻居的单元格相对形成的树更深，而退回随机有未到达邻居的单元格相对较浅
可以结合上面的三种形式产生变种，比如设置从一个单元格开始，最多钻一定步数，然后从栈中随机选取一个重复步骤
这种方法对每个方向的概率还可以进行调整，比如使向终点方向破墙的概率变大，降低迷宫难度
其他的变种还可以有，预设已访问列表，让它不是全False的矩阵，其中有True，这样可以让迷宫产生特定的形状

适合生成主线支线明显的迷宫
"""
class Maze_RB(Maze):
    _stack = []
    _visited = []

    # 现在想想，初始化和实际的生成迷宫过程分开两部分，可能没有什么道理，这两个过程分别使用都是没有意义的
    def createInitialMaze(self):
        self.mapMatrix = []
        self._visited = []
        for i in range(self._num_row * 2 - 1):
            self.mapMatrix.append([])
            for j in range(self._num_col * 2 - 1):
                if i % 2 == 0 and j % 2 == 0:
                    self.mapMatrix[i].append(True)
                    self._visited.append(False)
                else:
                    self.mapMatrix[i].append(False)
    
    # 用depth参数表示大概率会形成多深程度的树，0表示最浅，1表示一般深，2表示最深
    def createMaze(self, depth = 2):
        self._stack = [self._start_point]

        if depth == 0:
            while len(self._stack) == 0:
                current_stack_num = random.randint(0, len(self._stack) - 1)
                current_room = self._stack[current_stack_num]
                # current_room_x = current_room[0]
                # current_room_y = current_room[1]
                self._visited[self.point_to_num(current_room)] = True
                
                if len(possible_direction) > 0:
                    pass
                else:
                    self._stack.pop(current_stack_num)
        elif depth == 1:
            pass
        else:
            pass
        
    def _get_unvisited_directions(self, current_room_x, current_room_y = None):
        # 加了下划线，内部使用的函数，不做复杂验证了
        if type(current_room_x) == tuple:
            current_room_x, current_room_y = current_room_x
        # 分别对应上下左右
        unvisited_direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # 首先pop效率比remove高，所以比起for循环遍历更想用while + 索引号遍历，但pop之后索引号会发生变化，所以从后向前反着遍历
        i = 3
        while i >= 0:
            dir_x = current_room_x + unvisited_direction[i][0]
            dir_y = current_room_y + unvisited_direction[i][1]
            # 如果单元格在边界上会少方向，然后检查这个方向有没有被访问过
            if dir_x <= 0 or dir_x >= self._num_row - 1 or dir_y <= 0 or dir_y >= self._num_col - 1 or self._visited[self.point_to_num(dir_x, dir_y)]:
                unvisited_direction.pop(i)
            i -= 1
        return unvisited_direction



"""
Recursive division
递归分割
属于构造墙壁的迷宫生成算法
1.初始化，生成全空无墙迷宫
2.在空白空间随机生成十字墙壁，将空间分割为4个子空间
在其中3面墙壁上各自选择一个随机位置挖洞，确保4个子空间的连通性
对子空间重复这一步骤
3.结束，子空间不能继续分割

适合生成转角较少的迷宫
"""
class Maze_RD(Maze):
    _stack = []



# 扫雷游戏
class Minesweeper:
    mapMatrix = []
    mapShadow = []
    _num_row = 0
    _num_col = 0


    def __init__(self, num_row = 10, num_col = 0):
        pass



# 用turtle库做的计时器工具，越看文档越觉得能写出turtle库的人真的挺厉害的
class Timer:
    _timer = 0
    _t = 0


    # 参数 t 表示每多少毫秒计一次
    def __init__(self, t = 100):
        self._t = t
        turtle.ontimer(self._ontimer, t)
        turtle.listen()
    
    def _ontimer(self):
        self._timer += 1
    
    def check_timer(self):
        return self._timer
    
    def check_timer_secs(self):
        return self._timer * self._t / 1000



class FileHelper:
    _file_name = ''
    _file = None


    def __init__(self, file_name):
        if type(file_name) == str:
            self._file_name = file_name
        else:
            raise ParamsError
        self._file = open(file_name, 'at+')
    
    def __def__(self):
        self._file.write('\n')
        self._file.close()
    
    def add_line(self, content):
        if type(content) == str:
            self._file.write(content + '\n')
        else:
            raise ParamsError



# turtle库的Screen.mainloop()实际上又调用了tkinter.mainloop()
# 真的是层层套娃
mainloop = turtle.mainloop



if __name__ == '__main__':
    maze_drawer = MazeDrawer(30, 50)
    maze_wanderer = MazeWanderer(maze_drawer)
    maze_drawer.drawMaze()
    mainloop()