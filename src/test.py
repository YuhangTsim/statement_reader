import tempfile
import subprocess


def pdf_to_string(file_object):
    pdfData = file_object.read()
    tf = tempfile.NamedTemporaryFile()
    tf.write(pdfData)
    tf.seek(0)
    outputTf = tempfile.NamedTemporaryFile()

    if (len(pdfData) > 0):
        out, err = subprocess.Popen(
            ["pdftotext", "-layout", tf.name, outputTf.name]).communicate()
        return outputTf.read()
    else:
        return None


if __name__ == '__main__':
    pdf_file = "./data/pdf/test.pdf"
    try:
        file_object = open(pdf_file, 'rb')
        file_str = pdf_to_string(file_object)
        if len(file_str) > 100:
            print(" Success. PdftoText is good to go.")
        else:
            print(" Something wrong.")
    except Exception as e:
        print(" Something wrong : %s" % e)
