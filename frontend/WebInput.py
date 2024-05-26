import flet as ft
from flet import TextField,ElevatedButton, Text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Input

def main(page: ft.Page):
    # path to Hacking-Food-Recipes
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    
    # Set the page properties
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.auto_scroll = True
    page.theme_mode = "dark"
    
    # List to store input rows
    input_rows = []
    
    # Function to add a row
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
    
    # Function to delete a row
    def delete_row(e):
        if len(input_rows) > 0:
            page.remove(input_rows.pop())

    # Final function to compute the recipe
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
        
    # Function to show the plots  
    def show_plots():
        asset_path = path + "/plots"
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
                page.add(img)
                page.update()
            else:
                page.add(Text("No " + file + " found"))

    # Checks the textbox input for valid numbers
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

    # Hard coded positions for the floating buttons
    def pos_floating_button(add_button, delete_button):
        page.overlay.extend([add_button, delete_button])
        
        add_button.top = None
        add_button.left = None
        add_button.bottom = 20
        add_button.right = 120

        delete_button.top = None
        delete_button.left = None
        delete_button.bottom = 20
        delete_button.right = 10
        
        

    toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=toggle_dark_mode)
    compute_button = ft.ElevatedButton("Compute", on_click=compute)
    add_button = ft.FloatingActionButton(
        content=ft.Row(
            [ft.Icon(ft.icons.ADD)], alignment="center", spacing=5
        ),
        on_click=add_row,
        shape=ft.RoundedRectangleBorder(radius=5),
        width=100,
        mini=True,
        tooltip="Add new row"
    )
    
    
    delete_button = ft.FloatingActionButton(
        content=ft.Row(
            [ft.Icon(ft.icons.REMOVE)], alignment="center", spacing=5
        ),
        on_click=delete_row,
        bgcolor=ft.colors.RED_200,
        shape= ft.RoundedRectangleBorder(radius=5),
        width=100,
        mini=True,
        tooltip="Delete row"
        )
    
    pos_floating_button(add_button, delete_button)
    
    # Add buttons to the page
    page.add(ft.Row([compute_button,toggle_dark_mode_button]))
    
    # name of the recipe
    recipe_name = ft.TextField(label="Recipe Name",
                               border_color= "black" if page.theme_mode == "light" else "white",
                               height = 80)
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
