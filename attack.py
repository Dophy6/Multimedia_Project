import os
from pydub import AudioSegment
from scipy.signal import butter, lfilter

CURRENT_PATH = os.path.abspath(os.getcwd())
DATA_PATH = "/TOP10/"
FILTERS ={
	"LP" : butter_bandpass(0, 7350, 44100, order=5),
	"MP" : butter_bandpass(7350, 14700, 44100, order=5),
	"HP" : butter_bandpass(14700, 22050, 44100, order=5)
}

def change_ext(file_path, ext):
    song = AudioSegment.from_wav(path)
    file_path = file_path.replace("TOP10/","TOP10/EXT/")
    song.export("{}.{}".format(path,ext), format=ext)
	return file_path

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs #Nyquist frequence
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_butter_bandpass_filter(file_path, butter_filter):
	samplingFrequency, signalData = wavfile.read(file_path)
    b, a = FILTERS[butter_filter]
    y = lfilter(b, a, signalData)
	file_path = file_path.replace("TOP10/","TOP10/BAND_PASS/").replace(".wav", "_{}.wav".format(butter_filter))
	wavfile.write(file_path,samplingFrequency,y)
	return file_path

def add_white_noise(file_path,SNR):#Additive white gausian noise.
    samplingFrequency, signalData = wavfile.read(file_path)
    RMS_s=math.sqrt(np.mean(signalData**2))#RMS value of signal
    RMS_n=math.sqrt(RMS_s**2/(pow(10,SNR/20)))#RMS values of noise
    #Therefore mean=0, to round you can use RMS as STD
    noise=np.random.normal(0, RMS_n, signal.shape[0])
	signal_edit = signalData + noise
	file_path = file_path.replace("TOP10/","TOP10/NOISE/").replace(".wav", "_NOISE-.wav".format(SNR))
	wavfile.write(file_path,samplingFrequency,signal_edit)
	return file_path

def calc_specto(wav_overlay_paths, img_wav_paths=[]):
	wav_overlay_specto = []
	# The wav file must be mono, not stereo
	for f_n in wav_overlay_paths:
		samplingFrequency, signalData = wavfile.read(f_n)
		frequencies, times, spectrogram = signal.spectrogram(signalData, samplingFrequency)
		wav_overlay_specto.append({
				"name": (f_n.split("/"))[-1],
				"frequencies": frequencies,
				"times":times,
				"spectrogram": spectrogram
			})
	return wav_overlay_specto

def create_save_plot(wav_overlay_specto):

	for i in range(len(wav_overlay_specto)):

		fig, axs = plt.subplots(1, 1, figsize=(150,72), squeeze=False)
		fig.suptitle('Fabio Merola W82000188 - MM project - Steganografia audio')

		axs[0, 0].pcolormesh(wav_overlay_specto[i]["times"], wav_overlay_specto[i]["frequencies"], np.log(wav_overlay_specto[i]["spectrogram"]))
		axs[0, 0].set_title(wav_overlay_specto[i]["name"])
		dim = axs[0, 0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
		path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[i]["name"] + ".png"
		fig.savefig(path, bbox_inches=dim)
		fig.clear()
		plt.close("all")

def images_post_processing():
	for filename in os.listdir(CURRENT_PATH + DATA_PATH + "IMG_SPECTO"):
		if filename.endswith(".png"):
			temp = Image.open(CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + filename)
			
			temp = temp.convert('LA')
			
			temp = temp.point(lambda p: 0 if p>=245 else p)
			temp = temp.filter(MaxFilter(size=9)) #Dilatation
			temp = temp.filter(MinFilter(size=9)) #Erosion
			temp = temp.point(lambda p: 0 if p<205 else 255) #Tresholding
			
			width, height = temp.size # Get dimensions
			temp = temp.convert('RGB')
			
			width /= 6
			height /= 6
			newsize = (width, height) 
			temp = temp.resize(newsize) #Resize for better OCR read
			temp = temp.point(lambda p: 0 if p!=255 else 255) # delete interpolation artifacts
			left = 1
			top = 1
			right = width-1
			bottom = height-1
			temp = temp.crop((left, top, right, bottom)) # This crop removes white borders in order to improve the reading of OCR

			temp.save(CURRENT_PATH + DATA_PATH + "POST_P_IMG/" + filename + ".png")

def images_in_ocr():
	for filename in os.listdir(CURRENT_PATH + DATA_PATH + "POST_P_IMG"):
		if filename.endswith(".png"):
			text = image_to_string(Image.open(CURRENT_PATH + DATA_PATH + "POST_P_IMG/"+filename))
			print("- IMG: {}\n\t- OCR_TEXT: {}".format(filename.encode('ascii', 'replace'), text.encode('ascii', 'replace')))


if __name__ == '__main__':
	
	folders_needed = ["EXT", "BAND_PASS", "NOISE", "IMG_SPECTO", "POST_P_IMG/"]
	SNR = [5,10,20] #SNR -> Signal to Noise Ratio
	EXT = ["mp3", "wma", "aac"]
	wav_paths = []
	if not os.path.exists(CURRENT_PATH + DATA_PATH[:-1]):
		os.mkdir(CURRENT_PATH + DATA_PATH[:-1])

	for folder in folders_needed:
		if not os.path.exists(CURRENT_PATH + DATA_PATH + folder):
			os.mkdir(CURRENT_PATH + DATA_PATH + folder)

	for filename in os.listdir(CURRENT_PATH + DATA_PATH[:-1]):
		if filename.endswith(".wav"):
			print("\n\nSTARTING WORKING WITH: {}\n\n".format(filename))
			filename = CURRENT_PATH + DATA_PATH + filename
			wav_paths += [change_ext(filename, ext) for ext in EXT]
			wav_paths += [apply_butter_bandpass_filter(filename, butter_filter) for butter_filter in FILTERS.keys()]
			wav_paths += [add_white_noise(filename,snr) for snr in SNR]
	
	print("\n\nSTARTING CALC_SPECTO\n\n")
	wav_overlay_specto = calc_specto(wav_overlay_paths=wav_paths)

	gc.collect()

	print("\n\nSTARTING CREATE_SAVE_PLOT\n\n")
	create_save_plot(wav_overlay_specto=wav_overlay_specto)

	print("\n\nSTARTING IMAGES_POST_PROCESSING\n\n")
	images_post_processing()
	
	print("\n\nSTARTING IMAGES_IN_OCR\n\n")
	images_in_ocr()



