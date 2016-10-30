"""
Qt Application to monitor static code performance

"""
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QWidget, QLabel
from PyQt5.QtWidgets import QRadioButton, QTabWidget, QFormLayout, QComboBox, QMessageBox
from PyQt5.QtCore import Qt

from eoc21.pylint_app.pylint_directory import CodeChecker


__author__ = 'edwardcannon'

class CodeCheckerMainWindow(QMainWindow):
    """
    Main window for Code checker application
    """
    def __init__(self, parent=None):
        super(CodeCheckerMainWindow, self).__init__(parent=parent)
        self.entry_point = EntryPoint()
        self.setCentralWidget(self.entry_point)
        self.setWindowTitle("Data Science")

class EntryPoint(QTabWidget):
    """
    Class to set up separate tabs in main
    widget
    """
    def __init__(self, parent=None):
        super(EntryPoint, self).__init__(parent=parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = StaticCodeAnalyzerWidget()
        self.addTab(self.tab1, "ml")
        self.addTab(self.tab2, "visualisation")
        self.addTab(self.tab3, "lint")
        self.ml_ui()
        self.timeseries_ui()
        self.lint_ui()

    def ml_ui(self):
        """
        Machine learning tab
        """
        layout = QFormLayout()
        comboBox = QComboBox(self)
        comboBox.addItem("Naive Bayes")
        comboBox.addItem("Random Forest")
        comboBox.addItem("K-NN")
        comboBox.addItem("SVM")
        layout.addWidget(comboBox)
        self.setTabText(0, "Machine Learning")
        self.tab1.setLayout(layout)

    def timeseries_ui(self):
        """
        Time series tab
        """
        layout = QFormLayout()
        description = QLabel("Plot time series,"
                             " specify period")
        layout.addWidget(description)
        ts_layout = QHBoxLayout()
        ts_layout.addWidget(QRadioButton("Yearly"))
        ts_layout.addWidget(QRadioButton("Monthly"))
        ts_layout.addWidget(QRadioButton("Weekly"))
        ts_layout.addWidget(QRadioButton("Daily"))
        layout.addRow(QLabel("Period"), ts_layout)
        self.setTabText(1, "Time Series")
        self.tab2.setLayout(layout)

    def lint_ui(self):
        """
        Static code analyzer tab
        """
        self.setTabText(2, "Static Code Analyzer")
        self.tab3.setup_ui()

class StaticCodeAnalyzerWidget(QWidget):
    """
    Static code analyzer widget
    """
    def __init__(self, parent=None):
        super(StaticCodeAnalyzerWidget, self).__init__(parent=parent)
        self.layout = QFormLayout()
        self.repo_path = QLineEdit()
        self.author = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(lambda: self.whichbtn(self.submit_button))
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.canvas)

    def setup_ui(self):
        """
        Sets up static code analyzer interface
        :return:
        """
        self.layout.addRow("Python Repository Path:", self.repo_path)
        self.layout.addRow("Author:", self.author)
        self.layout.addRow(self.submit_button)
        self.setLayout(self.layout)

    def whichbtn(self, button):
        """
        Runs linting on submit
        :param button: submit button
        :return:
        """
        print("Starting linting for:")
        print(self.repo_path.text())
        print(self.author.text())
        if not self.repo_path.text():
            qmb = QMessageBox()
            qmb.setText("No repository path!")
            qmb.exec_()
            return
        try:
            cap_code_checker = CodeChecker(self.repo_path.text())
            df1 = cap_code_checker.identify_all_py()
            if not self.author.text():
                df3 = cap_code_checker.lint_code(df1)
            else:
                df2 = df1[(df1.Author == self.author.text())]
                df3 = cap_code_checker.lint_code(df2)
            self.create_lint_chart(df3)
        except:
            qmb = QMessageBox()
            qmb.setText("Path does not exist")
            qmb.exec_()

    def create_lint_chart(self, input_df):
        """
        Creates pop up histogram of pylint
        score distribution
        :param input_df: input data frame with lint scores
        :return:
        """
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.hist(input_df['pylint_score'], bins=10)
        ax.set_xlabel('Lint Score')
        ax.set_ylabel('Frequency')
        mean_score = round(input_df['pylint_score'].mean(), 2)
        ax.set_title('Pylint Score Distribution:'+self.author.text()
                     +", Avg Score:"+str(mean_score))
        self.canvas.draw()
        self.canvas.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CodeCheckerMainWindow()
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec_())
