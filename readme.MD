# Azure Fastapi Loader Template

**REQUIRES: `>=Python 3.9`**

* Load into vscode with Azure Functions Plugin
* Press `F5` to launch and debug.
* Change/Add API functionality in `src/api`
    * To create a new API, just duplucate the sample api, the loader will automatically bootstrap it on start.
* To change the name and description, modify `app/init.py`

### Configuration
* Configuration can be found in `config.py`
* The precedence of looking for configuration values follows `.env -> environment_variables -> default value`
* You can ensure that the required configuration strings has been loaded by specifying a value as `internal.UNSET` and calling `cfg.has_unset()` 