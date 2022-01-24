import requests, os

class hook:
  def __init__(self, description=''):
    self.url = os.environ['hook']
    self.description=description
    
    
  def send(self,content=""):
    description=self.description
    data = {
    "content" : content,
    "username" : "Katrina"
    }

    data["embeds"] = [
        {
            "description" : description,
            "title" : " "
        }
    ]
    result = requests.post(self.url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))


def create_hook(description):
  return hook(description=description)

"""
h = hook()
h.send(description=f"Command failed!\n{error}") 
"""