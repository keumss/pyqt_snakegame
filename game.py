import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor, QBrush, QPalette, QPixmap
from PyQt5.QtCore import Qt, QTimer

SPEED = 50 # 50:easy, 40:normal, 30:hard
SPD_LIST = [50, 40, 30]
SPD_INFO = ['easy', 'normal', 'hard']

BOARD_W = 400
BOARD_H = 400
UNIT_CELL_LEN = 20
BOARD_WCNT = BOARD_W / UNIT_CELL_LEN
BOARD_HCNT = BOARD_H / UNIT_CELL_LEN

dir_keys = [Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left]
dx = [0, 1, 0, -1]
dy = [-1, 0, 1, 0]

THEME = 0
THEME_LIST = [
    {'head':QColor(Qt.black), 'body':QColor(Qt.darkGreen),
     'apple':QColor(Qt.red), 'background':QColor('#e7e7e7'),
     'score':'black'},

    {'head':QColor('#1aa804'), 'body':QColor('#ff8000'),
    'apple':QColor('#ff82f9'), 'background':QColor('#a6e8ff'),
     'score':'blue'},

    {'head':QColor(Qt.yellow), 'body':QColor(Qt.darkGreen),
    'apple':QColor(Qt.red), 'background':QColor('#34009e'),
     'score':'white'},
]

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
        #self.resize(BOARD_W, BOARD_H)
        self.initGame()
        self.newGame()

    def initGame(self):
        self.setBackgroundColor(THEME_LIST[THEME]['background'])

        self.lbl_score = QLabel(self)
        self.lbl_score.setStyleSheet('color: ' + THEME_LIST[THEME]['score'])
        self.lbl_score.move(BOARD_W - 100, 0)
        self.lbl_score.resize(100, 30)
        font = self.lbl_score.font()
        font.setFamily('Times New Roman')
        font.setPointSize(15)
        self.lbl_score.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mainLoop)

    def setBackgroundColor(self, color):
        pal = QPalette()
        pal.setColor(QPalette.Window, color)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

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
        # draw apple
        qp.setPen(Qt.NoPen)
        qp.setBrush(THEME_LIST[THEME]['apple'])
        qp.drawRect(self.apple[0] * UNIT_CELL_LEN, self.apple[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

        # draw snake body
        body = self.snake.body[1:]
        qp.setBrush(THEME_LIST[THEME]['body'])
        for cell in body:
            qp.drawRect(cell[0] * UNIT_CELL_LEN, cell[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

        # draw snake head
        head = self.snake.body[0]
        qp.setBrush(THEME_LIST[THEME]['head'])
        qp.drawRect(head[0] * UNIT_CELL_LEN, head[1] * UNIT_CELL_LEN, UNIT_CELL_LEN, UNIT_CELL_LEN)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initMenu()
        self.gb = GameBoard()
        self.setCentralWidget(self.gb)

        self.setWindowTitle('Snake Game')
        self.setFixedSize(BOARD_W, BOARD_H + self.menubar.height())     #self.resize(BOARD_W, BOARD_H)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initMenu(self):
        action_setting = QAction(QIcon('image/setting.PNG'), 'Setting', self)
        action_setting.setShortcut('Ctrl+O')
        action_setting.triggered.connect(self.slot_setting)

        action_quit = QAction(QIcon('image/exit.png'), 'Quit', self)
        action_quit.setShortcut('Ctrl+Q')
        action_quit.triggered.connect(self.close)

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)
        self.menubar.setFixedHeight(30)
        filemenu = self.menubar.addMenu('File')
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

    def slot_setting(self):
        global SPEED, THEME
        #print('setting!')
        opt = SettingWindow()
        opt.exec_()

        if opt.speed != None and opt.theme != None:
            SPEED = opt.speed
            THEME = opt.theme
            self.gb.setBackgroundColor(THEME_LIST[THEME]['background'])
            self.gb.lbl_score.setStyleSheet('color: ' + THEME_LIST[THEME]['score'])
            print('new SPEED: %d, THEME: %d' % (SPEED, THEME))

class SettingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.speed = None
        self.theme = None

    def initUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.createModeGroup())
        vbox.addWidget(self.createThemeGroup())
        vbox.addLayout(self.createButtons())
        self.setLayout(vbox)

        self.setWindowTitle('Setting')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def createModeGroup(self):
        self.mode_rbtns = []
        for i in range(0, len(SPD_LIST)):
            self.mode_rbtns.append(QRadioButton(SPD_INFO[i], self))
        self.mode_rbtns[SPD_LIST.index(SPEED)].setChecked(True)

        hbox = QHBoxLayout()
        for i in range(0, len(SPD_LIST)):
            hbox.addWidget(self.mode_rbtns[i])

        groupbox = QGroupBox('Select mode', self)
        groupbox.setLayout(hbox)
        return groupbox

    def createThemeGroup(self):
        self.theme_rbtns = []
        for i in range(0, len(THEME_LIST)):
            self.theme_rbtns.append(QRadioButton('theme'+str(i+1), self))
        self.theme_rbtns[THEME].setChecked((True))

        grid = QGridLayout()
        for i in range(0, len(THEME_LIST)):
            grid.addWidget(self.theme_rbtns[i], 0, i)
            grid.addWidget(self.createThemeSample(i), 1, i)

        groupbox = QGroupBox('Select theme', self)
        groupbox.setLayout(grid)
        return groupbox

    def createThemeSample(self, theme):
        len = int(UNIT_CELL_LEN / 2)
        pixmap = QPixmap(UNIT_CELL_LEN * 2, UNIT_CELL_LEN * 2)
        pixmap.fill(THEME_LIST[theme]['background'])

        qp = QPainter()
        qp.begin(pixmap)
        qp.setPen(Qt.NoPen)
        qp.setBrush(THEME_LIST[theme]['head'])
        qp.drawRect(len*2, len*1, len, len)
        qp.setBrush(THEME_LIST[theme]['body'])
        qp.drawRect(0, 0, len*3, len)
        qp.drawRect(0, 0, len, len*4)
        qp.setBrush(THEME_LIST[theme]['apple'])
        qp.drawRect(len*3, len*3, len, len)
        qp.end()

        lbl = QLabel()
        lbl.setPixmap(pixmap)
        return lbl

    def createButtons(self):
        btn_save = QPushButton('Save', self)
        btn_save.clicked.connect(self.slot_save)
        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.clicked.connect(self.close)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        return hbox

    def slot_save(self):
        for i in range(0, len(SPD_LIST)):
            if self.mode_rbtns[i].isChecked():
                self.speed = SPD_LIST[i]
                break
        for i in range(0, len(THEME_LIST)):
            if self.theme_rbtns[i].isChecked():
                self.theme = i
                break
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GameWindow()
    ex.show()
    sys.exit(app.exec_())
