from Levenshtein import *

phrases={ #cutted as file names [:5]
    "My Cu" : "My Cup of Tea",
    "Right" : "Right Out of the Gate",
    "Shot " : "Shot In the Dark",
    "Rain " : "Rain on Your Parade",
    "Dropp" : "Dropping Like Flies",
    "No If" : "No Ifs, Ands, or Buts",
    "Every" : "Everything But The Kitchen Sink",
    "Quali" : "Quality Time",
    "Tug o" : "Tug of War",
    "Jig I" : "Jig Is Up"
}


fh = open('attack_flatten_cmd_result.txt')
#Normal flatten file 
''' 
for line in fh:
    #print(line)
    phrase = phrases[(line.replace("- IMG: ","").split(" - "))[0]].upper()
    ocr = (line.split("- OCR_TEXT: "))[1]
    ocr = ocr[:-1] if "\n" in ocr else ocr
    l_ratio = ratio(ocr,phrase)
    data= (line.split(" - "))[1].replace(".","_")
    font = (data.split("_"))[0]
    dim = (data.split("_"))[1]
    freq = (data.split("_"))[2]
    ext = (data.split("_"))[3]
    print("{};{};{};{};{};{};{}".format(phrase, ocr, l_ratio, font, dim, freq, ext))
fh.close()
'''
#Attack flatten file 
for line in fh:
    #print(line)
    phrase = phrases[(line.replace("- IMG: ","").split(" - "))[0]].upper()
    ocr = (line.split("- OCR_TEXT: "))[1]
    ocr = ocr[:-1] if "\n" in ocr else ocr
    l_ratio = ratio(ocr,phrase)
    data= (line.split(" - "))[1].replace(".","_")
    font = (data.split("_"))[0]
    dim = (data.split("_"))[1]
    freq = (data.split("_"))[2]
    edit = (data.split("_"))[4] if (data.split("_"))[4] != "wav" else (data.split("_"))[5]
    print("{};{};{};{};{};{};{}".format(phrase, ocr, l_ratio, font, dim, freq, edit))
fh.close()