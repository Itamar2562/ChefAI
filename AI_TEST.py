from google import genai
client = genai.Client(api_key="AIzaSyCf4MG4JI1aoxJKqTmdcIdcqQdllcj1OBo")

schema = {"type": "array","items": {"type": "object","properties": {"headline": {"type": "string"},"body": {"type": "string"}},"required": ["headline", "body"]}}
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=genai.types.GenerateContentConfig(
    system_instruction=""" 
    Return the answer as an array of objects, where each object is a dict with 'type' :food type , 'name' : recipe-name ,'description': short-description, 'data' : recipe steps as string.
    Return ONLY a valid JSON array.No backticks.No code block.No explanation.No text before or after.Only the JSON array.
    User will give one type of meal from : [Fried, soup, dessert, oven , general].follow these types -general is when no type was given simply write 'general' and dont follow a specific type.
    User might also add extra parameters from this list: [Halal, kosher,vegetarian and vegan] follow them.
    **rules
    *User will give you ingredients (only names-amounts doesn't matter) simply return up to 2 possible recipes *dont force recipes if not found. follow this structure exactly.
    *The user will give many ingredients, you dont have to include all but you cant return recipes that require additional ingredients the user didn't specify. 
    *If you cant return possible recipes simple return the json with name: 'no available recipes'
    *dont add any sign, emojis, only only text and the step numbers.
    *you must answer all steps dont return N/A and try to add details like temperatures or time.
    1. Ingredients
    2. Prepare
    3. Season
    4. Cook
    5. Serve"""))

response = chat.send_message("type: soup Ingredients:[chicken, beef, onion, salt, pepper, paprica, cucumber, chocolate, blueberry, green onion]")


print(response.text)


