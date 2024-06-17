from pydantic import BaseModel
from typing import List, Optional

class IngredientBase(BaseModel):
  name: str
  image: str

class IngredientCreate(IngredientBase):
  pass

class Ingredient(IngredientBase):
  id: int

  class Config:
    orm_mode = True

class IngredientUpdate(BaseModel):
  name: Optional[str]
  image: Optional[str]

class RecipeBase(BaseModel):
  name: str
  description: str
  cuisine: str
  dietary: str
  image: str

class RecipeCreate(RecipeBase):
  ingredient_ids: List[int]

class Recipe(RecipeBase):
  id: int
  ingredients: List[Ingredient] = []

  class Config:
      orm_mode = True

class RecipeUpdate(BaseModel):
  name: Optional[str]
  description: Optional[str]
  cuisine: Optional[str]
  dietary: Optional[str]
  image: Optional[str]
  ingredient_ids: Optional[List[int]]