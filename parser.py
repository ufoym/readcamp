import sys, os
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

class Parser(object):
    """pdf Parser"""
    def __init__(self, pdf_fn, pdf_pwd = ''):
        self.title = ''
        self.parse(pdf_fn, pdf_pwd)

    def parse(self, pdf_fn, pdf_pwd, max_page = 2):
        with open(pdf_fn, 'rb') as pdf_file:
            parser = PDFParser(pdf_file)
            doc = PDFDocument()
            parser.set_document(doc)
            doc.set_parser(parser)
            doc.initialize(pdf_pwd)

            if doc.is_extractable:
                rsrcmgr = PDFResourceManager()
                device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                # text with maximum score as title
                max_score = 0
                for i, page in enumerate(doc.get_pages()):
                    if i > max_page:   break
                    interpreter.process_page(page)
                    layout = device.get_result()
                    for lt_obj in layout:
                        if isinstance(lt_obj, LTTextBox) \
                        or isinstance(lt_obj, LTTextLine):
                            text = lt_obj.get_text().strip()
                            if not text:    continue
                            num_lines = text.count('\n') + 1
                            # feature: height of text box
                            height = lt_obj.height / num_lines
                            # feature: page where text locates
                            page_decay = pow(0.9, i)
                            # feature: valid character ratio
                            char_num, length = 0, 0
                            for c in text.lower():
                                if c == ' ' or c == '\n':
                                    continue
                                if 'a' <= c <= 'z':
                                    char_num += 1
                                length += 1
                            char_ratio = float(char_num) / length
                            # final score
                            score = height * page_decay * char_ratio

                            if score > max_score:
                                self.title, max_score = text, score
            else:
                print 'this pdf is not extractable'

    def get_title(self):
        title = self.title.replace('\n', ' ')
        title = ' '.join([s for s in title.split(' ') if s])
        return title

path = 'var\\'
for fn in os.listdir(path):
    if fn.endswith('.pdf'):
        print '#', fn
        print Parser(path+fn).get_title()
        print