import pytest
from mocks import MockPromoRepository


@pytest.fixture
def mock_promo_repository():
    return MockPromoRepository()
