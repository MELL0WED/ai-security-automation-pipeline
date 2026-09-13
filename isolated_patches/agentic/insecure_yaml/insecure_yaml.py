import yaml

def load_user_config(raw_config):
    return yaml.safe_load(raw_config)
