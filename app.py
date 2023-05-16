import os
from typing import Optional
from flask import Flask, jsonify, request

from famapy.metamodels.fm_metamodel.models import FeatureModel
from famapy.metamodels.fm_metamodel.transformations import UVLReader, FeatureIDEReader

from fm_characterization import FMCharacterization

app = Flask(__name__)
app.config['API_BASE_URL'] = '/api/v1'

def read_fm_file(filename: str) -> Optional[FeatureModel]:
    try:
        if filename.endswith(".uvl"):
            return UVLReader(filename).transform()
        elif filename.endswith(".xml") or filename.endswith(".fide"):
            return FeatureIDEReader(filename).transform()
    except:
        pass
    try:
        return UVLReader(filename).transform()
    except:
        pass
    try:
        return FeatureIDEReader(filename).transform()
    except:
        pass
    return None

@app.route("/", methods=['GET'])
def home():
    return jsonify(data='Hello World!'), 200

@app.route(app.config['API_BASE_URL'] + "/generate", methods=['POST'])
def index():

    data = {}

    if not 'fm_file' in request.files:
        return jsonify(error='Please upload a feature model (fm_file)'), 400

    if not 'fm_name' in request.form:
        return jsonify(error='Please give a feature model name (fm_name)'), 400

    if len(request.form['fm_name']) == 0:
        return jsonify(error='Feature model name is empty (fm_name)'), 400


    fm_file = request.files['fm_file']
    fm_name = request.form['fm_name']

    name = None
    description = None
    author = None
    year = None
    keywords = None
    reference = None
    domain = None

    if fm_file:
        filename = fm_file.filename
        fm_file.save(filename)
    
    name = fm_name

    description = request.form.get('description', '').replace(os.linesep, ' ')
    author = request.form.get('author', '')
    reference = request.form.get('reference', '')
    keywords = request.form.get('keywords', '')
    domain = request.form.get('domain', '')
    year = request.form.get('year', '')

    try:
        # Read the feature model
        fm = read_fm_file(filename)
        if fm is None:
            return jsonify(error='Feature model format not supported'), 400
        if not name:
            name = os.path.splitext(os.path.basename(filename))[0]

        characterization = FMCharacterization(fm)
        characterization.metadata.name = name
        characterization.metadata.description = description
        characterization.metadata.author = author
        characterization.metadata.year = year
        characterization.metadata.tags = keywords
        characterization.metadata.reference = reference
        characterization.metadata.domains = domain

        json_characterization = characterization.to_json()
        json_str_characterization = characterization.to_json_str()
        str_characterization = str(characterization)
        data['fm_facts'] = json_characterization
        
        data['fm_characterization_json_str'] = json_str_characterization
        data['fm_characterization_str'] = str_characterization

    except Exception as e:
        data = None
        print(e)
        raise e

    if os.path.exists(filename) and filename == fm_file.filename:
        os.remove(filename)

    return jsonify(data), 200

if __name__ == '__main__':
    app.run()