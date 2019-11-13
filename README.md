Export your personal [Hypothes.is](https://hypothes.is) data: annotations and profile information.

# Setting up
1. `git clone --recursive https://github.com/karlicoss/hypexport`
2. Follow [these](https://hypothes.is/account/developer) instructions to set up the token. You'll also need your username to access the API.
4. It might be convenient to dump it in a file, e.g. `secrets.py`:
```
username = ...
token = ...
```

# Using
**Recommended**: `./export --secrets /path/to/secrets.py`. That way you have to type less and have control over where you're keeping your plaintext tokens/passwords.

Alternatively, you can pass auth arguments directly, e.g. `./export --username <user> --token <token>`.
However, this is prone to leaking your keys/tokens in shell history.

You can also import script and call `get_json` function directory to get raw json.
