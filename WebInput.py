import flet as ft
import numpy as np
from flet import TextField,ElevatedButton, Text, Image
import sys
import os
import backend.Input as Input


import base64
from io import BytesIO
from PIL import Image as pil_image
class MainPage:
    def __init__(self, page):
        self.page = page
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.text_elements = []
        self.input_rows = []
        self.plot = None
        self.sample_plot = None
        self.computing = False
        
# Input region 

    # Function to add a row
    def add_row(self, e):

        if (self.plot is not None) or len(self.text_elements) > 0:
            self.remove_all_output(e)

        name_input = ft.TextField(
            label="Ingredient Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col=7
            )
        
        amount_input = ft.TextField(
            label="Amount",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            on_change= self.textbox_changed,
            keyboard_type=ft.KeyboardType.NUMBER,
            height = 80,
            col=5
            )
        
        input_row = ft.ResponsiveRow([name_input, amount_input])
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
# Input region end

# Plot region
 # Function to show the plot
    def show_plot(self,e):
        self.page.auto_scroll = False
        # test if the file exists

        if self.plot is not None:
            image_string = base64.b64encode(self.plot.getvalue()).decode("utf-8")
            self.plot.seek(0)
            self.sample_plot = Image(src_base64=image_string)
            self.page.add(
                ft.Row(controls=[self.sample_plot], alignment='center'))
        else:
            self.popup_snackbar("No plot available", ft.colors.RED_200)

        self.page.auto_scroll = True
    
    def remove_plot(self,e):
        if (self.plot != None):
            #TODO: Fix this
            # self.page.remove(self.sample_plot)
            # self.sample_plot = None
            # self.page.update()
            pass
                
    def plot_change(self, e):
        if e.control.value:
            self.show_plot(e)
        else:
            self.remove_plot(e)

# Plot region end

# main page region
   
    def build(self):
        # page settings
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.auto_scroll = True
        self.page.theme_mode = "dark"
        
        # Buttons

        toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=self.toggle_dark_mode,col={"sm": 6, "md": 4,"lg": 2},)
        new_recipe_button = ft.ElevatedButton("New Recipe", on_click=self.new_recipe, col={"sm": 6, "md": 4, "lg": 2},)
        switch_plot_button = ft.Switch(label = "Show Plot", on_change = self.plot_change, col={"sm": 6, "md": 4, "lg": 2})
        
        
        compute_button = self.create_floating_button(ft.icons.CALCULATE, self.compute, "Compute", ft.colors.GREEN_500, left=  10)
        add_button = self.create_floating_button(ft.icons.ADD, self.add_row, "Add new row", ft.colors.BLUE_200, right =120)
        delete_button = self.create_floating_button(ft.icons.REMOVE, self.delete_row, "Delete row",  ft.colors.RED_200,right =10)
        
        self.page.overlay.extend([compute_button,add_button, delete_button])
    
        # name of the recipe
        self.recipe_name = ft.TextField(
            label="Recipe Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col=12)
        

        self.page.add(ft.ResponsiveRow([new_recipe_button,toggle_dark_mode_button,switch_plot_button]))
        self.page.add(ft.ResponsiveRow([self.recipe_name]))


 
    # Function to create a floating button
    def create_floating_button(self, icon, on_click, tooltip, bgcolor, top=None, bottom=20, right=None, left=None):
        return ft.FloatingActionButton(
            content=ft.Row([ft.Icon(icon)], alignment="center", spacing=5),
            on_click=on_click,
            shape=ft.RoundedRectangleBorder(radius=5),
            width=100,
            mini=True,
            tooltip=tooltip,
            bgcolor=bgcolor,
            top=top,
            bottom=bottom,
            right=right,
            left = left
            
        )

    def toggle_dark_mode(self, e):
        self.page.auto_scroll = False
        new_border_color = "white" if self.page.theme_mode == "light" else "black"
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.recipe_name.border_color = new_border_color
        
        for row in self.input_rows:
            name_input, amount_input = row.controls
            name_input.border_color = new_border_color
            if not (amount_input.border_color == "red"):
                amount_input.border_color = new_border_color
        
        self.page.update()
        self.page.auto_scroll = True
        

    def compute(self, e):
        
        # stops the user from clicking the compute button multiple times
        if self.computing:
            self.popup_snackbar("Please wait until the computation is finished", ft.colors.RED_200)
            return
        
        # delete the output text and the plot
        self.remove_all_output(e)

        # get the inputs from the user
        inputs = self.get_inputs()
        
        ingredients = [item[0] for item in inputs]
        values_input = [float(item[1]) if item[1] != '' else None for item in inputs]

        Nutrients =  None       # Nutrients should be provided in the input later on
        if Nutrients == None:
            Nutrients = [0,0,0,0,0,0]

        if not self.validate_input(values_input):
            return

        # set the computing flag to True
        self.computing = True
        
        SAMPLES, samples_plot = Input.createMatrices(ingredients, values_input, Nutrients, self.page)
        self.plot = samples_plot
        
        # Output the results
        self.output(SAMPLES,ingredients)
        self.remove_plot(e)
        
        
        # set the computing flag to False
        self.computing = False 

   
    def validate_input(self, values_input):
        if sum([float(value) if value != None else 0 for value in values_input]) >= 1:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("The given amounts should be less than 1"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return False
        return True
        
        
    def output(self, samples, ingredients):
        mean_sample = np.mean(samples, axis=0)
        std_sample = np.std(samples, axis=0)
        textSize = 11
        textSize2 = 14
        
        recipe_name = self.recipe_name.value
        length = len(ingredients)
        
        self.text_elements = [
            Text("Dish: " + recipe_name, size = textSize2),
            Text(f"{length} ingredients in total", size = textSize2),
            Text("=" * 55, size = textSize)
            ]
        for i, zutat in enumerate(ingredients):
            self.text_elements.append(Text("{:>42}".format(zutat) + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%", size = textSize))
        self.text_elements.append(Text("=" * 55, size = textSize))
        
        
        for element in self.text_elements:
            self.page.add(element)
        
    def delete_output_text(self):
        if self.text_elements:
            for i in range(len(self.text_elements)):
                self.page.remove(self.text_elements.pop())
                self.page.update()
                        
    def remove_all_output(self,e):
        self.delete_output_text()
        self.remove_plot(e)
        
        #TODO: Fix this
        #self.plot_change(e) 
        
    # delete all output text and plot
    def new_recipe(self, e):
        self.recipe_name.value = ""
        self.remove_all_output(e)
        if self.input_rows:
            for row in self.input_rows:
                self.page.remove(row)
                self.page.update()
            self.input_rows = []
        self.page.update()
    
    # Function to show a snackbar wich pops up from the bottom of the screen and shows a message
    def popup_snackbar(self, text, color):
        self.page.show_snack_bar(
            ft.SnackBar(
                ft.Text(text), 
                open=True,
                bgcolor= color)
            )
    
        
def main(page: ft.Page):
    main_page = MainPage(page)
    main_page.build()
 
# Swap between the two lines below to run the app in the browser or in the terminal   
ft.app(main, assets_dir="./backend/plots")   
# ft.app(main, view=ft.AppView.WEB_BROWSER, assets_dir="./backend/plots")