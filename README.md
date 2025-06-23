## Cum se rulează codul de procesare video pe Raspberry Pi 4

### 1. Se descarcă fișierele necesare

Descarcă următoarele fișiere pe Raspberry Pi și salvează-le în directorul proiectului:

- [Coral](https://drive.google.com/drive/folders/1Jbkt2JSXDiCUp5Vs72evr1BS8fMRHmli?usp=sharing)  
- [DIY_Eng_CoralUSB](link-către-fișierul-DIY_Eng_CoralUSB)

---

### 2. Se pornește un mediu virtual Python în `DIY_Eng_CoralUSB` și se instalează dependențele

```bash
# Activează mediul virtual
source DIY_Eng_CoralUSB/bin/activate

# Actualizează pachetele și instalează OpenCV + alte dependențe de bază
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-venv libatlas-base-dev

# Instalează pachetele Python necesare
pip install -r requirements.txt
```
### 3. Rulează codul 'track_new.py'
```bash
#Accesează folderul unde se află fișierul
cd Coral/pycoral/examples-camera/opencv

#Rulează codul
python3 track_new.py
```
## Cum se rulează codul de procesare vocală pe Raspberry Pi 4

### 1. Se instalează bibliotecile
```bash
pip install -r requirements2.txt
```
### 3. Descarcă codul

- [Cod](https://drive.google.com/file/d/1kPmNCeyMhF8Uo8P_SFTZ-9kkk-0bmuaZ/view?usp=sharing)

### 2. Rulează codul
```bash
python3 vocal.py
```
