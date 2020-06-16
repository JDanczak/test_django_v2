from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import HttpResponse
import sounddevice as sd
import numpy as np
import math
import sys
from subprocess import run, PIPE
import scipy.io.wavfile
from io import StringIO
import matplotlib.pyplot as plt
import json
import matplotlib.backends.backend_agg
# Create your views here.
global_x = np.array(0)
global_y = np.array(0)


def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html', {'name': 'Janek'})


def main(request):
    return render(request, 'main.html')

def result2(request):
    return render(request, 'result2.html')

def add(request):
    # inicjalizacja zmiennych
    sciany = ["podloga", "sufit", "boczna1", "boczna2", "przod", "tyl"]
    a_śr = 0.0
    a_śr_sciana = 0.0
    A = 0.0

    #przypisanie wartości zmiennych głównych z formularza
    L = float(request.GET['L'])
    W = float(request.GET['W'])
    H = float(request.GET['H'])

    wspolczynnik_podloga =float(request.GET['a_podloga'])
    wspolczynnik_sufit =float(request.GET['a_sufit'])
    wspolczynnik_boczna1 =float(request.GET['a_b1'])
    wspolczynnik_boczna2 =float(request.GET['a_b2'])
    wspolczynnik_przod =float(request.GET['a_przod'])
    wspolczynnik_tyl =float(request.GET['a_tyl'])
    wspolczynniki = [wspolczynnik_podloga, wspolczynnik_sufit, wspolczynnik_boczna1,wspolczynnik_boczna2, wspolczynnik_przod, wspolczynnik_tyl]


    # przypisanie wartości zmiennych powierzchni dodatkowych z formularza
    #ktora_sciana1 = request.GET['powierzchnie1']
    H_p1 = float(request.GET['h_p1'])
    # W_p1 = float(request.GET['w_p1'])
    #A_p1 = float(request.GET['a_p1'])


    # powierzchnia i objetosc calkowita
    S_sufit = S_podloga = L * W
    S_boczna1 = S_boczna2 = W * H
    S_przod = S_tyl = L * H
    S = S_sufit + S_podloga + S_boczna1 + S_boczna2 + S_przod + S_tyl
    V = L * W * H

    S_scian = [S_podloga, S_sufit, S_boczna1, S_boczna2, S_przod, S_tyl]

    # obliczenie chlonnosci akustycznej
    i = 0
    for wspolczynniki_scian in wspolczynniki:
        A = A + wspolczynniki_scian * S_scian[i]
        i += 1
    i = 0

    a_śr = A/S


    # obliczenie czasu pogłosu
    if (a_śr >= 0.2):
        # wzór Eyringa
        T_60 = (-0.161 * V) / (S * math.log10((1 - a_śr)))
        wzor = "Eyring'a"
    else:
        # wzór Sabine'a
        T_60 = (0.161 * V) / (S * a_śr)
        wzor = "Sabine'a"

    #czas w milisekundach
    T_60 = T_60 * 1000
    T_60 = round(T_60, 1)
    A = round(A, 2)
    a_śr = round(a_śr,3)

    return render(request, 'result2.html', {"V": V, "S": S, "A": A, "a": a_śr, "T_60": T_60, "wzor": wzor})

@csrf_exempt
def upload(request):

    audio_blob = request.FILES["audio_data"]

    [sample_rate, audio_array] = scipy.io.wavfile.read(audio_blob)
    [energy, time_s] = energy_decay(audio_array, sample_rate, 80)
    # what I get is energy and time_s
    # now basic calculations for cursor are being done
    position = int(len(time_s)/2)
    #cursor_x = [time_s[position], time_s[position+100]]
    cursor_x = [position, position + 100]
    cursor_y = [-20, -80]
    list_time_s = time_s
    list_energy = energy

    json_time_s = json.dumps(list_time_s)
    json_energy = json.dumps(list_energy)
    json_cursor_x = json.dumps(cursor_x)
    json_cursor_y = json.dumps(cursor_y)
    request.session['r_time_s'] = json_time_s
    request.session['r_energy'] = json_energy
    request.session['cursor_x'] = json_cursor_x
    request.session['cursor_y'] = json_cursor_y
    cursor_x = [time_s[cursor_x[0]], time_s[cursor_x[1]]]


    fig = plot_graph(time_s, energy, cursor_x, cursor_y)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return render(request, "result.html", {'result': "", 'graph': data})


