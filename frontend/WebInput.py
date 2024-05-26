import flet as ft
from flet import TextField,ElevatedButton, Text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Input

def main(page: ft.Page):
    # path to Hacking-Food-Recipes
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = "dark"
    # List to store input rows
    input_rows = []
    
    

    def add_row(e):
        name_input = ft.TextField(label="Ingredient Name",
                                  border_color= "black" if page.theme_mode == "light" else "white",
                                  height = 80
                                  )
        amount_input = ft.TextField(label="Amount",
                                    border_color= "black" if page.theme_mode == "light" else "white",
                                    on_change= textbox_changed,
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    height = 80
                                    )
        input_row = ft.Row([name_input, amount_input])
        input_rows.append(input_row)
        page.add(input_row)
    
    def delete_row(e):
        if len(input_rows) > 0:
            page.remove(input_rows.pop())

    def compute(e):
        inputs = []
        for row in input_rows:
            name_input, amount_input = row.controls  
            inputs.append((name_input.value, amount_input.value))
            
        parseInput(inputs, page, recipe_name.value)
        show_plots()


    def toggle_dark_mode(e):
        new_border_color = "white" if page.theme_mode == "light" else "black"
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        recipe_name.border_color = new_border_color
        
        for row in input_rows:
            name_input, amount_input = row.controls
            name_input.border_color = new_border_color
            if not (amount_input.border_color == "red"):
                amount_input.border_color = new_border_color
        
        page.update()
    
    def show_plots():
        asset_path = path + "/plots"
        # test if the file exists
        image_files = ["graph.png", "Samples.png", "matrices.png"]

        for file in image_files:
            if os.path.exists(asset_path + "/" + file):
                img = ft.Image(
                    src=asset_path + "/" + file,
                    width=800,
                    height=800,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=1,
                )
                page.add(img)
                page.update()
            else:
                page.add(Text("No " + file + " found"))
    


    def textbox_changed(e):
        
        try:
            input = float(e.control.value)
            e.control.border_color = "white"
            e.control.helper_text = None
            page.update()
        except:
            e.control.border_color = "red"
            e.control.helper_text = "Please enter a number"
            page.update()


        
        
    # Buttons
    toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=toggle_dark_mode)
    add_button = ft.ElevatedButton("Add Row", on_click=add_row)
    compute_button = ft.ElevatedButton("Compute", on_click=compute)
    delete_button = ft.ElevatedButton("Delete Row", on_click=delete_row)
    
    # Add buttons to the page
    page.add(ft.Row([add_button,delete_button ,compute_button,toggle_dark_mode_button]))
    
    # name of the recipe
    recipe_name = ft.TextField(label="Recipe Name",
                               border_color= "black" if page.theme_mode == "light" else "white")
    page.add(recipe_name)
    

def parseInput(input, page: ft.Page, recipe_name: str, Nutrients = None):

    # Check if the input is valid
    if len(input) == 0:
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
