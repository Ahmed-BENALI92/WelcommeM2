Les étapes à faire pour config le back(windows)
0. Aller au dossier api_py
cd api_py 
1. Créer le vm python
python -m venv env
2. Activer le vm env\Scripts\activate
3. installer flask et autre libs 
pip install flask python-dotenv
pip install pandas
pip install folium
pip install matplotlib
4. Lancer le projet
flask run