import flet as ft
import numpy as np
from flet import TextField,ElevatedButton, Text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Input

class InputManager:
    def __init__(self,page):
        self.page = page
        self.input_rows = []
    
    # Function to add a row
    def add_row(self, e):       
        name_input = ft.TextField(
            label="Ingredient Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80
            )
        
        amount_input = ft.TextField(
            label="Amount",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            on_change= self.textbox_changed,
            keyboard_type=ft.KeyboardType.NUMBER,
            height = 80
            )
        input_row = ft.Row([name_input, amount_input])
        self.input_rows.append(input_row)
        self.page.add(input_row)
        
    # Checks the textbox input for valid numbers
    def textbox_changed(self, e):
        try:
            input = float(e.control.value)
            e.control.border_color = "white"
            e.control.helper_text = None
            self.page.update()
        except:
            e.control.border_color = "red"
            e.control.helper_text = "Please enter a number"
            self.page.update()
    
    # Function to delete a row
    def delete_row(self, e):
        if len(self.input_rows) > 0:
            self.page.remove(self.input_rows.pop())

    def get_inputs(self):
        inputs = []
        for row in self.input_rows:
            name_input, amount_input = row.controls
            inputs.append((name_input.value, amount_input.value))
        return inputs

class Plots:
    def __init__(self, page):
        self.page = page
        # path to Hacking-Food-Recipes
        self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.plots = []

 # Function to show the plots  
    def show_plots(self,e):
        self.page.auto_scroll = False
        asset_path = self.path + "/plots"
        # test if the file exists
        image_files = ["graph.png", "Samples.png", "matrices.png"]
        if len(self.plots) > 0:
            return

        for file in image_files:
            if os.path.exists(asset_path + "/" + file):
                img = ft.Image(
                    src=asset_path + "/" + file,
                    width=900,
                    height=350,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=1,
                )
                self.plots.append(img)
                self.page.add(img)
                self.page.update()
                
            else:
                self.page.add(Text("No " + file + " found"))
        self.page.auto_scroll = True
    
    def remove_plots(self,e):
        if len(self.plots) > 0:
            for i in range(len(self.plots)):
                self.page.remove(self.plots.pop())
                self.page.update()

    
class MainPage:
    def __init__(self, page):
        self.page = page
        self.InputManager = InputManager(page)
        self.Plots = Plots(page)
        self.text_elements = []
    
    def new_recipe(self, e):
        self.delete_output_text()
        self.Plots.remove_plots()
        if self.InputManager.input_rows:
            for row in self.InputManager.input_rows:
                self.page.remove(row)
                self.page.update()
            self.InputManager.input_rows = []
        self.page.update()
        
    def build(self):
        # page settings
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.auto_scroll = True
        self.page.theme_mode = "dark"
        
        # Buttons
        toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=self.toggle_dark_mode)
        compute_button = ft.ElevatedButton("Compute", on_click=self.compute)
        new_recipe_button = ft.ElevatedButton("New Recipe", on_click=self.new_recipe)
        show_plots_button = ft.ElevatedButton("Show Plots", on_click=self.Plots.show_plots)
        close_plots_button = ft.ElevatedButton("Close Plots", on_click=self.Plots.remove_plots)
        add_button = self.create_floating_button(ft.icons.ADD, self.InputManager.add_row, "Add new row", 120, ft.colors.BLUE_200)
        delete_button = self.create_floating_button(ft.icons.REMOVE, self.InputManager.delete_row, "Delete row", 10, ft.colors.RED_200)
        
    
        self.page.overlay.extend([add_button, delete_button])
        self.position_floating_button(add_button, delete_button)
    
        # name of the recipe
        self.recipe_name = ft.TextField(
            label="Recipe Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80)
        
        self.page.add(ft.Row([compute_button,toggle_dark_mode_button,new_recipe_button, show_plots_button,close_plots_button]))
        self.page.add(self.recipe_name)
        

    # Function to create a floating button
    def create_floating_button(self, icon, on_click, tooltip, right, bgcolor):
        return ft.FloatingActionButton(
            content=ft.Row([ft.Icon(icon)], alignment="center", spacing=5),
            on_click=on_click,
            shape=ft.RoundedRectangleBorder(radius=5),
            width=100,
            mini=True,
            tooltip=tooltip,
            bgcolor=bgcolor,
            right=right,
            bottom=20
        )
        
    # Hard coded positions for the floating buttons
    def position_floating_button(self,add_button, delete_button):
        add_button.top = None
        add_button.left = None

        delete_button.top = None
        delete_button.left = None 

    def toggle_dark_mode(self, e):
        self.page.auto_scroll = False
        new_border_color = "white" if self.page.theme_mode == "light" else "black"
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.recipe_name.border_color = new_border_color
        
        for row in self.InputManager.input_rows:
            name_input, amount_input = row.controls
            name_input.border_color = new_border_color
            if not (amount_input.border_color == "red"):
                amount_input.border_color = new_border_color
        
        self.page.update()
        self.page.auto_scroll = True
        
    def compute(self, e):
        inputs = self.InputManager.get_inputs()
        
        ingredients = [item[0] for item in inputs]
        values_input = [item[1] for item in inputs]
        if len(inputs) < 4:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("Provide more then 4 ingredients"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return
        
        # two values muss be without a given amount
        if values_input.count('') < 2:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("Provide at least 2 ingredients without a given amount"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return
        
        SAMPLES = parseInput(inputs, self.page, self.recipe_name.value)
        self.delete_output_text()
        self.output(SAMPLES,ingredients)
        self.Plots.remove_plots()
        
        
    def output(self, samples, ingredients):
        mean_sample = np.mean(samples, axis=0)
        std_sample = np.std(samples, axis=0)
        
        recipe_name = self.recipe_name.value
        length = len(ingredients)
        
        self.text_elements = [
            Text("Dish: " + recipe_name),
            Text(f"{length} ingredients in total"),
            Text("=" * 66)
            ]
        for i, zutat in enumerate(ingredients):
            self.text_elements.append(Text("{:>42}".format(zutat) + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"))
        self.text_elements.append(Text("=" * 66))
        
        
        for element in self.text_elements:
            self.page.add(element)
        
    def delete_output_text(self):
        if self.text_elements:
            for i in range(len(self.text_elements)):
                self.page.remove(self.text_elements.pop())
                self.page.update()
    
        
def main(page: ft.Page):
    main_page = MainPage(page)
    main_page.build()
 
    
def parseInput(input, page: ft.Page, recipe_name: str, Nutrients = None):

    # Check if the input is valid
    if len(input) <= 3:
        #<----------- would be nice to give the user a hint that they need to add more ingredients
        return

    # Parse the input
    stringArray = [item[0] for item in input]
    numberArray = [float(item[1]) if item[1] != '' else None for item in input]
    if Nutrients == None:
        Nutrients = [0,0,0,0,0,0]


    # Check if the parsed input is valid
    if numberArray.count(None) < 2:
        #<----------- would be nice to give the user a hint that they need at least 2 ingredients without a given amount
        return 
    if sum([float(item[1]) if item[1] != '' else 0 for item in input]) >= 1:
        #<----------- would be nice to give the user a hint that the sum of the ingredients should be less than 1
        return
    
    result = Input.createMatrices(stringArray, numberArray, Nutrients, page, recipe_name)
    return result
    
ft.app(main)
