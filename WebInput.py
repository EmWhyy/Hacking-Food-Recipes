import flet as ft
import numpy as np
from flet import Text
from flet.matplotlib_chart import MatplotlibChart

import os
import backend.Input as Input

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("svg")
tutorial_shown = False

class TutorialWindow:
    def __init__(self, page):
        self.page = page
        self.slides = [
            {"image": "quby-high-five.png", "text": "Welcome to our Recipe Calculator! \nThis application helps you calculate the optimal ingredient ratios for your recipes.\nStart by entering the name of your recipe and then add your ingredients along with their quantities."},
            {"image": "tutorial_recipe_name.png", "text": "Enter the name of your recipe at the top.\nThis serves as the title and is the first step in creating a new recipe."},
            {"image": "tutorial_valid_input.png", "text": "Here you can input the ingredients of your recipe along with their quantities.\nEnter the quantities as decimal numbers (e.g., 0.6 for 60%).\nThis forms the basis for the recipe calculations."},
            {"image": "tutorial_new_recipe.png", "text": "The 'New Recipe' button at the top left clears all outputs and lets you start fresh.\nThis is useful when you want to create a new recipe from scratch."},
            {"image": "tutorial_toggle_darkmode.png", "text": "The 'Toggle Dark Mode' button switches the appearance of the page between a light and dark mode according to your preference."},
            {"image": "tutorial_toggle_plotbuttons.png", "text": "The 'Show Plots' switch displays graphs of our 100 samples (various ingredient ratios).\nThis provides a visual representation of the calculated results."},
            {"image": "tutorial_add_and_remove_button.png", "text": "The blue and red buttons at the bottom right add or remove input rows.\nHere you can enter ingredient names and their quantities in decimal form."},
            {"image": "tutorial_compute_button.png", "text": "The green button at the bottom left starts the calculation.\nThis is the most important step to analyze the entered ingredient ratios and get the results."},
            {"image": "tutorial_tutorial_button.png", "text": "The 'i' button brings you back to the tutorial.\nThis is helpful if you need a refresher on how to use the application."},

        ]
        self.current_slide = 0
        self.image = ft.Image(src=self.slides[self.current_slide]["image"])
        self.text = ft.Text(self.slides[self.current_slide]["text"])
        self.dialog = None

    def close_tutorial(self, e):
        self.page.dialog.open = False
        self.page.update()

    def update_slide(self):
        slide = self.slides[self.current_slide]
        self.image.src = slide["image"]
        self.text.value = slide["text"]
        self.page.update()

    def next_slide(self, e):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.update_slide()

    def previous_slide(self, e):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.update_slide()

    def show(self):
        close_button = ft.IconButton(icon=ft.icons.CLOSE, on_click=self.close_tutorial)
        prev_button = ft.IconButton(icon=ft.icons.CHEVRON_LEFT, on_click=self.previous_slide)
        next_button = ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, on_click=self.next_slide)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column([
                    ft.Row([ft.Container(), close_button], alignment=ft.MainAxisAlignment.END),
                    ft.Container(content=ft.Column([self.image, self.text]),alignment=ft.alignment.center,expand=True),
                    ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)          
                ]),
                alignment=ft.alignment.center,
                width=1200,
                height=800
            )
        )
        self.page.dialog.open = True
        self.page.update()

class MainPage:
    def __init__(self, page):
        self.page = page
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.text_elements = []
        self.input_rows = []
        self.plot = None
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
            if (self.plot is not None) or len(self.text_elements) > 0:
                self.remove_all_output(e)
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
 
    def compute_plot(self, SAMPLES, ingredients):
        
        mean_sample = np.mean(SAMPLES, axis=0)
        std_sample = np.std(SAMPLES, axis=0)
        
        fig, ax = plt.subplots()
        ax.bar(ingredients, mean_sample * 100, align='center', color='black', alpha=0.5, ecolor='black', capsize=10)
        ax.errorbar(ingredients, mean_sample * 100, yerr=std_sample * 100, fmt='none', ecolor='red', capsize=5)

        ax.set_ylabel('Porportion of Ingredients')
        ax.set_title('Mean and Standard Deviation of Ingredients in the Recipe')
        ax.set_ylim(0,100) 
        
        # legend 
        ax.legend(["Mean", "Standard Deviation"], loc='upper right')
        
        chart_container = ft.Container(
            content=MatplotlibChart(fig, expand=True),
            width=600,  
            height=400
            )
        
        self.plot = chart_container
        self.page.add(self.plot)
        
        
    def show_plot(self,e):
        if (self.plot != None):
            self.page.add(self.plot)
        else:
            self.popup_snackbar("No Plot to show", ft.colors.RED_200)
        
    def remove_plot(self,e):
        # if (self.plot != None):
        #     self.page.remove(self.plot)
        #     self.page.update()
        pass
                
    def plot_change(self, e):
        # if e.control.value:
        #     self.show_plot(e)
        # else:
        #     self.remove_plot(e)
        pass

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
        switch_plots_button = ft.Switch(label = "Show Plots", on_change = self.plot_change, col=colums_Switch )
        tutorial_button = ft.ElevatedButton(content=ft.Icon(ft.icons.INFO), on_click=lambda e: TutorialWindow(self.page).show(), col={"sm": 6, "md": 4, "lg": 2})
        
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
        

        self.page.add(ft.ResponsiveRow([new_recipe_button,toggle_dark_mode_button,switch_plots_button, tutorial_button]))
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
        
        SAMPLES = Input.createMatrices(ingredients, values_input, Nutrients, self.page)
        self.compute_plot(SAMPLES, ingredients)
        
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
    
    # Function to show a snackbar which pops up from the bottom of the screen and shows a message
    def popup_snackbar(self, text, color):
        self.page.show_snack_bar(
            ft.SnackBar(
                ft.Text(text), 
                open=True,
                bgcolor= color)
            )
    
        
def main(page: ft.Page):
    global tutorial_shown
    
    main_page = MainPage(page)
    main_page.build()
    
    # Show the tutorial window on first launch
    if not tutorial_shown:
        tutorial = TutorialWindow(page)
        tutorial.show()
        tutorial_shown = True


# Swap between the two lines below to run the app in the browser or in the terminal   
ft.app(main, assets_dir="./backend/tutorial_pictures")   
# ft.app(main, view=ft.AppView.WEB_BROWSER, assets_dir="./backend/tutorial_pictures")