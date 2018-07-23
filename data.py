import json
from typing import List


def createCliNodeFromJsonNode(jsonNode):
  command = jsonNode[0]
  help = jsonNode[1]["help"]
  # if help is not None:
  #   help = help.split('.')[0]
  group = jsonNode[1]["group"]
  params = jsonNode[1].get("parameters", None)

  if params is not None:
    cliType = "command"
  else:
    cliType = "group"

  # create initial queries
  queries = list(filter(None, [command, help]))

  return CliNode(command, group, help, cliType, queries)

class CliNode:
  def __init__(self, id, group, help, cliType, queries: List[str]):
    self.id = id
    self.group = group
    self.help = help
    self.cliType = cliType
    self.queries = queries

  def getQueries(self) -> List[str]:
    return self.queries

  def __str__(self):
    return (self.id, self.cliType, self.help).__str__()

  def __repr__(self):
    return self.__str__()

class CliData:
  def __init__(self, dataJson):
    self._dataJson = dataJson
    self._nodes = list(map(createCliNodeFromJsonNode, self._dataJson.items()))
    self._commandNodes = list(filter(lambda n: n.cliType == "command", self._nodes))

  def getAllNodes(self):
    return self._nodes

  def getCommandNodes(self):
    return self._commandNodes

  @classmethod
  def loadFromJson(cls, filepath: str) -> CliData:
    with open (filepath) as f:
      data = json.load(f)

    return cls(data)

# export
cliData = CliData.loadFromJson('data/help_dump_with_top_group.json')
data_partial = CliData.loadFromJson('data/help_dump_with_top_group_partial.json')
data_sm = CliData.loadFromJson('data/help_dump_small_with_top_group.json')
