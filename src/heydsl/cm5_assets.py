from .asset import AssetType, ExternalAsset


def default_cm5_assets() -> list[ExternalAsset]:
    """Return the default CodeMirror 5 assets."""
    assets = [
        ExternalAsset(
            type=AssetType.STYLESHEET,
            url="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/codemirror.min.css",
            integrity="sha512-uf06llspW44/LZpHzHT6qBOIVODjWtv4MxCricRxkzvopAlSWnTf6hpZTFxuuZcuNE9CBQhqE0Seu1CoRk84nQ==",
        ),
        ExternalAsset(
            type=AssetType.SCRIPT,
            url="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.20/codemirror.min.js",
            integrity="sha512-hJEMjfR4ds7mXbBot3i/R+CsiyYpeWSezXul8uLBT8wXAHPUdhRgl4LLTtMGwjarftGKiQqK1v20XScm0ANTPQ==",
        ),
    ]
    return assets
