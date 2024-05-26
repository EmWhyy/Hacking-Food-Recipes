import flet as ft
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
    def show_plots(self):
        asset_path = self.path + "/plots"
        # test if the file exists
        image_files = ["graph.png", "Samples.png", "matrices.png"]

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
        
    def build(self):
        # page settings
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.auto_scroll = True
        self.page.theme_mode = "dark"
        
        # Buttons
        toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=self.toggle_dark_mode)
        compute_button = ft.ElevatedButton("Compute", on_click=self.compute)
        add_button = self.create_floating_button(ft.icons.ADD, self.InputManager.add_row, "Add new row", 120, ft.colors.BLUE_200)
        delete_button = self.create_floating_button(ft.icons.REMOVE, self.InputManager.delete_row, "Delete row", 10, ft.colors.RED_200)
    
        self.page.overlay.extend([add_button, delete_button])
        self.position_floating_button(add_button, delete_button)
    
        # name of the recipe
        self.recipe_name = ft.TextField(
            label="Recipe Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80)
        
        self.page.add(ft.Row([compute_button,toggle_dark_mode_button]))
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
        new_border_color = "white" if self.page.theme_mode == "light" else "black"
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.recipe_name.border_color = new_border_color
        
        for row in self.InputManager.input_rows:
            name_input, amount_input = row.controls
            name_input.border_color = new_border_color
            if not (amount_input.border_color == "red"):
                amount_input.border_color = new_border_color
        
        self.page.update()
        
    def compute(self, e):
        inputs = self.InputManager.get_inputs()
        parseInput(inputs, self.page, self.recipe_name.value)
        self.Plots.remove_plots(e)
        self.Plots.show_plots()
        
        

def main(page: ft.Page):
    main_page = MainPage(page)
    main_page.build()

    # test area 
    # text = []
    
    # def printo(e):
    #     new_text = ft.Text("Hello World")
    #     text.append(new_text)
    #     page.add(new_text)
    #     page.update()
    
    # def deleto(e):
    #     if len(text) > 0:
    #         page.remove(text.pop())
    #         page.update()
        
    
    # test_button = ft.ElevatedButton("Test", on_click=printo)
    # test_button2 = ft.ElevatedButton("Test", on_click=remove_plots)
    
    
    # page.add(ft.Row([test_button, test_button2]))
    
    
    
    
    
    
    
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
    
    Input.createMatrices(stringArray, numberArray, Nutrients, page, recipe_name)
    
ft.app(main)
