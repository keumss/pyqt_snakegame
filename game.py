import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer

SPEED = 50
INIT_BODY_LEN = 2

BOARD_W = 300
BOARD_H = 300
UNIT_LEN = 10
BOARD_WCNT = BOARD_W / UNIT_LEN
BOARD_HCNT = BOARD_H / UNIT_LEN

dir_keys = [Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left]
dx = [0, 1, 0, -1]
dy = [-1, 0, 1, 0]

class Snake:
    def __init__(self):
        if INIT_BODY_LEN in range(1, 5):
            self.body = []
            for i in range(0, INIT_BODY_LEN):
                self.body.append((10-i, 10))
        else:
            self.body = [(10, 10), (9, 10)]
        self.dir = 1
        self.ndir = 1

    def nextHead(self):
        head = self.body[0]
        return (head[0] + dx[self.dir], head[1] + dy[self.dir])

    def moveHead(self, nh):
        self.body.insert(0, nh)

    def cutTail(self):
        self.body.pop()

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snake Game')
        self.resize(BOARD_W, BOARD_H)
        self.center()
        self.initMenu()
        self.initGame()

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
        print(menubar.width())
        print(menubar.height())

        filemenu.addAction(action_rank)
        filemenu.addAction(action_setting)
        filemenu.addAction(action_quit)

    def initGame(self):
        self.statusBar().showMessage('press direction key to start')
        self.gameState = 'stop'
        self.snake = Snake()
        self.apple = self.createApple()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mainLoop)
        self.update()

    def createApple(self):
        while True:
            apple = (random.randint(5, BOARD_WCNT), random.randint(5, BOARD_HCNT))
            if apple not in self.snake.body:
                return apple

    def startGame(self):
        self.statusBar().showMessage('')
        self.gameState = 'playing'
        self.timer.start(SPEED)

    def stopGame(self):
        self.gameState = 'stop'
        self.timer.stop()

    def mainLoop(self):
        #print('mainLoop..')
        self.snake.dir = self.snake.ndir
        nh = self.snake.nextHead()

        if nh in self.snake.body or \
            nh[0] < 0 or nh[1] < 0:
            self.stopGame()
            self.statusBar().showMessage('game over')
            QMessageBox.about(self, 'Game over', 'Score : %d' % (len(self.snake.body) - INIT_BODY_LEN) )
            self.initGame()
            return
        elif nh == self.apple:
            self.snake.moveHead(nh)
            self.apple = self.createApple()
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

        # draw apple
        qp.setBrush(QColor(Qt.red))
        qp.drawRect(self.apple[0] * UNIT_LEN, self.apple[1] * UNIT_LEN, UNIT_LEN, UNIT_LEN)

        # draw snake
        body = self.snake.body[1:]
        qp.setBrush(QColor(40, 150, 20))
        qp.setPen(QPen(QColor(Qt.black), 2))
        for cell in body:
            qp.drawRect(cell[0] * UNIT_LEN, cell[1] * UNIT_LEN, UNIT_LEN, UNIT_LEN)

        head = self.snake.body[0]
        qp.setBrush(QColor(Qt.black))
        qp.drawRect(head[0] * UNIT_LEN, head[1] * UNIT_LEN, UNIT_LEN, UNIT_LEN)

    def keyPressEvent(self, e):
        if e.key() in dir_keys:
            if self.gameState == 'stop':
                sd = dir_keys.index(e.key())
                if (sd+2) % 4 != self.snake.dir:
                    print('start game')
                    self.snake.ndir = sd
                    self.startGame()
            elif self.gameState == 'playing':
                nd = dir_keys.index(e.key())
                if (nd % 2 == 0) ^ (self.snake.dir % 2 == 0):
                    self.snake.ndir = nd

        elif e.key() == Qt.Key_Escape:
            if self.gameState == 'playing':
                self.stopGame()
                self.statusBar().showMessage('pause')

    def slot_rank(self):
        print("rank!")
        QMessageBox().about(self, 'rank', 'to be implemented')

    def slot_setting(self):
        print("setting!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GameWindow()
    w.show()
    sys.exit(app.exec_())
