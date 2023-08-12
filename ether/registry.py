class ContentTypesRegistry:
    """
    Class for keeping a register of discovered content types.
    """
    _registry: dict[str, any] = {}

    def register(self, api_id: str, contenttype: any):
        """
        Register a content type instance under an API ID.
        """
        self._registry[api_id] = contenttype

    def get(self, api_id: str):
        """
        Returns the content type instance for a given API ID.
        """
        return self._registry.get(api_id, None)

    def entries(self):
        """
        Returns the entire registry.
        """
        return self._registry.items()

    def __len__(self):
        return len(self._registry)


# Create a default registry
registry = ContentTypesRegistry()
