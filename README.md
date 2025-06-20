# A cloud info API for fedcloud

This is a FastAPI application that provides some of the information available in
the AppDB IS.

## Running the application

The application will read site information from a directory where the jsons
should be available. It will also watch for changes in those files to update the
info about the sites.

It also uses the
[Operations Portal API](https://gitlab.in2p3.fr/opsportal/sf3/-/wikis/API-documentation)
to fetch the list of VOs.

Both can be configured via env variables, that can be set on the command line:

```sh
CLOUD_INFO_DIR="<directory>" OPS_PORTAL_TOKEN="<XXXX>" uv run fastapi dev --app app
```

### Disabling validity check

By default the application will check if the Glue objects with the site
information are still valid according to the `CreationTime` and `Validity` of
these objects. This check can be disabled with the `CHECK_GLUE_VALIDITY`
environment variable set to `False`:

```sh
CHECK_GLUE_VALIDITY=False uv run fastapi dev --app app
```
