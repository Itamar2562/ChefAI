import itertools
import time
from Protocol import *

class Recipes:
    def __init__(self, container, home, client_statue,callback_receive_msg):
        self._container=container
        self._home=home
        self._client_statue=client_statue
        self._callback_receive_msg=callback_receive_msg
        self._recipes_window=None
        self._received_massage=False
        self._loading_label=None
        self._threads=[]
        self._frames=[]

    def create_ui(self):

        self._recipes_window = CTkScrollableFrame(self._container)
        temp_frame=CTkFrame(self._container, )
        self._loading_label=CTkLabel(master=temp_frame, font=('Calibri', 100), anchor='w')
        self._loading_label.place(x=250,y=250)

        t1=threading.Thread(target=lambda: self.animate(temp_frame), daemon=True)
        t1.start()
        self._threads.append(t1)
        t2=threading.Thread(target=self.receive_massage)
        t2.start()
        self._threads.append(t2)
    #return the scrollable frame in recieve massage

    def receive_massage(self):
        # msg=[
        #     {"type":"general","time":45,"name":"Chicken and Veggie Tortilla Wraps","description":"Flavorful chicken and fresh vegetables wrapped in soft tortillas.","data":"Ingredients: 2 chicken breasts, 4 tortillas, 1 tomato, 1/2 cucumber, 1/4 onion, 1 chile pepper (optional), 1/2 avocado, 1 tbsp mustard, pinch of pepper.\nPrepare: Slice chicken breasts into thin strips. Dice tomato, cucumber, onion, and chile pepper. Mash avocado.\nSeason: Toss chicken strips with mustard, paprica, and pepper.\nCook: Heat a pan over medium-high heat. Cook chicken strips until browned and cooked through, about 5-7 minutes. Warm tortillas in a dry pan for 15-30 seconds per side.\nServe: Spread mashed avocado on each tortilla. Add cooked chicken, diced vegetables, and roll up tightly."},
        #     {"type":"general","time":75,"name":"Meat and Onion Skewers","description":"Juicy meat and tender onions grilled or baked with a savory tomato paste glaze.","data":"Ingredients: 500g meat, 1 large onion, 2 tbsp tomato paste, 1 tsp paprica, 1/2 tsp pepper, skewers.\nPrepare: Cut meat into 1-inch cubes. Cut onion into wedges, separating layers. If using wooden skewers, soak them in water for 30 minutes.\nSeason: In a bowl, combine tomato paste, paprica, and pepper. Add meat and onion, toss to coat. Marinate for at least 30 minutes in the refrigerator.\nCook: Preheat oven to 200°C (400°F) or preheat grill to medium-high heat. Thread marinated meat and onion alternately onto skewers. Grill for 15-20 minutes, turning occasionally, until meat is cooked to your preference. If baking, place skewers on a baking sheet and bake for 20-25 minutes, turning once, until cooked through.\nServe: Serve hot, perhaps with a simple side salad."},
        #     {"type":"general","time":25,"name":"Avocado and Egg Toast","description":"Toasted bread topped with creamy avocado, a fried egg, and fresh tomato.","data":"Ingredients: 2 slices bread, 2 eggs, 1 avocado, 1/2 tomato, pinch of pepper.\nPrepare: Slice avocado thinly or mash. Slice tomato.\nSeason: Season eggs with pepper before or after cooking.\nCook: Toast bread until golden. Fry eggs to your desired doneness (sunny-side up, over easy, etc.).\nServe: Spread mashed avocado or arrange slices on toast. Top with fried egg and tomato slices. Sprinkle with pepper."},
        #     {"type":"dessert","time":80,"name":"Berry and Chocolate Bread Pudding","description":"A comforting dessert featuring bread, mixed berries, and rich chocolate, baked until golden.","data":"Ingredients: 4 slices bread, 1 cup blueberries, 1 cup strawberries (sliced), 1/2 cup chocolate (chopped), 2 eggs, 1 tsp vanilla.\nPrepare: Tear bread into small pieces. Slice strawberries.\nSeason: Not applicable for this step.\nCook: Preheat oven to 180°C (350°F). In a bowl, whisk eggs and vanilla. Gently fold in bread pieces, blueberries, sliced strawberries, and chopped chocolate. Pour mixture into a greased baking dish. Bake for 45-60 minutes, or until set and golden brown on top. A knife inserted into the center should come out mostly clean.\nServe: Serve warm."},
        #     {"type":"general","time":15,"name":"Fresh Tomato, Cucumber and Onion Salad","description":"A light and refreshing salad with crisp vegetables.","data":"Ingredients: 2 tomatoes, 1 cucumber, 1/2 onion, pinch of pepper.\nPrepare: Dice tomatoes and cucumber. Thinly slice the onion.\nSeason: Add pepper to taste.\nCook: No cooking required.\nServe: Combine all diced and sliced vegetables in a bowl. Toss gently and serve immediately."},
        #     {"type":"general","time":40,"name":"Spicy Chicken and Carrot Skillet","description":"A quick and spicy one-pan meal with tender chicken and carrots.","data":"Ingredients: 2 chicken breasts, 2 carrots, 1/2 onion, 1-2 chile peppers, 1 tsp paprica, 1/2 tsp pepper.\nPrepare: Slice chicken breasts into bite-sized pieces. Peel and slice carrots into thin rounds or julienne. Dice onion and chile peppers.\nSeason: Toss chicken with paprica and pepper.\nCook: Heat a large skillet over medium-high heat. Add chicken and cook until browned and cooked through, about 5-7 minutes. Remove chicken and set aside. Add carrots, onion, and chile peppers to the skillet. Sauté for 8-10 minutes until vegetables are tender-crisp. Return chicken to the skillet, stir to combine, and heat through for 1-2 minutes.\nServe: Serve hot, as a standalone meal or with bread."}]
        msg=self._callback_receive_msg()
        write_to_log(msg)
        self._received_massage=True
        self._recipes_window.pack(fill="both",expand=True)
        while msg!="END":
            msg=json.loads(msg)
            for i in range(len(msg)):
                self.add_recipe(msg[i])
            msg=self._callback_receive_msg()

    def add_recipe(self,data):
        #create the frame
        current_frame=CTkFrame(master=self._recipes_window,width=200,height=300)
        headline=CTkLabel(master=current_frame,text=data['name'], font=('Calibri',20,"bold"))
        description=CTkLabel(master=current_frame,text=data['description'],font=('Calibri',15))
        headline.place(x=50,y=0)
        description.place(x=0,y=50)
        data_text=CTkLabel(master=current_frame,text=data['data'],anchor='w', wraplength=1000)
        data_text.place(x=0,y=100)
        self._frames.append(current_frame)
        current_frame.pack(pady=20, padx=2, fill="x",)


    def animate(self,temp_frame):
        temp_frame.pack(fill="both", expand=True)
        for c in itertools.cycle(['..', '....', '......', '........', '..........', '............']):
            if self._received_massage:
                temp_frame.after(0,temp_frame.destroy)
                break
            self._loading_label.configure(text=c)
            time.sleep(0.1)






