import pytest
from tests.mocks.subscriptions_handler_mock import SubscriptionsHandler
from tests.mocks.kleinzengen_filter_mock import KleinzengenFilter

def test_subscription_handler_initialization():
    handler = SubscriptionsHandler()
    assert handler is not None
    assert hasattr(handler, 'subscriptions')
    assert isinstance(handler.subscriptions, list)

def test_subscription_add_and_remove():
    handler = SubscriptionsHandler()
    filter_obj = KleinzengenFilter()
    
    # Test adding subscription
    handler.add_subscription(filter_obj)
    assert len(handler.subscriptions) == 1
    assert handler.subscriptions[0] == filter_obj
    
    # Test removing subscription
    handler.remove_subscription(0)
    assert len(handler.subscriptions) == 0

def test_subscription_list_filters():
    handler = SubscriptionsHandler()
    filter_obj = KleinzengenFilter()
    filter_obj.brands = ["BMW"]
    filter_obj.min_price = 10000
    
    handler.add_subscription(filter_obj)
    filters = handler.list_subscriptions()
    assert len(filters) > 0
    assert isinstance(filters[0], KleinzengenFilter)
