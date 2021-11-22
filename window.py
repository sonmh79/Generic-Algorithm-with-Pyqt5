import sys
import os
import time
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from ga import VRP

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("ga.ui")[0]
## python실행파일 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(BASE_DIR + r'/ga.ui')[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.distanceFile = None
        self.demandFile = None
        self.df_dist = None
        self.df_demand = None


        # SET DEFAULT VARIABLES
        self.capa, self.chromo, self.mp, self.el, self.robots = 3, 100 , 0.2, 200, 3
        self.input_capa.setText(str(self.capa))
        self.input_chromo.setText(str(self.chromo))
        self.input_mp.setText(str(self.mp))
        self.input_el.setText(str(self.el))
        self.input_robots.setText(str(self.robots))
        self.variables = [
            (self.lbl_capa, self.input_capa, self.lbl_resCapa),
            (self.lbl_chromo, self.input_chromo, self.lbl_resChromo),
            (self.lbl_mp, self.input_mp, self.lbl_resMp),
            (self.lbl_el, self.input_el, self.lbl_resEl),
            (self.lbl_robots, self.input_robots, self.lbl_resRobots),
        ]

        # CONNECT SIGNALS
        self.btn_openDistance.clicked.connect(self.openDistance)
        self.btn_openDemand.clicked.connect(self.openDemand)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_run.clicked.connect(self.run)
        self.btn_update.clicked.connect(self.updateVariables)

    def updateVariables(self):

        """ Update Variables From Input and Show Results """

        self.capa = int(self.input_capa.text())
        self.lbl_resCapa.setText(str(self.capa))
        self.chromo = int(self.input_chromo.text())
        self.lbl_resChromo.setText(str(self.chromo))
        self.mp = float(self.input_mp.text()) # Mutation Prob Must Be Float !!
        self.lbl_resMp.setText(str(self.mp))
        self.el = int(self.input_el.text())
        self.lbl_resEl.setText(str(self.el))
        self.robots = int(self.input_robots.text())
        self.lbl_resRobots.setText(str(self.robots))


    def run(self):

        """ Run GA with Variables """

        v = VRP(df = self.df_demand, d_data = self.df_dist, capacity=self.capa, cnum=self.chromo, mutation_prob=self.mp, ev_times=self.el, robots=self.robots)
        s = time.time()
        v.ga()
        e = time.time()
        t = e - s
        self.genData = v.gen
        print("Total Time: ", round(t, 1), "(s)")

        # DRAW GRAPH
        x = [g[0] for g in self.genData]
        y = [g[1] for g in self.genData]
        canvas = FigureCanvas(Figure(figsize=(4, 3)))
        layout = self.verticalLayout
        layout.addWidget(canvas)
        layout.addWidget(NavigationToolbar(canvas, self))
        self.ax = canvas.figure.subplots()
        self.ax.plot(x, y,label="GA", linestyle ='-')
        self.ax.set_xlabel("Generations")
        self.ax.set_ylabel("Min Distance")
        self.ax.set_title("GA")
        self.ax.legend()

    def reset(self):

        """ Reset Tables and Data """

        self.distanceFile = self.demandFile = None
        self.txt_distanceData.setText("-")
        self.txt_demandData.setText("-")
        self.distanceTable.clear()
        self.demandTable.clear()


    def openDistance(self):

        """ Open Excel Files with Distance Data """

        fname = QFileDialog.getOpenFileName(self)
        self.distanceFile = fname[0]
        self.txt_distanceData.setText(self.distanceFile)
        self.df_dist = pd.read_excel(self.distanceFile,header=None)
        self.distanceTable.setRowCount(len(self.df_dist))
        self.distanceTable.setColumnCount(len(self.df_dist))

        for i in range(len(self.df_dist)):
            for j in range(len(self.df_dist)):
                self.distanceTable.setItem(i, j, QTableWidgetItem(str(self.df_dist[i][j])))
        #self.distanceTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def openDemand(self):

        """ Open Excel Files with Demand Data """

        fname = QFileDialog.getOpenFileName(self)
        self.demandFile = fname[0]
        self.txt_demandData.setText(self.demandFile)
        self.df_demand = pd.read_excel(self.demandFile)
        self.demandTable.setRowCount(len(self.df_demand))
        self.demandTable.setColumnCount(1)

        for i in range(len(self.df_demand)):
            for j in range(0,1):
                self.demandTable.setItem(i, j, QTableWidgetItem(str(self.df_demand.iloc[i,j])))
        self.demandTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.demandTable.setHorizontalHeaderLabels(["Demand"])
        self.df_demand.index = range(1,len(self.df_demand)+1)


if __name__ == "__main__" :

    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()