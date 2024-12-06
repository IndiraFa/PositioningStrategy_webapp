Positioning Strategy - Mangetamain

The Mangetamain company asked us to study the relevance of a repositioning towards a site dedicated to nutrition, health and fitness.
We published our analysis of its database in the form of a webapp. 

Direct link to the public app : https://positioningstrategy-mangetamain-stable.streamlit.app 

# How setup environment
1. create virtual environment
```python
python -m venv .venv
```

2. activate virtual environment
- on linux/MacOs
```bash
source .venv/bin/activate
```

-   on windows
``` powershell
.venv\Scripts\activate.bat
```

3. install dependancies
```python
python -m pip install -r requirements.txt
```

# Run Program
```python
PYTHONPATH=src streamlit run src/Homepage.py
```

# Documentation sphinx
```bash
cd docs
make html
xdg-open build/html/index.html
```


