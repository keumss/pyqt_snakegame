import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer

SPEED = 50  # 50:easy, 40:normal, 30:hard
BOARD_W = 400
BOARD_H = 400
UNIT_CELL_LEN = 20
BOARD_WCNT = BOARD_W / UNIT_CELL_LEN
BOARD_HCNT = BOARD_H / UNIT_CELL_LEN

dir_keys = [Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left]
dx = [0, 1, 0, -1]
dy = [-1, 0, 1, 0]

class Snake:
    def __init__(self):
        self.body = [(5, 5), (4, 5)]
        self.dir = 1
        self.ndir = 1

    def nextHead(self):
        head = self.body[0]
        return (head[0] + dx[self.dir], head[1] + dy[self.dir])

    def moveHead(self, nh):
        self.body.insert(0, nh)

    def cutTail(self):
        self.body.pop()

class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.color_head = QColor(Qt.black)
        self.color_body = QColor("#088c06")
        self.color_apple = QColor(Qt.red)
        self.color_background = QColor("#e7e7e7")
        self.resize(BOARD_W, BOARD_H)
        self.initGame()
        self.newGame()

    def initGame(self):
        self.lbl_score = QLabel(self)
        self.lbl_score.move(BOARD_W - 100, 0)
        self.lbl_score.resize(100, 30)
        font = self.lbl_score.font()
        font.setFamily('Times New Roman')
        font.setPointSize(15)
        self.lbl_score.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mainLoop)

    def newGame(self):
        self.gameState = 'stop'
        self.snake = Snake()
        self.apple = self.createApple()
        self.score = 0
        self.lbl_score.setText('score : %d' % 0)
        self.update()

    def createApple(self):
        while True:
            apple = (random.randint(0, BOARD_WCNT - 1), random.randint(0, BOARD_HCNT - 1))
            if apple not in self.snake.body:
                return apple

    def startGame(self):
        self.gameState = 'playing'
        self.timer.start(SPEED)

    def stopGame(self):
        self.gameState = 'stop'
        self.timer.stop()

    def mainLoop(self):
        self.snake.dir = self.snake.ndir
        nh = self.snake.nextHead()

        if nh in self.snake.body or \
            nh[0] < 0 or nh[0] >= BOARD_WCNT or nh[1] < 0 or nh[1] >= BOARD_HCNT:
            self.snake.moveHead(nh)
            self.snake.cutTail()
            self.update()
            self.stopGame()
            QMessageBox.about(self, 'Game over', 'Game over!')
            self.newGame()
            return
        elif nh == self.apple:
            self.snake.moveHead(nh)
            self.apple = self.createApple()
            self.score += 1
            self.lbl_score.setText('score : %d' % self.score)
        else:
            self.snake.moveHead(nh)
            self.snake.cutTail()
        self.update()

    def paintEvent(self, e):
        #print('paintEvent!')
        qp = QPainter()
        qp.begin(self)
        self.drawGame(qp)
        qp.end()

    def drawGame(self, qp):
        # draw boundary
        qp.fillRect(0, 0, BOARD_W, BOARD_H, self.color_background)

        # draw apple
        qp.setPen(Qt.NoPen)
        qp.setBrush(self.color_apple)
        qp.drawRect(self.apple[0] * UNIT_CELL_LEN, self.apple[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

        # draw snake body
        body = self.snake.body[1:]
        qp.setBrush(self.color_body)
        for cell in body:
            qp.drawRect(cell[0] * UNIT_CELL_LEN, cell[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

        # draw snake head
        head = self.snake.body[0]
        qp.setBrush(self.color_head)
        qp.drawRect(head[0] * UNIT_CELL_LEN, head[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snake Game')
        self.setFixedSize(BOARD_W, BOARD_H + UNIT_CELL_LEN)     #self.resize(BOARD_W, BOARD_H)
        self.center()
        self.initMenu()
        self.gb = GameBoard()
        self.setCentralWidget(self.gb)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initMenu(self):
        action_rank = QAction(QIcon('image/crown.PNG'), 'Rank', self)
        action_rank.setShortcut('Ctrl+R')
        action_rank.triggered.connect(self.slot_rank)

        action_setting = QAction(QIcon('image/setting.PNG'), 'Setting', self)
        action_setting.setShortcut('Ctrl+O')
        action_setting.triggered.connect(self.slot_setting)

        action_quit = QAction(QIcon('image/exit.png'), 'Quit', self)
        action_quit.setShortcut('Ctrl+Q')
        action_quit.triggered.connect(self.close)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('File')
        filemenu.addAction(action_rank)
        filemenu.addAction(action_setting)
        filemenu.addAction(action_quit)

    def keyPressEvent(self, e):
        if e.key() in dir_keys:
            if self.gb.gameState == 'stop':
                sd = dir_keys.index(e.key())
                if (sd + 2) % 4 != self.gb.snake.dir:
                    self.gb.snake.ndir = sd
                    self.gb.startGame()

            elif self.gb.gameState == 'playing':
                nd = dir_keys.index(e.key())
                if (nd % 2 == 0) ^ (self.gb.snake.dir % 2 == 0):
                    self.gb.snake.ndir = nd

    def slot_rank(self):
        print("rank!")
        QMessageBox().about(self, 'rank', 'to be implemented')

    def slot_setting(self):
        print("setting!")
        QMessageBox().about(self, 'rank', 'to be implemented')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GameWindow()
    ex.show()
    sys.exit(app.exec_())
