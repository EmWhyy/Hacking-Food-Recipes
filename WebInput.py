import flet as ft
import numpy as np
from flet import TextField,ElevatedButton, Text
import sys
import os
import backend.Input as Input

class MainPage:
    def __init__(self, page):
        self.page = page
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.text_elements = []
        self.input_rows = []
        self.plots = []
        self.computing = False
        
# Input region 

    # Function to add a row
    def add_row(self, e):

        if len(self.plots) > 0 or len(self.text_elements) > 0:
            self.remove_all_output(e)

        name_input = ft.TextField(
            label="Ingredient Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col={"xs": 7.416,"md":3.708 }
            )
        
        amount_input = ft.TextField(
            label="Amount",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            on_change= self.textbox_changed,
            keyboard_type=ft.KeyboardType.NUMBER,
            height = 80,
            col={"xs": 4.584, "md": 2.292}
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
 # Function to show the plots  
    def show_plots(self,e):
        self.page.auto_scroll = False
        plots_path = os.path.join(self.path, 'backend', 'plots')
        # test if the file exists
        image_files = ["graph.png", "Samples.png", "matrices.png"]
        if len(self.plots) > 0:
            return

        for file in image_files:
            if os.path.exists(plots_path + "/" + file):
                img = ft.Image(
                    src=file,
                    width=900,
                    height=350,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=1,
                )
                self.plots.append(img)
                self.page.add(img)
                self.page.update()
                
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        ft.Text("Plots not found!"), 
                        open=True,
                        bgcolor=ft.colors.RED_200)
                    )
        self.page.auto_scroll = True
    
    def remove_plots(self,e):
        if len(self.plots) > 0:
            for i in range(len(self.plots)):
                self.page.remove(self.plots.pop())
            self.page.update()
                
    def plots_change(self, e):
        if e.control.value:
            self.show_plots(e)
        else:
            self.remove_plots(e)

# Plot region end

# main page region
   
    def build(self):
        # page settings
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.auto_scroll = True
        self.page.theme_mode = "dark"
        
        # Buttons and Recipe-Field
        # screen is divided into 12 colums for all sizes
        # "md": 3 means this button takes up 3 of these 12 colums on medium screens and larger
        colums_ElevatedButton = {"xs": 12,"md": 2.472} 
        colums_Switch = {"xs": 6, "md": 2.472}
        colums_Recipe = {"xs": 12, "md": 6}

        toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=self.toggle_dark_mode,col=colums_ElevatedButton)
        new_recipe_button = ft.ElevatedButton("New Recipe", on_click=self.new_recipe, col=colums_ElevatedButton,)
        switch_plots_button = ft.Switch(label = "Show Plots", on_change = self.plots_change, col=colums_Switch )
        
        
        compute_button = self.create_icon_button(ft.icons.CALCULATE, 48, self.compute, "Compute")
        add_button = self.create_icon_button(ft.icons.ADD, 40, self.add_row, "Add new ingredient")
        delete_button = self.create_icon_button(ft.icons.REMOVE, 40, self.delete_row, "Delete ingredient")

        self.page.bottom_appbar = ft.BottomAppBar(
            height = 64,
            content= ft.Row([add_button, delete_button,ft.Container(expand=True), compute_button]),
            padding = ft.padding.symmetric(horizontal=8)
        )
        
    
        # name of the recipe
        self.recipe_name = ft.TextField(
            label="Recipe Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col = colums_Recipe)
        

        self.page.add(ft.ResponsiveRow([new_recipe_button,toggle_dark_mode_button,switch_plots_button]))
        self.page.add(ft.ResponsiveRow([self.recipe_name]))


 
    # Function to create a iconbutton
    def create_icon_button(self, icon, icon_size, on_click, tooltip):
        return ft.IconButton(
            icon = icon,
            icon_size = icon_size,
            on_click=on_click,
            tooltip=tooltip
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
        
        # delete the output text and the plots
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
        
        SAMPLES = Input.createMatrices(ingredients, values_input, Nutrients, self.page)
        
        # Output the results
        self.output(SAMPLES,ingredients)
        self.remove_plots(e)
        
        
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
        self.remove_plots(e)
        
        #Fix this
        #self.plots_change(e) 
        
    # delete all output text and plots
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