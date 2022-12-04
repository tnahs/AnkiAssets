# AnkiAssets

Load global CSS and JavaScript files for your cards!

## Installation

Download and run `bundle/AnkiAssets.ankiaddon`.

## Usage

1. Place CSS and JavaScript files into their respective directories within the
  add-on's `user_files` directory. CSS files go into `user_files/assets/
  css` and JavaScript into `user_files/assets/javascript`.  For example,
  the following shows the final structure of the add-on's directory when a
  `card.css`, `_normalize.css` and `card.js` are added.

    ```plaintext
    addons21/AnkiAssets
    ├── src/
    └── user_files
        ├── assets.json
        └── assets
            ├── css
            │   ├── _normalize.css
            │   └── card.css  <-- Here!
            └── javascript
                └── card.js  <-- And here!
    ```

> Note that files starting with underscores `_` or periods `.` are ignored. This
> allows for the use of CSS-style importing e.g. `@import "_normalize.css";`

2. Run Anki and go to `Tools` > `AnkiAssets Preferences...` to enable/disable
the assets you want loaded for every card.

```plaintext
┌────────────────────────────────┐
│     AnkiAssets Preferences     │
├────────────────────────────────┤
│   CSS:                         │
│ ┌────────────────────────────┐ │
│ │  █ card.css                │ │
│ └────────────────────────────┘ │
│   JavaScript:                  │
│ ┌────────────────────────────┐ │
│ │  █ card.js                 │ │
│ └────────────────────────────┘ │
│ ┌───────┐     ┌──────────────┐ │
│ └───────┘     └──────────────┘ │
└────────────────────────────────┘
```

<!-- TODO: Does this hot-reload? -->

## Development

1. Install the required `[python-version]`. See the [Anki development][anki-dev]
   docs for more information.

    ```shell
    pyenv install [python-version]
    ```

2. Set `[python-version]` as the local version:

    ```shell
    cd ./AnkiAssets
    pyenv local [python-version]
    ```

3. Create and enter a virtual environment:

    ```shell
    python -m venv .venv
    pip install --upgrade pip
    source .venv/bin/activate
    ```

4. Install required packages:

    ```shell
    pip install -r requirements.txt
    ```

5. Set development environment variables. See
   [Anki development | Environment Variables][env-var] for more information

    ```shell
    export ANKIDEV=1
    export LOGTERM=1
    export DISABLE_QT5_COMPAT=1
    export ANKI_ADDON_DEVELOPMENT=1
    ```

[anki-dev]: https://github.com/ankitects/anki/blob/main/docs/development.md
[env-var]: https://github.com/ankitects/anki/blob/main/docs/development.md#environmental-variables
