

Export/takeout for your personal [Hypothes.is](https://hypothes.is) data: annotations and profile information.

<!-- Keep this separator: Quarto otherwise moves the generated preamble below the following heading. -->

# Setting up

1.  install with PIP
    - `pip3 install --user git+https://github.com/karlicoss/hypexport`

    - for export functionality: append `[export]`

    - for optional extras for logging and faster json processing: append `[optional]`

    - or any combination of the above, e.g. `[export,optional]`

    - alternatively, clone the repository and run `pip3 install --editable .`.
2.  Follow [these](https://hypothes.is/account/developer) instructions to set up the token

# Exporting

Usage:

**Recommended**: create `secrets.py` keeping your API parameters, e.g.:

    username = "USERNAME"
    token = "TOKEN"

After that, use:

    python3 -m hypexport.export --secrets /path/to/secrets.py

That way you type less and have control over where you keep your plaintext secrets.

**Alternatively**, you can pass parameters directly, e.g.

    python3 -m hypexport.export --username <username> --token <token>

However, this is verbose and prone to leaking your keys/tokens/passwords in shell history.

You can also import `hypexport.export` as a module and call `get_json` function directly to get raw JSON.

I **highly** recommend checking exported files at least once just to make sure they contain everything you expect from your export.
If they don’t, please feel free to ask or raise an issue!

<!-- TODO FIXME api limitations 10000 annotations? -->

# Updating README

This README is generated from a ‘literate’ Quarto [README.qmd](README.qmd) via the following command:

`tox -e quarto`

If you want to correct something, feel free to simply update `README.md` though, I can reconcile the changes next time I regenerate it.
