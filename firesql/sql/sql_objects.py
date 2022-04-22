from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

@dataclass
class SQL_ValueBool():
  """
  Store information about a boolean literal
  """
  type='bool'
  value: bool

@dataclass
class SQL_ValueString():
  """
  Store information about a string literal
  """
  type='string'
  value: str

@dataclass
class SQL_ValueNumber():
  """
  Store information about a number literal
  """
  type='number'
  value: Union[int, float]

SQL_Value = Union[SQL_ValueBool, SQL_ValueNumber, SQL_ValueString]
SQL_ValueList = List[SQL_Value]

@dataclass
class SQL_ColumnRef():
  type='column_ref'
  table: str
  column: str
  func: str

@dataclass
class SQL_SelectFrom():
  part: str
  alias: str

# froward declare
class SQL_BinaryExpression:
  pass

@dataclass
class SQL_Expression():
  expr: Union[SQL_BinaryExpression, SQL_ColumnRef, SQL_Value, SQL_ValueList]
  paren: bool

@dataclass
class SQL_BinaryExpression():
  type='binary_expr'
  operator: str
  left: SQL_Expression
  right: SQL_Expression

@dataclass
class SQL_JoinExpression():
  type='join_expr'
  operator: str
  left: SQL_SelectFrom
  right: SQL_SelectFrom
  on: SQL_BinaryExpression

@dataclass
class SQL_Select():
  type='select'
  columns: List[SQL_ColumnRef]
  froms: Union[SQL_JoinExpression, List[SQL_SelectFrom]]
  where: SQL_BinaryExpression
  
@dataclass
class SQL_Update():
  type='update'
  table: SQL_SelectFrom
  sets: List[SQL_BinaryExpression]
  where: SQL_BinaryExpression

@dataclass
class SQL_Insert():
  type='insert'
  table: SQL_SelectFrom
  columns: List[SQL_ColumnRef]
  values: SQL_ValueList

@dataclass
class SQL_Delete():
  type='delete'
  table: SQL_SelectFrom
  where: SQL_BinaryExpression

SQL_DML_Command = Union[SQL_Select, SQL_Insert, SQL_Update, SQL_Delete]
