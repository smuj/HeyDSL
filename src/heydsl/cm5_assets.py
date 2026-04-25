from .asset import AssetType, ExternalAsset

CM5_BASE_URL = "https://cdnjs.cloudflare.com/ajax/libs/codemirror"
CM5_VERSION = "5.65.20"


def make_cm5_asset(
    asset_type: AssetType,
    name: str,
    integrity: str | None = None,
    subdir: str | None = None,
) -> ExternalAsset:
    """Helper function to create a CodeMirror 5 asset."""
    extension = "css" if asset_type == AssetType.STYLESHEET else "js"
    url = "/".join(
        [CM5_BASE_URL, CM5_VERSION]
        + ([f"{subdir}"] if subdir else [])
        + [
            f"{name}.min.{extension}",
        ]
    )
    return ExternalAsset(type=asset_type, url=url, integrity=integrity)


def default_cm5_assets() -> list[ExternalAsset]:
    """Return the default CodeMirror 5 assets."""
    return [
        make_cm5_asset(
            AssetType.STYLESHEET,
            "codemirror",
            "sha512-uf06llspW44/LZpHzHT6qBOIVODjWtv4MxCricRxkzvopAlSWnTf6hpZTFxuuZcuNE9CBQhqE0Seu1CoRk84nQ==",
        ),
        make_cm5_asset(
            AssetType.SCRIPT,
            "codemirror",
            "sha512-hJEMjfR4ds7mXbBot3i/R+CsiyYpeWSezXul8uLBT8wXAHPUdhRgl4LLTtMGwjarftGKiQqK1v20XScm0ANTPQ==",
        ),
        make_cm5_asset(
            AssetType.SCRIPT,
            "simple",
            "sha512-CGM6DWPHs250F/m90YZ9NEiEUhd9a4+u8wAzeKC6uHzZbYyt9/e2dLC5BGGB6Y0HtEdZQdSDYjDsoTyNGdMrMA==",
            "addon/mode",
        ),
    ]


def curated_cm5_themes() -> dict[str, ExternalAsset]:
    """Return a curated list of popular CodeMirror 5 themes."""
    themes = {
        name: make_cm5_asset(AssetType.STYLESHEET, name, integrity, subdir="theme")
        for name, integrity in [
            (
                "cobalt",
                "sha512-dAYwzcmdv0GvCo9UJmVP430Mc9kmvpdDVk/pHNG90qTZR6tpHQlR9BsVdK9ZGpnNtQNVl+j7UQppCwOPN0TTNQ==",
            ),
            (
                "dracula",
                "sha512-gFMl3u9d0xt3WR8ZeW05MWm3yZ+ZfgsBVXLSOiFz2xeVrZ8Neg0+V1kkRIo9LikyA/T9HuS91kDfc2XWse0K0A==",
            ),
            (
                "eclipse",
                "sha512-Gv0sGKOVrQcQjUHL+xd9Bpq5AvLKbcQMb8s4J1//caCLxqvj00CLJMzJlqnTHTCQbKFRpPHqzXteq6dSMs7PEw==",
            ),
            (
                "material",
                "sha512-jA21084nir3cN96YuzJ1DbtDn30kxhxqQToAzCEGZcuRAswWfYirpUu8HVm8wRNoWDCYtA4iavd2Rb1bQSLv7g==",
            ),
            (
                "monokai",
                "sha512-R6PH4vSzF2Yxjdvb2p2FA06yWul+U0PDDav4b/od/oXf9Iw37zl10plvwOXelrjV2Ai7Eo3vyHeyFUjhXdBCVQ==",
            ),
            (
                "solarized",
                "sha512-/fyHOMgAeLm/HB9+Z0TYk1kDPdEfFDhgw68SHIyok5rW/TGTdOOVPeR3N51bkUpjr2ycg2j9/18g7qsbtLW+ig==",
            ),
        ]
    }
    return themes
