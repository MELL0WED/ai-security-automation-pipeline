import importlib

def load_plugin(plugin_name):
    # plugin_name comes from a trusted internal config file, not user input
    module = importlib.import_module(f"plugins.{plugin_name}")
    return module.run()
