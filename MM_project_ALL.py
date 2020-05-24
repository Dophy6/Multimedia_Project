import wave, os, gc
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from array import array
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ImageFilter import MinFilter, MaxFilter
from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.playback import play
from pytesseract import image_to_string

CURRENT_PATH = os.path.abspath(os.getcwd())
DATA_PATH = "/DATA/"
FONTS_PATH = "/Fonts/"
ORIGINAL_AUDIO_PATH = CURRENT_PATH + "/Tchaikovsky - Danza della fata confetto(44,1k).wav"

def text_on_img(filename, text, size=300, exstension=".pbm", freq="HF", font_size=50, font='FreeSansBold.ttf'): # HF = High Frequency, LF = Low Frequency
	filename = CURRENT_PATH + DATA_PATH + "IMG/" +filename + "_" + freq + exstension
	fnt = ImageFont.truetype(CURRENT_PATH + FONTS_PATH + font, font_size)
	image = Image.new(mode = "RGB", size = (int(size/2)*len(text),size+font_size), color = "black")
	draw = ImageDraw.Draw(image)
	if freq == "HF":
		draw.text((0,1), text.upper(), font=fnt, fill=(255,255,255))
	elif freq == "LF":
		draw.text((0,size-1), text.upper(), font=fnt, fill=(255,255,255))
	image.save(filename)
	print("text_on_img\t{}\tsaved".format(filename))
	return filename

def make_wav_from_img(image_filename, sampling_freq=44100): 
	image = mpimg.imread(image_filename)
	image = np.sum(image, axis = 2).T[:, ::-1]
	image = image**3
	w, h = image.shape

	data = np.fft.irfft(image, h*2, axis=1).reshape((w*h*2))
	data -= np.average(data)
	data *= (2**15-1.)/np.amax(data)
	data = array("h", np.int_(data)).tostring()
	image_filename = image_filename.replace("IMG","WAV") + ".wav" #In order to change directory
	output_file = wave.open(image_filename, "w")
	output_file.setparams((1, 2, sampling_freq, 0, "NONE", "not compressed"))
	output_file.writeframes(data)
	output_file.close()
	print ("make_wav_from_img\t{}\tsaved".format(image_filename))
	return image_filename

def wav_overlay(wav_msg_path, original_audio=ORIGINAL_AUDIO_PATH):
	sound1 = AudioSegment.from_wav(original_audio)
	sound2 = AudioSegment.from_wav(wav_msg_path)

	tmpsound = sound1.overlay(sound2) 
	if os.path.exists(wav_msg_path):
  		os.remove(wav_msg_path)

	wav_msg_path = wav_msg_path.replace("WAV", "WAV_OVERLAY")
	#play(tmpsound)
	tmpsound.export(wav_msg_path, format="wav")
	print ("wav_overlay\t{}\tsaved".format((wav_msg_path.split("/"))[-1]))
	return wav_msg_path

def calc_specto(wav_overlay_paths, img_wav_paths=[]):
	#img_wav_specto = []
	wav_overlay_specto = []
	# The wav file must be mono, not stereo
	'''
	#Don't use it in bulk executions, they'r just for demo

	samplingFrequency, signalData = wavfile.read(ORIGINAL_AUDIO_PATH)
	frequencies, times, spectrogram = signal.spectrogram(signalData, samplingFrequency)
	original_audio_specto = {
		"name": (ORIGINAL_AUDIO_PATH.split("/"))[-1],
		"frequencies": frequencies,
		"times":times,
		"spectrogram": spectrogram
	}
	
	for f_n in img_wav_paths:
		samplingFrequency, signalData = wavfile.read(f_n)
		frequencies, times, spectrogram = signal.spectrogram(signalData, samplingFrequency)
		img_wav_specto.append({
				"name": (f_n.split("/"))[-1],
				"frequencies": frequencies,
				"times":times,
				"spectrogram": spectrogram
			})
	'''
	for f_n in wav_overlay_paths:
		samplingFrequency, signalData = wavfile.read(f_n)
		frequencies, times, spectrogram = signal.spectrogram(signalData, samplingFrequency)
		wav_overlay_specto.append({
				"name": (f_n.split("/"))[-1],
				"frequencies": frequencies,
				"times":times,
				"spectrogram": spectrogram
			})

	#return original_audio_specto, img_wav_specto, wav_overlay_specto
	return wav_overlay_specto

