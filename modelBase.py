from enum import Enum
from log import log
from data import CliNode, CliData

# suggetion result
class Suggestion:
  def __init__(self, cliNode: CliNode, score):
    self.cliNode = cliNode
    self.score = score

  def mapSuggestionToRes(self):
    return {
      "id": self.cliNode.id,
      "score": self.score,
      "str": self.cliNode.help
    }

  def __str__(self):
    return (self.cliNode.id, self.cliNode.help, self.score).__str__()

  def __repr__(self):
    return (self.cliNode.__repr__(), self.score).__str__()

def mapSuggestionToRes(suggestion: Suggestion):
  return suggestion.mapSuggestionToRes()

# Nlp Processed Cli Node
class NlpCliNode:
  def __init__(self, cliNode, nlpQueries):
    self.cliNode = cliNode
    self.nlpQueries = nlpQueries

  def compare(self, nlpQuery):
    scores = map(nlpQuery.similarity, self.nlpQueries)
    maxScore = max(scores)
    return round(float(maxScore), 4)

class CliNlpModel:
  def __init__(self, id: str, getQueriesFromCliNode, cliData: CliData, nlpModel, rewriteQuery = None, scoreThreshold = 0.5):
    self.id = id
    self._cliData = cliData
    self._nlp = nlpModel
    self.scoreThreshold = scoreThreshold
    self._getQueriesFromCliNode = getQueriesFromCliNode

    if rewriteQuery is not None:
      self.rewriteQuery = rewriteQuery
    else:
      self.rewriteQuery = lambda query: query

    op = log().start("processing data with model: " + self.id)
    self.nlpNodes = list(map(self._getNlpCliNode, cliData.getAllNodes()))
    op.end("done")

  def _getNlpQuery(self, query):
    rewrittenQuery = self.rewriteQuery(query)
    nlpQuery = self._nlp(rewrittenQuery)
    return nlpQuery

  def _getNlpCliNode(self, cliNode: CliNode) -> NlpCliNode:
    queries = self._getQueriesFromCliNode(cliNode)
    nlpQueries = list(map(self._getNlpQuery, queries))
    return NlpCliNode(cliNode, nlpQueries)

  def getSuggestions(self, queryStr, top = 100):
    nlpQuery = self._getNlpQuery(queryStr)
    scoredNodes = list(map(lambda nlpCliNode: Suggestion(nlpCliNode.cliNode, nlpCliNode.compare(nlpQuery)), self.nlpNodes))
    matches = filter(lambda scoredNode: scoredNode.score > self.scoreThreshold, scoredNodes)
    sortedMatches = sorted(matches, key=lambda suggestion: suggestion.score, reverse=True)
    return sortedMatches[:top]

  def getLegacyResult(self, queryStr, top = 10):
    suggestions = self.getSuggestions(queryStr, top)
    result = list(map(mapSuggestionToRes, suggestions))
    return result
