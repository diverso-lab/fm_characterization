import argparse

from famapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader

from fm_characterization.models.fm_characterization import FMCharacterization


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Characterization of feature models.')
    parser.add_argument('feature_model', type=str, help='Feature model.')
    args = parser.parse_args()


    fm = FeatureIDEReader(args.feature_model).transform() 
    fm_characterization = FMCharacterization(fm)

    print(f'METRICS')
    for property, value in fm_characterization.metrics.items():
        print(f'  {property.value}: {value}')
    
    print(f'ANALYSIS')
    for property, value in fm_characterization.analysis.items():
        print(f'  {property.value}: {value}')