def create_save_plot(wav_overlay_specto, original_audio_specto={}, img_wav_specto=[]):

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
	'''
	#Don't use it in bulk executions, they'r just for demo

	axs[0, 1].pcolormesh(wav_overlay_specto[2]["times"], wav_overlay_specto[2]["frequencies"], np.log(wav_overlay_specto[2]["spectrogram"]))
	axs[0, 1].set_title(wav_overlay_specto[2]["name"])
	dim = axs[0, 1].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[2]["name"] + ".png"
	fig.savefig(path, bbox_inches=dim)

	axs[0, 2].pcolormesh(wav_overlay_specto[4]["times"], wav_overlay_specto[4]["frequencies"], np.log(wav_overlay_specto[4]["spectrogram"]))
	axs[0, 2].set_title(wav_overlay_specto[4]["name"])
	dim = axs[0, 2].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[4]["name"] + ".png"
	fig.savefig(path, bbox_inches=dim)

	axs[1, 0].pcolormesh(wav_overlay_specto[1]["times"], wav_overlay_specto[1]["frequencies"], np.log(wav_overlay_specto[1]["spectrogram"]))
	axs[1, 0].set_title(wav_overlay_specto[1]["name"])
	dim = axs[1, 0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[1]["name"] + ".png"
	fig.savefig(path, bbox_inches=dim)

	axs[1, 1].pcolormesh(wav_overlay_specto[3]["times"], wav_overlay_specto[3]["frequencies"], np.log(wav_overlay_specto[3]["spectrogram"]))
	axs[1, 1].set_title(wav_overlay_specto[3]["name"])
	dim = axs[1, 1].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[3]["name"] + ".png"
	fig.savefig(path, bbox_inches=dim)

	axs[1, 2].pcolormesh(wav_overlay_specto[5]["times"], wav_overlay_specto[5]["frequencies"], np.log(wav_overlay_specto[5]["spectrogram"]))
	axs[1, 2].set_title(wav_overlay_specto[5]["name"])
	dim = axs[1, 2].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	path = CURRENT_PATH + DATA_PATH + "IMG_SPECTO/" + wav_overlay_specto[5]["name"] + ".png"
	fig.savefig(path, bbox_inches=dim)
	'''


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
	
	folders_needed = ["IMG", "WAV", "WAV_OVERLAY", "IMG_SPECTO","POST_P_IMG"]
			
	if not os.path.exists(CURRENT_PATH + DATA_PATH[:-1]):
		os.mkdir(CURRENT_PATH + DATA_PATH[:-1])

	for folder in folders_needed:
		if not os.path.exists(CURRENT_PATH + DATA_PATH + folder):
			os.mkdir(CURRENT_PATH + DATA_PATH + folder)

	texts = [
		"My Cup of Tea",
		"Right Out of the Gate",
		"Shot In the Dark",
		"Rain on Your Parade",
		"Dropping Like Flies",
		"No Ifs, Ands, or Buts",
		"Everything But The Kitchen Sink",
		"Quality Time",
		"Tug of War",
		"Jig Is Up"
	]
	fonts = [
		"FreeMono.ttf",
		"FreeMonoBold.ttf",
		"FreeSerif.ttf",
		"FreeSerifBold.ttf",
		"FreeSans.ttf",
		"FreeSansBold.ttf",
	]
	f_dim = [25, 50, 75, 100]
	print("\n\nSTARTING TEXT_ON_IMG\n\n")
	img_paths = [
		text_on_img(filename="{} - {}_{}".format(text[:5], (font.split("."))[0], str(f_d)),text=text, exstension=ext, freq=freq, font_size=f_d, font=font) 
		for text in texts
		for font in fonts
		for f_d in f_dim
		for ext in [".png",".pbm",".jpeg"]
		for freq in ["HF","LF"]
	]
	print("\n\nSTARTING MAKE_WAV_FROM_IMG\n\n")
	img_wav_paths = [make_wav_from_img(img_p) for img_p in img_paths]
	print("\n\nSTARTING WAV_OVERLAY\n\n")
	wav_overlay_paths = [wav_overlay(w_m_path) for w_m_path in img_wav_paths]
	print("\n\nSTARTING CALC_SPECTO\n\n")
	#original_audio_specto, img_wav_specto, wav_overlay_specto = calc_specto(img_wav_paths, wav_overlay_paths)
	wav_overlay_specto = calc_specto(wav_overlay_paths=wav_overlay_paths)

	gc.collect()

	print("\n\nSTARTING CREATE_SAVE_PLOT\n\n")
	create_save_plot(wav_overlay_specto=wav_overlay_specto)
	print("\n\nSTARTING IMAGES_POST_PROCESSING\n\n")
	images_post_processing()
	print("\n\nSTARTING IMAGES_IN_OCR\n\n")
	images_in_ocr()

