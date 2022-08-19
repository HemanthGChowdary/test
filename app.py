import time
ST=time.time()
from flask import Flask, request, render_template
from itertools import chain, combinations
from werkzeug.utils import secure_filename
import os, sys, csv

app = Flask(__name__)

def hasIrregularChild(lit, D_S, mnsp):
    fri = set([ obj for obj in lit if sum([ obj.issubset(ds) for ds in D_S ]) >= mnsp])
    return fri


def persion_belongs(fi, ino):
    data = set( [ i2.union(i1) for i1 in fi for i2 in fi if len(i2.union(i1)) == ino ] )
    return data

def prepareSS(persion, redo):
    li = list(chain.from_iterable(combinations(persion, j) for j in range(redo-1, redo)))
    return  set( [ frozenset(list(i)) for i in li ])


def apriori_gen(read_lines, mnsp):
    FD, myis, ino = [], set(), 2
    for record in read_lines:
        recordNo, record = record[0], list(map(int, record[1:]))
        myis = myis.union(record)
        record.append( recordNo + 'key' )
        data = frozenset( record )
        FD.append(data)

    myis = list(set(frozenset([i]) for i in myis) )
    regular = hasIrregularChild( myis, FD, mnsp)
    regular_S = regular.copy()

    while True:
        perbe = persion_belongs(regular, ino)
        dup_I = set()
        for bolon in perbe:
            division = prepareSS(bolon, ino)
            count = division.intersection(regular)
            if len(count) == len(division):
                dup_I.add(bolon)

        perbe = dup_I
        regular = hasIrregularChild(perbe, FD, mnsp)

        if not regular:
            break
        else:
            for ri in regular:
                regular_S.add(ri)
                regular_S = regular_S - prepareSS(ri, ino)

            ino += 1

    return [set(z) for z in regular_S]


@app.route('/', methods=['GET', 'POST'])
def main():
    context = { "error": None, "result": "", "no_of_items":0, "file_name":"" }
    return render_template('index.html', data=context)


@app.route('/result/', methods=['POST'])
def sub_index():
    context = { "error": None, "result": "", "no_of_items":0, "file_name":"" }
    if (request.method == 'POST') and ('csv' in request.files) and (request.files['csv'].filename != ""):
        try:
            csvFile = request.files['csv']
            mnsp = request.form.get('min_sup')
            csvFile.save(secure_filename(csvFile.filename))

            with open(csvFile.filename, "r") as fobj: #fobj - file object
              data = list(csv.reader(fobj))
            result = apriori_gen(data, int(mnsp))
            os.remove(csvFile.filename)

            context["file_name"] = csvFile.filename
            context['result'] = result
            context['no_of_items'] = len(result)
            context['time']=round( (time.time()-ST)/100, 3)
        except Exception as e:
            context['error'] = str(e)
            with open('err.text', 'w+') as te:
                te.writelines(str(e))
    return render_template('result.html', data=context)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
