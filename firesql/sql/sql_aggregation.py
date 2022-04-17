import sys
from typing import Dict, List

class FireSQLAggregate():

  def __init__(self):
    self.aggregationLookup = {
      'count': self.count,
      'sum': self.sum,
      'avg': self.avg,
      'min': self.min,
      'max': self.max,
    }

  @classmethod
  def fieldName(cls, func, column):
    fieldName = '{}({})'.format(func, column)
    return fieldName

  @classmethod
  def hasAggregation(cls, aggregationFields: Dict) -> bool:
    for part in aggregationFields.keys():
      if aggregationFields[part]:
        return True
    return False

  def aggregation(self, aggregationFields: Dict, documents: Dict) -> List:
    if FireSQLAggregate.hasAggregation(aggregationFields):
      adoc = {}
      for part in aggregationFields.keys():
        if aggregationFields[part]:
          for func, column in aggregationFields[part]:
            aggregationFunc = self.aggregationLookup[func]
            fieldName = FireSQLAggregate.fieldName(func, column)
            adoc[fieldName] = aggregationFunc(documents, column)

      return [adoc]
    else:
      return documents

  def count(self, documents, column):
    return len(documents)

  def sum(self, documents, column):
    total = 0
    for doc in documents:
      value = doc[column]
      if isinstance(value, int) or isinstance(value, float):
        total += value
    return total

  def avg(self, documents, column):
    count = 0
    total = 0
    for doc in documents:
      value = doc[column]
      if isinstance(value, int) or isinstance(value, float):
        count += 1
        total += value
    if count > 0:
      return float(total) / float(count)
    else:
      return 0

  def min(self, documents, column):
    minValue = sys.maxsize
    for doc in documents:
      value = doc[column]
      if isinstance(value, int) or isinstance(value, float):
        if value < minValue:
          minValue = value
    return minValue

  def max(self, documents, column):
    # 2's compliment binary of maxsize is minsize
    maxValue = ~sys.maxsize
    for doc in documents:
      value = doc[column]
      if isinstance(value, int) or isinstance(value, float):
        if value > maxValue:
          maxValue = value
    return maxValue 
