import socket
import json

data = ["Voc\u00ea: Pedro 1", "Voc\u00ea: Pedro 2", "Voc\u00ea: Ol\u00e1", "Voc\u00ea: Pedro 1", "Voc\u00ea: ol\u00e1", "Voc\u00ea: Pedro", "Pedro: lucas 1", "Pedro: Lucas 2", "Pedro: ol\u00e1"]


data = json.dumps(data)

data = data.encode("utf-8")

data = data.decode('utf-8')

data = json.loads(data)

print(data)
