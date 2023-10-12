# images-research

### Description

Data collection and analysis pipeline for container security research.
### Usage

**Setup**

Install dependencies
```
./install_deps.sh
```

Setup python virtual environment
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

**Run script method**
Use run_all.sh to run all stages automatically. Output will be stored in a directory called `data`.
```
./run_all.sh
```

**Manually run each stage**
Run each stage manually. You will have to create the data directory yourself.
```
mkdir data
mkdir data/reports
python scripts/1_scan_images.py -r data/reports
mkdir data/datasets
python scripts/2_build_datasets.py -r data/reports -o data/datasets
```


