from google import genai
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import Literal
import time

from Server.BL.ServerOP import write_to_log, MAX_AI_USAGE_AMOUNT, MAX_AI_RETRIES

load_dotenv()
API_KEY = os.environ.get('API_KEY')
client = genai.Client(api_key=API_KEY)


class Recipe(BaseModel):
    type: Literal["Fried", "Soup", "Dessert", "Oven", "General"] = Field(description="type of dish")
    time: int = Field(description="total max minutes of prep + cooking")
    difficulty: Literal["Easy", "Medium", "Hard", "Very Hard"] = Field(description="difficulty of the dish")
    name: str = Field(description="name of the recipe")
    description: str = Field(description="description of the recipe")
    nutrition: str = Field(description="""
                  string with these exact newline-separated values (use \n):
                  calories:VALUE
                  protein:VALUE
                  fats:VALUE
                  carbs:VALUE
                  sodium:VALUE
                  Allergens:VALUE
                  (Write "None" or "0" if a value doesn't apply)
                  dont forget units of measure""")
    data: str = Field(description="""
                 string with all preparation steps:
                  1. Ingredients:
                     - list each ingredient on a new line starting with "-"
                  2. Step name:
                     (content here)
                  3. Step name:
                     (content here) 
                  and etc for all steps.
                  Use exactly two newlines (\n\n) between steps.Include step numbers.""")


class RecipesResponse(BaseModel):
    recipes: list[Recipe]

# Builds a structured prompt, sends it to the AI model, and returns the raw response text
def get_response(user_prompt):
    full_prompt = f"""
    Generate recipes based on the following user request.
    User input specifies: time (approximate), types (follow exactly), difficulty (follow exactly),
                 preferences (Halal/Kosher/Vegetarian/Vegan), and ingredients (names only).
    USER REQUEST:
    {user_prompt}

     INGREDIENT RULES (CRITICAL):
    - ONLY use ingredients from the provided list
    - Do NOT add salt, pepper, oil, water, butter, spices, flour, sugar, or any pantry staples
    - If any ingredient is not in the provided list, do not use it
    - If the ingredient list is empty, return the "no available recipes" response
    - If ingredients cannot make a real dish, return "no available recipes" response
    - you don't have to use all of the ingredients and don't specify where the ingredient is from (e.g. from "water")

    NO AVAILABLE RECIPES RESPONSE (if applicable):
    Return this exact structure if no valid recipes exist:
    return one recipe with the name "no available recipes" and with all the other fields empty

    OUTPUT REQUIREMENTS:
    - Return as many recipes as you can with at least 6 recipes that are correct (return less if you cant find correct ones)
    - NO field should be empty except in the "no available recipes" case
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RecipesResponse
        )
    )
    return response.text


# Builds an AI request string, logs it, and returns either simulated or real AI output
def send_and_receive_ai_request(cooking_time: str, food_type: str, difficulty: str, preference: str, ingredients: str):
    request = f"maximum time: {cooking_time}; type: {food_type}; difficulty: {difficulty}; additional preference: {preference}; Ingredients: {ingredients};"
    response = get_response(request)
    return response










