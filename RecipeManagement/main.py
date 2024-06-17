from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Base, Ingredient, Recipe
from schemas import Ingredient as IngredientSchema, IngredientUpdate, Recipe as RecipeSchema, RecipeCreate, RecipeUpdate
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
  try:
    db = SessionLocal()
    yield db
  finally:
    db.close()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingredients/", response_model=IngredientSchema)
def create_ingredient(ingredient: IngredientSchema, db: Session = Depends(get_db)):
  db_ingredient = Ingredient(name=ingredient.name, image=ingredient.image)
  db.add(db_ingredient)
  db.commit()
  db.refresh(db_ingredient)
  return db_ingredient

@app.get("/ingredients/", response_model=List[IngredientSchema])
def get_all_ingredients(db: Session = Depends(get_db)):
  ingredients = db.query(Ingredient).all()
  return ingredients

@app.put("/ingredients/{ingredient_id}", response_model=IngredientSchema)
def update_ingredient(ingredient_id: int, ingredient: IngredientUpdate, db: Session = Depends(get_db)):
  db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
  if db_ingredient is None:
    raise HTTPException(status_code=404, detail="Ingredient not found")
  db_ingredient.name = ingredient.name
  db_ingredient.image = ingredient.image
  db.commit()
  db.refresh(db_ingredient)
  return db_ingredient

@app.delete("/ingredients/{ingredient_id}", response_model=IngredientSchema)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
  ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
  if ingredient is None:
    raise HTTPException(status_code=404, detail="Ingredient not found")
  db.delete(ingredient)
  try:
    db.commit()
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=400, detail="Ingredient is associated with a recipe and cannot be deleted")
  return ingredient

@app.post("/recipes/", response_model=RecipeSchema)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
  db_ingredients = db.query(Ingredient).filter(Ingredient.id.in_(recipe.ingredient_ids)).all()
  if not db_ingredients:
    raise HTTPException(status_code=400, detail="Ingredients not found")
  db_recipe = Recipe(
    name=recipe.name,
    description=recipe.description,
    cuisine=recipe.cuisine,
    dietary=recipe.dietary,
    image=recipe.image,
    ingredients=db_ingredients
  )
  db.add(db_recipe)
  db.commit()
  db.refresh(db_recipe)
  return db_recipe

@app.get("/recipes/", response_model=List[RecipeSchema])
def get_all_recipes(db: Session = Depends(get_db)):
  recipes = db.query(Recipe).all()
  return recipes

@app.get("/recipes/{recipe_id}", response_model=RecipeSchema)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
  recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
  if recipe is None:
    raise HTTPException(status_code=404, detail="Recipe not found")
  return recipe

@app.get("/available_ingredients/{recipe_id}")
def get_available_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    existing_ingredient_ids = (
        db.query(Ingredient.id)
        .join(Recipe.ingredients)
        .filter(Recipe.id == recipe_id)
        .all()
    )
    existing_ingredient_ids = [i[0] for i in existing_ingredient_ids]
    available_ingredients = db.query(Ingredient).filter(~Ingredient.id.in_(existing_ingredient_ids)).all()
    return available_ingredients

@app.put("/recipes/{recipe_id}", response_model=RecipeSchema)
def update_recipe(recipe_id: int, recipe: RecipeUpdate, db: Session = Depends(get_db)):
  db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
  if db_recipe is None:
    raise HTTPException(status_code=404, detail="Recipe not found")
  
  if recipe.name is not None:
    db_recipe.name = recipe.name
  if recipe.description is not None:
    db_recipe.description = recipe.description
  if recipe.cuisine is not None:
    db_recipe.cuisine = recipe.cuisine
  if recipe.dietary is not None:
    db_recipe.dietary = recipe.dietary
  if recipe.image is not None:
    db_recipe.image = recipe.image
  
  if recipe.ingredient_ids is not None:
    db_ingredients = db.query(Ingredient).filter(Ingredient.id.in_(recipe.ingredient_ids)).all()
    if len(db_ingredients) != len(recipe.ingredient_ids):
      raise HTTPException(status_code=400, detail="One or more ingredients not found")
    db_recipe.ingredients = db_ingredients
  
  db.commit()
  db.refresh(db_recipe)
  return db_recipe

@app.delete("/recipes/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeSchema)
def remove_ingredient_from_recipe(recipe_id: int, ingredient_id: int, db: Session = Depends(get_db)):
  recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
  if recipe is None:
    raise HTTPException(status_code=404, detail="Recipe not found")
  ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
  if ingredient is None:
    raise HTTPException(status_code=404, detail="Ingredient not found")
  if ingredient not in recipe.ingredients:
    raise HTTPException(status_code=400, detail="Ingredient not in recipe")
  recipe.ingredients.remove(ingredient)
  db.commit()
  db.refresh(recipe)
  return recipe

@app.delete("/recipes/{recipe_id}", response_model=RecipeSchema)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
  recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
  if recipe is None:
    raise HTTPException(status_code=404, detail="Recipe not found")
  db.delete(recipe)
  db.commit()
  return recipe