"""
Identifies python files in a directory
and lints them
"""

import argparse
import glob

import matplotlib.pyplot as plt

import pandas as pd
from pylint.lint import Run

__author__ = 'edwardcannon'

class CodeChecker(object):
    """
    Lints a python code base
    """
    def __init__(self, idir):
        self.input_directory = idir
        self.lint_df = None

    def identify_all_py(self):
        """
        Identifies all python files recursively in a directory
        and who authors them
        :return:
        """
        self.lint_df = pd.DataFrame()
        authors = []
        files = []
        for filename in glob.iglob(self.input_directory+'/**/*.py', recursive=True):
            if '__init__' not in filename:
                with open(filename) as f_handle:
                    content = f_handle.readlines()
                    for line in content:
                        if '__author__' in line:
                            try:
                                authors.append(str(line).
                                               strip().
                                               split('=')[1].
                                               replace("'", "").
                                               replace('"', '').
                                               strip())
                                files.append(filename)
                            except IndexError:
                                print("Ignoring line!")

        assert len(authors) == len(files)
        self.lint_df['Author'] = authors
        self.lint_df['File'] = files
        return self.lint_df

    def lint_code(self, input_df):
        """
        Lints all files in the data frame
        :return:
        """
        scores = []
        for index, row in input_df.iterrows():
            input_file = row['File']
            result = Run([input_file], exit=False)
            scores.append(result.linter.stats['global_note'])
        input_df['pylint_score'] = scores
        return input_df

def set_up_args():
    """
    Sets up argparser with required program
    arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("idir", help='Input file directory to lint')
    parser.add_argument("--author")
    return parser.parse_args()

if __name__ == '__main__':
    args = set_up_args()

    if args.idir:
        cap_code_checker = CodeChecker(args.idir)
        cap_code_checker.identify_all_py()
        if args.author:
            author_file_df = cap_code_checker.lint_df[(cap_code_checker.
                                                       lint_df.Author == args.author)]
            linted_df = cap_code_checker.lint_code(author_file_df)
        else:
            linted_df = cap_code_checker.lint_code(cap_code_checker.lint_df)
        BINS = 10
        plt.hist(linted_df['pylint_score'], BINS, normed=1, facecolor='red', alpha=0.75)
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.title("Pylint Score Distribution")
        plt.show()


