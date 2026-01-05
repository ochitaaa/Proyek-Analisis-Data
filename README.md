## 🌍 Beijing Air Quality

Dashboard interaktif untuk analisis kualitas udara di Beijing (2013–2017) menggunakan Streamlit.

### Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

### Run steamlit app
```bash
streamlit run dashboard.py
```