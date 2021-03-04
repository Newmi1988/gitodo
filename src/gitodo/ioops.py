from datetime import datetime
from pathlib import Path

import yaml

TODO_LIST = {}

test = {"a" : datetime.now()}

with open(Path('.') / 'test.yaml', 'w') as file:

    yaml.dump(
        data = test,
        stream= file
    )