def display(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    res = rt60_calc(time, cursor_x)
    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return render(request, "result.html", {'result': res, 'graph': data})

def cursor_up(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_y[0] + 5 <= 0:
        cursor_y[0] = cursor_y[0] + 5
        cursor_y[1] = cursor_y[1] + 5
        msg = rt60_calc(time, cursor_x)
        json_cursor_y = json.dumps(cursor_y)
        request.session['cursor_y'] = json_cursor_y
    else:
        msg = "Nie można ustawić kursora powyżej 0 dB."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})


def cursor_down(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_y[1] - 5 >= -100:
        cursor_y[0] = cursor_y[0] - 5
        cursor_y[1] = cursor_y[1] - 5
        msg = rt60_calc(time, cursor_x)
        json_cursor_y = json.dumps(cursor_y)
        request.session['cursor_y'] = json_cursor_y
    else:
        msg = "Nie można ustawić kursora poniżej -100 dB."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})

def cursor_left(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_x[0]-50 > 0:
        cursor_x = [cursor_x[0]-50, cursor_x[1]-50]
        temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
        msg = rt60_calc(time, cursor_x)
        json_cursor_x = json.dumps(cursor_x)
        request.session['cursor_x'] = json_cursor_x
    else:
        msg = "Nie można ustawić kursora poniżej 0 s."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})

def cursor_right(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_x[1] + 50 < len(time):
        cursor_x = [cursor_x[0]+50, cursor_x[1]+50]
        temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
        msg = rt60_calc(time, cursor_x)
        json_cursor_x = json.dumps(cursor_x)
        request.session['cursor_x'] = json_cursor_x
    else:
        msg = "Nie można ustawić kursora poniżej 0 s."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})


def tilt_bigger(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_x[0] + 6 < cursor_x[1] and cursor_x[1] - 6 > cursor_x[0]:
        cursor_x = [cursor_x[0]+6, cursor_x[1]-6]
        temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
        msg = rt60_calc(time, cursor_x)
        json_cursor_x = json.dumps(cursor_x)
        request.session['cursor_x'] = json_cursor_x
    else:
        msg = "Nie można ustawić kursora poniżej 0 s."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})

def tilt_smaller(request):
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)
    cursor_x = request.session['cursor_x']
    cursor_x = json.loads(cursor_x)
    temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
    cursor_y = request.session['cursor_y']
    cursor_y = json.loads(cursor_y)

    if cursor_x[0]-6 > 0 and cursor_x[1] + 6 < len(time):
        cursor_x = [cursor_x[0]-6, cursor_x[1]+6]
        temp_cursor_x = [time[cursor_x[0]], time[cursor_x[1]]]
        msg = rt60_calc(time, cursor_x)
        json_cursor_x = json.dumps(cursor_x)
        request.session['cursor_x'] = json_cursor_x
    else:
        msg = "Nie można ustawić kursora poniżej 0 s."

    fig = plot_graph(time, energy, temp_cursor_x, cursor_y)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return render(request, "result.html", {'result': msg, 'graph': data})




def plot_graph(f_time, f_energy, x_cur, y_cur):
    fig = plt.figure(figsize=(14, 5))
    plt.rcParams['savefig.facecolor'] = '#1F1B2A'
    plt.rcParams['axes.facecolor'] = '#1F1B2A' #'#F9741B'
    plt.rcParams['axes.edgecolor'] = '#F9741B'
    plt.rcParams['axes.labelcolor'] = '#F9741B'
    plt.rcParams['xtick.color'] = '#F9741B'
    plt.rcParams['ytick.color'] = '#F9741B'
    plt.plot(f_time, f_energy)
    plt.plot(x_cur, y_cur, 'r-+')
    plt.grid(b=True, which='major', color='#E7356A', linestyle='-', alpha=0.7)
    plt.grid(b=True, which='minor', color='#E7356A', linestyle=':', alpha=0.5)
    # plt.xlim(-100,0)
    plt.minorticks_on()
    plt.xlabel("time [s]")
    plt.ylabel("level [dB]")
    """#plt.rcParams['axes.facecolor'] = 'red'
    plt.rcParams['savefig.facecolor'] = '#1F1B2A'
    plt.rcParams['axes.facecolor'] = '#1F1B2A' #'#F9741B'
    plt.rcParams['axes.edgecolor'] = '#F9741B'
    plt.rcParams['axes.labelcolor'] = '#F9741B'
    plt.rcParams['grid.color'] = '#F9741B'
    plt.rcParams['xtick.color'] = '#F9741B'
    plt.rcParams['ytick.color'] = '#F9741B'"""

    return fig


