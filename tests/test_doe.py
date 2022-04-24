import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DOE import DOE

def test_d_optimal():

    doe = DOE.DOE('tests/data/doe_setting.xlsx')
    args = {
        'method':'d_optimal',
        'num_sample':50
        }
    doe.create_table(args)
    doe.table

def test_box_behnken():

    doe = DOE.DOE('tests/data/doe_setting_only_numeric_three.xlsx')
    args = {
        'method':'box_behnken',
        'randomize':True
        }
    doe.create_table(args)
    doe.table

def test_central_composite():

    doe = DOE.DOE('tests/data/doe_setting_only_numeric_three.xlsx')
    args = {
        'method':'central_composite',
        'randomize':True
        }
    doe.create_table(args)
    doe.table

def test_placket_burman():

    doe = DOE.DOE('tests/data/doe_setting_binary_category.xlsx')
    args = {
        'method':'placket_burman',
        'randomize':True
        }
    doe.create_table(args)
    doe.table

def test_full_fact():

    doe = DOE.DOE('tests/data/doe_setting.xlsx')
    args = {
        'method':'full_fact',
        'randomize':True
        }
    doe.create_table(args)
    doe.table

def test_latin_hypercube():

    doe = DOE.DOE('tests/data/doe_setting.xlsx')
    args = {
        'method':'lth',
        'num_samples':100
        }
    doe.create_table(args)
    doe.table