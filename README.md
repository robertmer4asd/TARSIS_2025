## Cum se rulează codul pe Raspberry Pi

### 1. Se descarcă fișierele necesare

Descarcă următoarele fișiere pe Raspberry Pi și salvează-le în directorul proiectului:

- [Coral](link-către-fișierul-Coral)  
- [DIY_Eng_CoralUSB](link-către-fișierul-DIY_Eng_CoralUSB)

---

### 2. Se pornește un mediu virtual Python în `DIY_Eng_CoralUSB` și se instalează dependențele

```bash
# Activează mediul virtual
source venv/bin/activate

# Actualizează pachetele și instalează OpenCV + alte dependențe de bază
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-venv libatlas-base-dev

# Instalează pachetele Python necesare
pip install -r requirements.txt
