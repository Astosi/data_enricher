from components.cacher import LeiLookupCache


def test_cache():
    # Create a cache with a limit of 3 items
    cache = LeiLookupCache(cache_size=3)

    # Add three items to the cache
    for i in range(1, 4):
        cache.add(f"key{i}", f"value{i}")
        assert cache.get(f"key{i}") == f"value{i}"

    # Add another item, which should remove the first item (key1)
    cache.add("key4", "value4")

    assert cache.get("key4") == "value4"
    assert cache.get("key1") is None
