from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table to handle the many-to-many relationship
recipe_ingredient_association = Table(
  'recipe_ingredient_association', Base.metadata,
  Column('recipe_id', Integer, ForeignKey('recipes.id')),
  Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)

class Recipe(Base):
  __tablename__ = "recipes"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  description = Column(String)
  cuisine = Column(String)
  dietary = Column(String)
  image = Column(String)
  ingredients = relationship(
    "Ingredient",
    secondary=recipe_ingredient_association,
    back_populates="recipes"
  )

class Ingredient(Base):
  __tablename__ = "ingredients"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  image = Column(String)
  recipes = relationship(
    "Recipe",
    secondary=recipe_ingredient_association,
    back_populates="ingredients"
  )