def energy_decay(f_data, f_sample_rate, f_averaging, f_reference=32767):
    time_div = f_averaging/f_sample_rate
    signal_length = len(f_data)
    out_length = int(signal_length/f_averaging)
    offset = 0
    energy = []
    time_s = []
    for i in range(out_length):
        sum_of_squares = np.int64(0)
        for j in range(f_averaging):
            sum_of_squares += abs(np.int64(f_data[j+offset])*np.int64(f_data[j+offset]))
        offset += f_averaging
        momentary_rms = math.sqrt(sum_of_squares/f_averaging)
        # momentary_rms_db = 20*math.log10(momentary_rms/f_reference)
        if momentary_rms != 0:
            momentary_rms_db = 20 * math.log10(momentary_rms / f_reference)
        else:
            momentary_rms_db = -90.0
        energy.append(momentary_rms_db)
        time_s.append(time_div*i)
    return energy, time_s

def rt60_calc(ax_time, markers):
    time = ax_time[markers[1]] - ax_time[markers[0]]
    time = "%.2f" % round(time, 2)
    outstring = "RT60 = " + str(time) + " s"
    return outstring
# FUNCTIONS NOT USED AT THE MOMENT


"""def add(request):
    val1 = float(request.POST['num1'])
    val2 = float(request.POST['num2'])
    res = val1 + val2

    # json_audio = request.session['audio_file']
    # audio = str.split(audio)
    # audio = json.loads(json_audio)
    # audio = np.array(audio)
    energy = request.session['r_energy']
    energy = json.loads(energy)
    time = request.session['r_time_s']
    time = json.loads(time)

    fig = plt.figure()
    plt.plot(time, energy)
    plt.grid(b=True, which='major', color='k', linestyle='-', alpha=0.7)
    plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
    plt.minorticks_on()
    plt.xlabel("time [s]")
    plt.ylabel("level [dB]")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return render(request, "result.html", {'result': res, 'graph': data})"""


"""def external(request):
    wej = request.POST.get('param')
    wyj = run([sys.executable, "external_test.py", wej], shell=False, stdout=PIPE)
    print(wyj)
    return render(request, 'home.html', {'name': wyj})"""

"""def plot_energy_decay(time_div, energy, zoom=1):
    # figure = plt.plot()
    length = len(energy)
    print("dlugosc", length)
    if zoom > 1:
        new_length = length / (2*zoom)
        new_time_div = time_div[int((length/2) - new_length):int((length/2)+new_length)]
        new_energy = energy[int((length/2) - new_length):int((length/2)+new_length)]
        plt.plot(new_time_div, new_energy)
        plt.grid(b=True, which='major', color='k', linestyle='-', alpha=0.7)
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.xlabel("time [s]")
        plt.ylabel("level [dB]")
        # plt.show()


    else:
        plt.plot(time_div, energy)
        plt.grid(b=True, which='major', color='k', linestyle='-', alpha=0.7)
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.xlabel("time [s]")
        plt.ylabel("level [dB]")
        # plt.show()

    return figure"""

"""
[sample_rate, audio_array] = scipy.io.wavfile.read(audio_blob)

flength = type(audio_array)
#[y_energy, x_time] = energy_decay(audio_array, sample_rate, 80)
x = np.arange(0, np.pi * 3, .1)
y = np.sin(x)
#request.session['audio_file'] = audio_array
lista = audio_array.tolist()
json_str = json.dumps(lista)
request.session['audio_file'] = json_str

json_audio = request.session['audio_file']
# audio = str.split(audio)
audio = json.loads(json_audio)
audio = np.array(audio)
# array = str(audio)#np.array(audio)"""

"""fig = plt.figure()
plt.plot(audio_array)

imgdata = StringIO()
fig.savefig(imgdata, format='svg')
imgdata.seek(0)

data = imgdata.getvalue()

return render(request, 'home.html', {'name': str(audio_array), 'graph': data})"""