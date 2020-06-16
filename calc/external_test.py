import sounddevice as sd
import scipy.io.wavfile

[f_sample_rate, f_data] = scipy.io.wavfile.read("4_500_Hz.wav")
sd.play(f_data, f_sample_rate, blocking=True)
sd.wait()
print("DONE.")
