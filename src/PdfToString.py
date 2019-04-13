""" tool to tranform pdf into text  """

import subprocess
import tempfile
# import argparse


def pdf_to_string(file_object):
    """ general pdf to string """
    pdfData = file_object.read()
    tf = tempfile.NamedTemporaryFile()
    tf.write(pdfData)
    tf.seek(0)
    outputTf = tempfile.NamedTemporaryFile()
    if pdfData:
        out, err = subprocess.Popen(
            ["pdftotext", "-layout", tf.name, outputTf.name]).communicate()
        return outputTf.read().decode('utf-8')
    else:
        return None


if __name__ == '__main__':
    with open('./../data/pdf/Wide Neural Networks of Any Depth Evolve as Linear Models Under Gradient Descent.pdf', 'rb') as file_name:
        text = pdf_to_string(file_name).decode('utf-8')
        print(f"Successfully read this pdf! \nThere are {len(text)} words.")
