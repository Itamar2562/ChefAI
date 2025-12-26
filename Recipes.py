import itertools
import time

from PIL.ImageOps import expand

from Protocol import *

class Recipes:
    def __init__(self, container, home, client_statue,callback_receive_msg):
        self._container=container
        self._home_window=home
        self._recipes_main_window=None
        self._client_statue=client_statue
        self._callback_receive_msg=callback_receive_msg
        self._recipes_scrollable_window=None
        self._received_massage=False
        self._loading_label=None
        self._headline=None
        self._btn_back=None
        self._threads=[]
        self._frames=[]
        self._specific_recipe_frame=None
        self._drag_start_x=0
        self._drag_start_y=0
        self._drag_scheduled=False
        self._cook_image = CTkImage(Image.open(r"Images\cook_icon.png"), size=(100, 100))

    def create_ui(self):
        self._recipes_main_window=CTkFrame(self._container, )
        self._recipes_main_window.pack(fill="both",expand=True)
        self._recipes_scrollable_window = CTkScrollableFrame(self._recipes_main_window,height=500,width=980)
        self._loading_label=CTkLabel(master=self._recipes_main_window, font=('Calibri', 100), anchor='w')
        self._loading_label.place(x=250,y=250)
        t1=threading.Thread(target=lambda: self.animate(self._recipes_main_window), daemon=True)
        t1.start()
        self._threads.append(t1)
        t2=threading.Thread(target=self.receive_massage)
        t2.start()
        self._threads.append(t2)
    #return the scrollable frame in recieve massage

    def create_recipes_frame(self):
        self._recipes_scrollable_window.place(x=0,y=60)
        self._headline=CTkLabel(master=self._recipes_main_window, text="Recipes", font=('Calibri', 50,"bold","underline"))
        self._headline.place(x=410,y=0)
        self._btn_back = CTkButton(self._recipes_main_window, text="Back", height=30, width=80, text_color="white", hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_back)
        self._btn_back.place( x=920,y=10)

    def on_click_back(self):
        self.on_click_destroy_specific_recipe()
        self._recipes_main_window.pack_forget()
        self._home_window.pack(fill="both", expand=True)

    def receive_massage(self):
        #msg=[{"type":"general","time":65,"name":"Vegetarian Frittata with Carrots & Mozzarella","description":"A hearty Italian-style frittata baked with fresh vegetables and melted mozzarella cheese.","data":"1. Ingredients: 8 large eggs, 1 medium onion, 2 ripe tomatoes, 1 large carrot, 1 cup shredded mozzarella cheese, 1 small chile pepper (optional), 1 tsp paprica, salt and pepper to taste, 1 tbsp olive oil.\n2. Prepare: Preheat oven to 375°F (190°C). Dice the onion, tomatoes, and chile pepper. Grate the carrot. Whisk eggs in a large bowl with salt, pepper, and paprica.\n3. Season: Adjust the seasoning of the whisked egg mixture to your preference.\n4. Cook: Heat olive oil in an oven-safe, non-stick skillet over medium heat. Sauté diced onion and grated carrots for 5-7 minutes until softened. Add diced tomatoes and chile pepper, cook for another 3-5 minutes. Pour egg mixture over vegetables. Sprinkle mozzarella cheese evenly over the top. Cook on the stovetop for 5-7 minutes until the edges set, then transfer to the preheated oven and bake for 15-20 minutes, or until set and golden brown.\n5. Serve: Let the frittata cool slightly in the skillet before slicing into wedges and serving warm."},{"type":"general","time":45,"name":"Spicy Tomato & Mozzarella Quesadillas with Avocado","description":"Warm tortillas filled with a savory blend of melted mozzarella, fresh tomatoes, and a hint of chile, served with creamy avocado.","data":"1. Ingredients: 4 large tortillas, 1.5 cups shredded mozzarella cheese, 2 ripe tomatoes, 1/2 small onion, 1 small chile pepper (or to taste), 1 ripe avocado, 1 tbsp tomato paste, salt and pepper to taste, 1 tbsp olive oil.\n2. Prepare: Dice tomatoes, onion, and chile pepper finely. In a small bowl, mash the avocado with a pinch of salt. In another bowl, mix diced tomatoes, onion, chile pepper, tomato paste, salt, and pepper.\n3. Season: Taste and adjust seasoning for the tomato mixture and mashed avocado as needed.\n4. Cook: Heat a large skillet over medium heat. Place one tortilla in the skillet. Spread half of the tomato mixture over one half of the tortilla. Sprinkle half of the mozzarella cheese over the mixture. Fold the tortilla in half. Cook for 3-4 minutes per side, until golden brown and cheese is melted. Repeat with remaining ingredients for the second quesadilla.\n5. Serve: Slice the quesadillas in half or quarters and serve immediately with the mashed avocado."},{"type":"general","time":60,"name":"Rustic Tomato Soup with Mozzarella Melts","description":"A comforting and simple homemade tomato soup, enriched with a touch of tomato paste, paired with crispy mozzarella melts on bread.","data":"1. Ingredients: 6-8 ripe tomatoes, 1 medium onion, 2 tbsp tomato paste, 1 tsp paprica, salt and pepper to taste, 4 slices bread, 1 cup shredded mozzarella cheese, 2 tbsp olive oil, 2 tbsp butter.\n2. Prepare: Roughly chop tomatoes and onion. In a large pot, heat olive oil over medium heat. Add onion and sauté until softened, about 5-7 minutes. Add chopped tomatoes, tomato paste, paprica, salt, and pepper. Stir well. Add 2 cups water and bring to a simmer. Cook for 20-25 minutes until vegetables are very soft. For the mozzarella melts, butter one side of each bread slice.\n3. Season: Carefully blend the soup using an immersion blender until smooth (or transfer to a regular blender). Taste and adjust seasoning as needed.\n4. Cook: Return blended soup to the pot and gently heat. For the mozzarella melts, place 2 slices of bread (butter-side down) in a hot skillet over medium heat. Top each with half of the mozzarella cheese. Place the remaining bread slices (butter-side up) on top. Cook until golden brown and cheese is melted, about 3-4 minutes per side.\n5. Serve: Ladle hot soup into bowls. Cut the mozzarella melts in half and serve alongside the soup."},{"type":"general","time":50,"name":"Avocado & Egg Salad Toast Bowls","description":"Toasted bread \"bowls\" filled with a fresh, creamy avocado and hard-boiled egg salad, seasoned with mustard and paprica.","data":"1. Ingredients: 4 slices thick bread, 4 large eggs, 1 ripe avocado, 1/2 medium tomato, 1/4 small onion, 1 tsp mustard, 1/2 tsp paprica, salt and pepper to taste, 1 tbsp olive oil.\n2. Prepare: Preheat oven to 375°F (190°C). Use a large cookie cutter or knife to create an indentation (without cutting through) in the center of each bread slice to form a \"bowl.\" Toast bread slices in the oven for 5-7 minutes until lightly golden. Hard boil the eggs (about 10-12 minutes), then cool, peel, and chop them. Dice the tomato and onion finely. Mash the avocado in a bowl.\n3. Season: In the bowl with mashed avocado, add chopped eggs, diced tomato, diced onion, mustard, paprica, salt, and pepper. Mix well until combined and creamy.\n4. Cook: No cooking required after the initial bread toasting and egg boiling.\n5. Serve: Spoon the avocado and egg salad mixture generously into the toasted bread bowls. Serve immediately."},{"type":"general","time":25,"name":"Berry & Chocolate Vanilla Parfait","description":"A delightful layered dessert featuring fresh blueberries, strawberries, vanilla-flavored yogurt, and a rich chocolate drizzle.","data":"1. Ingredients: 1 cup fresh blueberries, 1 cup fresh strawberries, 1/2 cup chocolate (chips or bar), 1 tsp vanilla extract, 2 cups plain yogurt, 1 tbsp sugar (optional).\n2. Prepare: Wash and slice the strawberries. Gently melt the chocolate using a microwave or a double boiler. In a bowl, mix the plain yogurt with vanilla extract and optional sugar until well combined.\n3. Season: Adjust sweetness of yogurt if using sugar and vanilla.\n4. Cook: No cooking is required for this recipe.\n5. Serve: In clear glasses or bowls, create layers: first a spoonful of vanilla yogurt, then sliced strawberries, followed by blueberries, and a drizzle of melted chocolate. Repeat the layers until the glass is full. Serve chilled."},{"type":"general","time":30,"name":"Crunchy Carrot & Cucumber Avocado Salad","description":"A refreshing and healthy salad combining crunchy carrots, crisp cucumber, creamy avocado, and fresh tomato, dressed in a zesty mustard vinaigrette.","data":"1. Ingredients: 2 medium carrots, 1 large cucumber, 1 ripe avocado, 1 medium tomato, 1/4 small red onion, 2 tbsp olive oil, 1 tbsp mustard, 1 tbsp white vinegar, salt and pepper to taste.\n2. Prepare: Peel and julienne or finely grate the carrots. Dice the cucumber, avocado, tomato, and red onion. In a small bowl, whisk together olive oil, mustard, white vinegar, salt, and pepper to create the dressing.\n3. Season: Taste and adjust the seasoning of the mustard vinaigrette to your preference.\n4. Cook: No cooking is required for this salad.\n5. Serve: Combine all the prepared vegetables in a large mixing bowl. Pour the mustard vinaigrette over the vegetables and toss gently to ensure everything is evenly coated. Serve immediately as a side or light meal."}]
        msg=self._callback_receive_msg()
        write_to_log(msg)
        self._received_massage=True
        self.create_recipes_frame()
        while msg!="END":
            msg=json.loads(msg)
            for i in range(len(msg)):
                self.add_recipe(msg[i])
            bottom_spacer = CTkFrame(self._recipes_scrollable_window, height=50, fg_color="transparent")
            bottom_spacer.pack(fill="x")
            #break
            msg=self._callback_receive_msg() #temp error

    def add_recipe(self,data):
        #create the frame
        current_frame=CTkFrame(master=self._recipes_scrollable_window,width=200,height=100)
        headline=CTkLabel(master=current_frame,text=data['name'], font=('Calibri',20,"bold","underline"))
        description=CTkLabel(master=current_frame,text=data['description'],font=('Calibri',15),wraplength=500,justify="left",)
        cook_btn=CTkButton(master=current_frame,image=self._cook_image,text="",hover=False,fg_color="transparent",command=lambda:self.on_click_cook(data))
        cook_btn.place(x=500,y=0)
        headline.place(x=5,y=0)
        description.place(x=5,y=50)
        self._frames.append(current_frame)
        current_frame.pack(pady=10, padx=2, fill="x",)

    def on_click_cook(self,data):
        if not self._specific_recipe_frame:
            self._specific_recipe_frame = CTkFrame(master=self._recipes_main_window, width=750, height=450,border_width=3,border_color="blue")
            self.bind_drag(self._specific_recipe_frame)
            self._specific_recipe_frame.lift()

        self._drag_start_x = 0
        self._drag_start_y = 0
        headline = CTkLabel(master=self._specific_recipe_frame, text=data['name'],font=('Calibri', 25, "bold", "underline"))
        description = CTkLabel(master=self._specific_recipe_frame, text=data['description'], font=('Calibri', 20),anchor='w', justify="left", wraplength=650)
        btn_back = CTkButton(self._specific_recipe_frame, text="Back", height=30, width=80, text_color="white",hover_color="#4185D0", font=("Calibri", 17), fg_color="#C850C0",command=self.on_click_destroy_specific_recipe)
        recipe_steps = CTkLabel(master=self._specific_recipe_frame, text=data['data'], anchor='w', justify="left",wraplength=700, font=('Calibri', 18))
        for child in self._specific_recipe_frame.winfo_children():
            self.bind_drag(child)
        recipe_steps.place(x=5, y=90)
        headline.place(x=5, y=5)
        description.place(x=5, y=35)
        btn_back.place(x=670, y=5)
        self._specific_recipe_frame.place(x=150, y=50)

    def bind_drag(self,widget):
        widget.bind("<ButtonPress-1>", self.start_move,add="+")
        widget.bind("<B1-Motion>", self.on_move,add="+")

    def start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._drag_scheduled = False

    def on_move(self, event):
        x = self._specific_recipe_frame.winfo_x() + event.x - self._drag_start_x
        y = self._specific_recipe_frame.winfo_y() + event.y - self._drag_start_y

        # schedule placement every 10ms (throttling)
        if not self._drag_scheduled:
            self._drag_scheduled = True
            self._specific_recipe_frame.after(3, self._do_drag, x, y)

    def _do_drag(self, x, y):
        self._specific_recipe_frame.place(x=x, y=y)
        self._drag_scheduled = False

    def on_click_destroy_specific_recipe(self):
        if self._specific_recipe_frame:
            self._specific_recipe_frame.after(0,self._specific_recipe_frame.destroy)
            self._specific_recipe_frame=None

    def animate(self,temp_frame):
        temp_frame.pack(fill="both", expand=True)
        for c in itertools.cycle(['..', '....', '......', '........', '..........', '............']):
            if self._received_massage:
                self._loading_label.after(0,self._loading_label.destroy)
                break
            self._loading_label.configure(text=c)
            time.sleep(0.1)






