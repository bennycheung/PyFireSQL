from dataclasses import dataclass
from typing import Dict, List

@dataclass
class JoinPart():
  docs: Dict
  joinField: str
  selectFields: List
  nameMap: Dict


class FireSQLJoin():

  def __init__(self):
    pass

  def _get_field_value(self, doc, field):
    tokens = field.split('.')
    if len(tokens) == 1:
      return doc.get(field, '')
    else:
      # loop through the subfields to reach the lowest value
      dd = doc
      for f in tokens:
        dd = dd.get(f, '')
        if not dd:
          break
      return dd

  def join(self, leftJoinPart: JoinPart, rightJoinPart: JoinPart) -> List:
    docs = []
    for ldocId, ldoc in leftJoinPart.docs.items():
      for rdocId, rdoc in rightJoinPart.docs.items():
        if ldoc[leftJoinPart.joinField] == rdoc[rightJoinPart.joinField]:
          jdoc = {}
          for field in leftJoinPart.selectFields:
            if field == 'docid':
              jdoc['docid'] = ldocId
            elif field in ldoc:
              jdoc[ leftJoinPart.nameMap[ field ] ] = ldoc[field]
          for field in rightJoinPart.selectFields:
            if field == 'docid':
              jdoc['docid'] = rdocId
            elif field in rdoc:
              jdoc[ rightJoinPart.nameMap[ field ] ] = rdoc[field]
          docs.append(jdoc)
    return docs


  def inner_join(self, leftJoinPart: JoinPart, rightJoinPart: JoinPart) -> List:
    docs = []
    # assign longer part to be lookupPart and the other part is loopPart
    if len(leftJoinPart.docs) > len(rightJoinPart.docs):
      lookupPart = leftJoinPart
      loopPart = rightJoinPart
    else:
      lookupPart = rightJoinPart
      loopPart = leftJoinPart

    # create fast lookup for the right part
    keyLookup = {}
    for docId, doc in lookupPart.docs.items():
      key = doc[lookupPart.joinField]
      if key not in keyLookup:
        keyLookup[key] = [ (docId, doc) ]
      else:
        keyLookup[key].append( (docId, doc) )

    for ldocId, ldoc in loopPart.docs.items():
      if ldoc[loopPart.joinField] in keyLookup:
        # fast lookup for all right part matched the left doc join field
        for rdocId, rdoc in keyLookup[ ldoc[loopPart.joinField] ]:
          jdoc = {}
          for field in loopPart.selectFields:
            if field == 'docid':
              jdoc['docid'] = ldocId
            else:
              jdoc[ loopPart.nameMap[ field ] ] = self._get_field_value(ldoc, field)
          for field in lookupPart.selectFields:
            if field == 'docid':
              jdoc['docid'] = rdocId
            else:
              jdoc[ lookupPart.nameMap[ field ] ] = self._get_field_value(rdoc, field)
          docs.append(jdoc)

    return docs
