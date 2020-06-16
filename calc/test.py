import sounddevice as sd
import scipy.io.wavfile
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import cmath
import wave
import struct
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
            sum_of_squares += np.int64(f_data[j+offset])*np.int64(f_data[j+offset])
        offset += f_averaging
        momentary_rms = math.sqrt(sum_of_squares/f_averaging)
        momentary_rms_db = 20*math.log10(momentary_rms/f_reference)
        energy.append(momentary_rms_db)
        time_s.append(time_div*i)
    return energy, time_s
global InDevice
global OutDevice





def plot_energy_decay(time_div, energy, zoom=1):
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
        plt.show()


    else:
        plt.plot(time_div, energy)
        plt.grid(b=True, which='major', color='k', linestyle='-', alpha=0.7)
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.xlabel("time [s]")
        plt.ylabel("level [dB]")
        plt.show()


def set_devices():
    print("avaliable devies: ")
    print(sd.query_devices())

    print("select input device: ")
    f_input = int(input())
    print("selected input device: ", f_input)

    print("select output device: ")
    f_output = int(input())
    print("selected output device: ", f_output)
    sd.default.device = (f_input, f_output)
    print(sd.default.device)


def measure(f_band, f_averaging=80):
    if f_band == '125':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_125_Hz.wav")
    elif f_band == '250':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_250_Hz.wav")
    elif f_band == '500':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_500_Hz.wav")
    elif f_band == '1000':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_1000_Hz.wav")
    elif f_band == '2000':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_2000_Hz.wav")
    elif f_band == '4000':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_4000_Hz.wav")
    elif f_band == '8000':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_8000_Hz.wav")
    elif f_band == 'full':
        [f_sample_rate, f_data] = scipy.io.wavfile.read("4_full_range.wav")
    else:
        print("No band selected. Select the right band to measure.")
        return 1

    f_measurement = sd.playrec(f_data, f_sample_rate, 1, blocking=True)
    sd.wait()
    [f_energy, f_division] = energy_decay(f_measurement, f_sample_rate, f_averaging)
    return f_energy, f_division
"""
sd.default.device = 20, 20
[sample_rate, data] = scipy.io.wavfile.read("test_noise.wav")
print(len(data))
print(sd.default.device)
print(sd.query_devices())
myrecording = sd.playrec(data, sample_rate, 1, blocking=True)
print("GRAM!")
print(len(myrecording))
#sd.play(myrecording, sample_rate)
sd.wait()
print("odtworzylo")
[energia, podzialka] = energy_decay(myrecording, sample_rate, 80)
plot_energy_decay(podzialka, energia)

"""
#set_devices()
sd.default.device = 20,20
[energia, podzialka] = measure('2000')
plot_energy_decay(podzialka, energia)
plot_energy_decay(podzialka, energia, 8)
plot_energy_decay(podzialka, energia, 11)
plot_energy_decay(podzialka, energia, 16)





###RUBBISH_BIN###

#scipy.io.wavfile.write("output.wav", sample_rate, myrecording)
""""
[ttt_sample_rate, ttt_data] = scipy.io.wavfile.read("output.wav")
[rec_en, tdiv] = energy_decay(ttt_data, ttt_sample_rate, 40)
plot_energy_decay(tdiv, rec_en)
#print(pink_noise_gen(100, 44100))
"""
"""
sd.default.device = 20, 20
print(sd.query_devices())
duration = 10  # seconds
fs = 48000
channels = 1
myrecording = sd.rec(int(duration*fs), fs, channels)
sd.wait()
print("nagralo")
sd.play(myrecording, fs)
sd.wait()
print("odtworzylo")
print(sd.default.device)
"""

"""
def pink_noise_gen(f_length, f_sample_rate, f_band=17012):
    number_of_points = f_length*f_sample_rate
    kmax = int(f_band*np.pi*2/f_length) + 1
    pos_coeff_magnitudes = []
    neg_coeff_magnitudes = []
    pos_coefficients = []
    neg_coefficients =[]
    for i in range(kmax):
        freq = i*f_length/(2*np.pi)
        if freq == 0:
            pos_coeff_magnitudes.append(0)
        else:
            pos_coeff_magnitudes.append(abs(1/freq))
    print("punkty: %d, kmax: %d, wspolczynniki: %d"%(number_of_points, kmax, len(pos_coeff_magnitudes)))
    for i in range(kmax):
        if i > 0:
            freq = i*f_length/(2*np.pi)
            neg_coeff_magnitudes.append(-abs(1/freq))
    print("punkty: %d, kmax: %d, wspolczynniki: %d" % (number_of_points, kmax, len(neg_coeff_magnitudes)))
    for j in range(kmax):
        phi = random.uniform(0, 2*np.pi)
        temporary_coefficient = pos_coeff_magnitudes[j]*np.exp(im_unit*phi)
        pos_coefficients.append(temporary_coefficient)
        if j > 0:
            temporary_coefficient = neg_coeff_magnitudes[j-1]*np.exp(- im_unit*phi)
            neg_coefficients.append(temporary_coefficient)
    print("dlugosc pos: ", len(pos_coefficients))
    print("dlugosc neg: ", len(neg_coefficients))
    total_coefficients = pos_coefficients + neg_coefficients
    print("dlugosc: ", len(total_coefficients))
    generated_noise = np.fft.ifft(total_coefficients)
    print("dlugosc szumu: ", len(generated_noise))
    plt.plot(abs(generated_noise))
    plt.show()
    return total_coefficients

"""
"""
for i in range(5):
    sample_data = rev_file.readframes(i)
    print(type(sample_data))
    print(sample_data)
"""

"""
fs = 44100  # Sample rate
seconds = 15  # Duration of recording
energy=[]
part_energy=0
sum_of_squares=0
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()  # Wait until recording is finished

for sample in range(int((seconds*fs)/80)):
    for item in range(80):
        sum_of_squares += (myrecording[sample+item])*(myrecording[sample+item])
    part_energy = math.sqrt(sum_of_squares/80)
    energy.append(part_energy)
    part_energy=0
    sum_of_squares=0
print(len(energy))
plt.plot(energy)
plt.show()
print(energy)
write('output.wav', fs, myrecording)  # Save as WAV file
"""