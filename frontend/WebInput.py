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
        name_input = ft.TextField(label="Ingredient Name")
        number_input = ft.TextField(label="Amount")
        input_row = ft.Row([name_input, number_input])
        input_rows.append(input_row)
        page.add(input_row)

    def compute(e):
        inputs = []
        for row in input_rows:
            name_input, number_input = row.controls  
            inputs.append((name_input.value, number_input.value))
            
        Input.parseInput(inputs, page, recipe_name.value)
        show_plots()

    
    def toggle_dark_mode(e):
        if page.theme_mode == "light":
            page.theme_mode = "dark"
        else:
            page.theme_mode = "light"
        page.update()
    
    def show_plots():

        asset_path = path + "/plots"


        # test if the file exists
        if os.path.exists(asset_path + "/graph.png"):
            img = ft.Image(
                src=asset_path + "/graph.png",
                width=800,
                height=800,
                fit=ft.ImageFit.CONTAIN,
                border_radius=1,
            )
            page.add(img)
            page.update()           
        else:
            page.add(Text("No graph found"))
            
        if os.path.exists(asset_path + "/Samples.png"):
            img = ft.Image(
                src=asset_path + "/Samples.png",
                width=800,
                height=800,
                fit=ft.ImageFit.CONTAIN,
                border_radius=1,
            )
            page.add(img)
            page.update()
            
        else:
            page.add(Text("No Samples found"))
            
        if os.path.exists(asset_path + "/matrices.png"):
            img = ft.Image(
                src=asset_path + "/matrices.png",
                width=800,
                height=800,
                fit=ft.ImageFit.CONTAIN,
                border_radius=1,
            )
            page.add(img)
            page.update()
        else:
            page.add(Text("No matrices found"))
        






    # Buttons
    toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=toggle_dark_mode)
    add_button = ft.ElevatedButton("Add Row", on_click=add_row)
    compute_button = ft.ElevatedButton("Compute", on_click=compute)
    
    # Add the buttons to the page
    page.add(ft.Row([add_button, compute_button,toggle_dark_mode_button]))
    
    # name of the recipe
    recipe_name = ft.TextField(label="Recipe Name")

    page.add(recipe_name)
    
ft.app(main)
