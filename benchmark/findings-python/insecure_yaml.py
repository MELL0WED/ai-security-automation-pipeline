import yaml

def load_user_config(raw_config):
    return yaml.load(raw_config, Loader=yaml.UnsafeLoader)
