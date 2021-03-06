from ocelot.errors import UnresolvableActivityLink, OverlappingMarkets
from ocelot.transformations.locations.linking import (add_reference_product_codes,
    actualize_activity_links,
    link_consumers_to_global_markets,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_regional_markets,
    log_and_delete_unlinked_exchanges,
)
import pytest


def test_add_reference_product_codes():
    given = [{
        'code': 'foo',
        'exchanges': [{
            'type': 'reference product',
        }, {
            'type': 'not reference product'
        }]
    }]
    expected = [{
        'code': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'code': 'foo'
        }, {
            'type': 'not reference product'
        }]
    }]
    assert add_reference_product_codes(given) == expected

def test_add_reference_product_codes_error():
    given = [{'name': ''}]
    with pytest.raises(AssertionError):
        add_reference_product_codes(given)

def test_actualize_activity_links():
    given = [{
        'code': 'find me',
        'id': 'the right one',
        'name': '',
        'location': '',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
        }]
    }]
    expected = [{
        'code': 'find me',
        'id': 'the right one',
        'name': '',
        'location': '',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'code': 'find me',
            'name': 'foo',
        }]
    }]
    assert actualize_activity_links(given) == expected

def test_actualize_activity_links_errors():
    too_many = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
            'amount': 1,
        }]
    }]
    # with pytest.raises(UnresolvableActivityLink):
    #     actualize_activity_links(too_many)
    actualize_activity_links(too_many)

    too_few = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
            'amount': 1,
        }]
    }]
    # with pytest.raises(UnresolvableActivityLink):
    #     actualize_activity_links(too_few)
    actualize_activity_links(too_few)

def test_link_consumers_to_regional_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'reference product': 'sandwiches',
        'name': '',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    expected = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'reference product': 'sandwiches',
        'name': '',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'olympics',
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'Made in the EU',
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    assert link_consumers_to_regional_markets(given) == expected

def test_link_consumers_to_regional_markets_no_market():
    missing = [{
        'type': 'market activity',
        'reference product': 'granola',
        'name': '',
        'location': 'UCTE without Germany',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'FR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    link_consumers_to_regional_markets(missing)

def test_link_consumers_to_regional_markets_overlapping_markets():
    error = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'UCTE without Germany',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'FR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    with pytest.raises(OverlappingMarkets):
        link_consumers_to_regional_markets(error)

def test_link_consumers_to_global_markets_no_link():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_global_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert 'code' not in result[2]['exchanges'][0]

def test_link_consumers_to_global_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'GLO',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_global_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert result[2]['exchanges'][0]['code'] == 'yes!'

def test_link_consumers_to_global_markets_use_row():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RoW',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_global_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert result[2]['exchanges'][0]['code'] == 'yes!'

def test_log_and_delete_unlinked_exchanges_logged():
    error = [{
        'type': 'market activity',
        'reference product': 'nope',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    # TODO: Check if message written to log
    log_and_delete_unlinked_exchanges(error)

def test_log_and_delete_unlinked_exchanges_deletion():
    error = [{
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    expected = [{
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': []
    }]
    assert log_and_delete_unlinked_exchanges(error) == expected

def test_link_consumers_to_recycled_content_activities():
    given = [{
        'type': 'transforming activity',
        'reference product': 'cheese, Recycled Content cut-off',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese, Recycled Content cut-off'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert result[1]['exchanges'][0]['code'] == 'found it'

def test_link_consumers_to_recycled_content_activities_not_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese, Recycled Content cut-off',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese, Recycled Content cut-off'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert 'code' not in result[1]['exchanges'][0]

def test_link_consumers_to_recycled_content_activities_wrong_name():
    given = [{
        'type': 'transforming activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert 'code' not in result[1]['exchanges'][0]
