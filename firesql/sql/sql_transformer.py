from lark import Transformer
from .sql_objects import *

class SelectTransformer(Transformer):
  def name(self, args):
    return args[0]

  def string(self, args):
    return args[0]

  CNAME = str
  STAR = str

  def ESCAPED_STRING(self, args):
    return str(args).strip('"')

  def true(self, args):
    return True

  def false(self, args):
    return False

  def number(self, args):
    sqlValue = SQL_ValueNumber(args[0].value)
    return sqlValue

  def bool(self, args):
    sqlValue = SQL_ValueBool(args[0])
    return sqlValue

  def string(self, args):
    sqlValue = SQL_ValueString(eval(args[0].value))
    return sqlValue
  
  def literal(self, args):
    return args[0]

  def alias_string(self, args):
    return args[0]

  def column_name(self, args):
    # (table_name, field_name)
    sqlColumn = SQL_ColumnRef(table=args[0], column=args[1])
    return sqlColumn

  def select_expression(self, args):
    return args[0]

  def from_expression(self, args):
    return args[0]

  def join(self, args):
    return args[0]
  
  def join_expression(self, args):
    if len(args) > 2:
      sqlJoin = SQL_JoinExpression(operator='join', left=args[0], right=args[1], on=args[2])
    else:
      sqlJoin = SQL_JoinExpression(operator='join', left=args[0], right=args[1], on=None)
    return sqlJoin

  def table_name(self, args):
    # (table_name, alias)
    sqlFrom = SQL_SelectFrom(part=args[0], alias=args[1])
    return sqlFrom

  def select_clause(self, args):
    return args

  def from_clause(self, args):
    return args

  def equals(self, args):
    sqlExpr = SQL_BinaryExpression(operator='==', left=args[0], right=args[1])
    return sqlExpr

  def not_equals(self, args):
    sqlExpr = SQL_BinaryExpression(operator='!=', left=args[0], right=args[1])
    return sqlExpr

  def is_null(self, args):
    sqlExpr = SQL_BinaryExpression(operator='==', left=args[0], right=None)
    return sqlExpr

  def is_not_null(self, args):
    sqlExpr = SQL_BinaryExpression(operator='!=', left=args[0], right=None)
    return sqlExpr

  def greater_than(self, args):
    sqlExpr = SQL_BinaryExpression(operator='>', left=args[0], right=args[1])
    return sqlExpr

  def less_than(self, args):
    sqlExpr = SQL_BinaryExpression(operator='<', left=args[0], right=args[1])
    return sqlExpr

  def greater_than_or_equal(self, args):
    sqlExpr = SQL_BinaryExpression(operator='>=', left=args[0], right=args[1])
    return sqlExpr

  def less_than_or_equal(self, args):
    sqlExpr = SQL_BinaryExpression(operator='<=', left=args[0], right=args[1])
    return sqlExpr

  def in_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='in', left=args[0], right=args[1:])
    return sqlExpr

  def not_in_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='not_in', left=args[0], right=args[1:])
    return sqlExpr

  def contain_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='array_contains', left=args[0], right=args[1])
    return sqlExpr

  def contain_any_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='array_contains_any', left=args[0], right=args[1:])
    return sqlExpr

  def like_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='like', left=args[0], right=args[1])
    return sqlExpr

  def not_like_expr(self, args):
    sqlExpr = SQL_BinaryExpression(operator='not_like', left=args[0], right=args[1])
    return sqlExpr

  def comparison_type(self, args):
    return args[0]

  def bool_and(self, args):
    sqlExpr = SQL_BinaryExpression(operator='and', left=args[0], right=args[1])
    return sqlExpr

  def bool_or(self, args):
    sqlExpr = SQL_BinaryExpression(operator='or', left=args[0], right=args[1])
    return sqlExpr

  def bool_parentheses(self, args):
    return args[0]

  def bool_expression(self, args):
    return args[0]

  def where_clause(self, args):
    return args[0]

  def select(self, args):
    sqlSelect = SQL_Select(columns=args[0], froms=args[1], where=args[2])
    return sqlSelect
  
  def final(self, args):
    return args[0]
