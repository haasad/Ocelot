# -*- coding: utf-8 -*-
from ocelot.io.extract_ecospold2 import generic_extractor
from ocelot.io.validate_internal import dataset_schema
from ocelot.transformations.cutoff.allocation import choose_allocation_method
from ocelot.transformations.cutoff.economic import economic_allocation
import pytest
import os


### Test artificial cases

@pytest.fixture(scope="function")
def no_allocation(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.cutoff.economic.apply_allocation_factors',
        lambda x, y: (x, y)
    )

def test_economic_allocation_outputs(no_allocation):
    dataset = {
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
            'amount': 2,
            'properties': [{
                'name': 'price',
                'amount': 14
            }]
        }]
    }
    expected = {
        'type': 'reference product',
        'name': 'foo',
        'amount': 2,
        'properties': [{
            'name': 'price',
            'amount': 14
        }]
    }
    obj, lst = economic_allocation(dataset)
    assert obj is dataset
    assert list(lst) == [(1, expected)]

def test_allocation_factors(no_allocation):
    dataset = {'exchanges': [{
        'name': 'first',
        'type': 'reference product',
        'amount': 4,
        'properties': [{
            'name': 'price',
            'amount': 2.5
        }]
    }, {
        'name': 'second',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 2
        }]
    }, {
        'name': 'third',
        'type': 'biosphere',
        'amount': 30
    }]}
    obj, lst = economic_allocation(dataset)
    # Allocation by revenue; revenue is (4 * 2.5 = 10, 2 * 10 = 20) = (1/3, 2/3)
    assert [x[0] for x in lst] == [1/3, 2/3]

def test_normal_economic_allocation():
    dataset = {'exchanges': [{
        'name': 'first',
        'type': 'reference product',
        'amount': 4,
        'properties': [{
            'name': 'price',
            'amount': 2.5
        }]
    }, {
        'name': 'second',
        'type': 'reference product',
        'amount': 10,
        'properties': [{
            'name': 'price',
            'amount': 2
        }]
    }, {
        'name': 'third',
        'type': 'biosphere',
        'amount': 60
    }]}
    # Allocation by revenue; revenue is (4 * 2.5 = 10, 2 * 10 = 20) = (1/3, 2/3)
    # So biosphere amount is (20, 40)
    # Normalize to production of 1: 20 / 4, 40 / 10 = (5, 4)
    expected = [{
        'exchanges': [{
            'amount': 1.0,
            'name': 'first',
            'type': 'reference product',
            'uncertainty': {
                'maximum': 1.0,
                'minimum': 1.0,
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'type': 'undefined',
            },
            'properties': [{
                'name': 'price',
                'amount': 2.5}]
        }, {
            'amount': 0.0,
            'name': 'second',
            'type': 'dropped product',
            'properties': [{
                'name': 'price',
                'amount': 2
            }]
        }, {
            'amount': 5,
            'name': 'third',
            'type': 'biosphere',
        }]
    }, {
        'exchanges': [{
            'amount': 1.0,
            'name': 'second',
            'type': 'reference product',
            'uncertainty': {
                'type': 'undefined',
                'pedigree matrix': {},
                'standard deviation 95%': 0,
                'maximum': 1.0,
                'minimum': 1.0,
            },
            'properties': [{
                'name': 'price',
                'amount': 2
            }]
        }, {
            'type': 'dropped product',
            'amount': 0.0,
            'name': 'first',
            'properties': [{
                'name': 'price',
                'amount': 2.5
            }]
        }, {
            'type': 'biosphere',
            'name': 'third',
            'amount': 4
        }]
    }]
    assert economic_allocation(dataset) == expected

# TODO: Find out expected behaviour here... right now it will work as you think
# But maybe this is not desired.

def test_economic_allocation_negative_price():
    pass

def test_economic_allocation_negative_amount():
    pass

def test_economic_allocation_zero_amount():
    pass

def test_economic_allocation_zero_price():
    pass


### Test real test data

@pytest.fixture(scope="module")
def cardboard():
    fp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "corrugated-board.spold")
    return generic_extractor(fp)[0]

def test_load_validate_cardboard_dataset(cardboard):
    assert dataset_schema(cardboard)

def test_choice_allocation_method(cardboard):
    assert choose_allocation_method(cardboard) == economic_allocation

def test_allocation_function_output_valid(cardboard):
    for new_ds in economic_allocation(cardboard):
        assert dataset_schema(new_ds)
