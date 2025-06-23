## Cum se rulează codul de procesare video pe Raspberry Pi 4

### 1. Se descarcă fișierele necesare

Descarcă următoarele fișiere pe Raspberry Pi și salvează-le în directorul proiectului:

- [Coral](link-către-fișierul-Coral)  
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
