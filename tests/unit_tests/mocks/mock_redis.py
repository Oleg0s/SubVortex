from typing import List
from unittest.mock import AsyncMock


def mock_get_selection(hoktkey: str, selection: List[int] = None):
    # Mock the redis instance
    mocked_redis = AsyncMock()

    # Set the return value for redis.get
    selection_key = f"selection:{hoktkey}"
    selection_value = ", ".join(map(str, selection)).encode() if selection else None
    mocked_redis.get = AsyncMock(
        side_effect=lambda key: (selection_value if key == selection_key else None)
    )

    return mocked_redis
