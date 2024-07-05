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
        self.text_elements = None
        self.input_rows = []
        self.plot = None
        self.computing = False
        
# Input region 

    # Function to add a row
    def add_row(self, e):


        if (self.plot is not None) or (self.text_elements is not None):
            self.remove_all_output(e)

        name_input = ft.TextField(
            label="Ingredient Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col={"xs": 7.416,"md":6 }
            )
        
        amount_input = ft.TextField(
            label="Amount",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            on_change= self.textbox_changed,
            keyboard_type=ft.KeyboardType.NUMBER,
            height = 80,
            col={"xs": 4.584, "md": 3}
            )
        
        input_row = ft.ResponsiveRow([name_input, amount_input], alignment = ft.MainAxisAlignment.CENTER)
        self.input_rows.append(input_row)
        self.page.add(input_row)
        
    # Checks the textbox input for valid numbers
    def textbox_changed(self, e):
        try:
            # Check if the input is empty
            if e.control.value.strip() == "": 
                e.control.border_color = None  
                e.control.helper_text = None
            else:
                input = float(e.control.value)
                e.control.border_color = "white"
                e.control.helper_text = None
        except:
            e.control.border_color = "red"
            e.control.helper_text = "Please enter a number"
        
        self.page.update()

    
    # Function to delete a row
    def delete_row(self, e):
        
        if (self.plot is not None) or (self.text_elements is not None):
            self.remove_all_output(e)
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
 
    def compute_plot(self, SAMPLES, ingredients):
        color = "white" if self.page.theme_mode == "dark" else "black"
        
        mean_sample = np.mean(SAMPLES, axis=0)
        std_sample = np.std(SAMPLES, axis=0)
        
        fig, ax = plt.subplots()
        
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        ax.bar(ingredients, mean_sample * 100, align='center', color='#0b105c', alpha=0.7, ecolor='none', capsize=10)
        ax.errorbar(ingredients, mean_sample * 100, yerr=std_sample * 100, fmt='none', ecolor='#FF5722', capsize=5)


        ax.set_ylabel('Proportion of Ingredients', color=color)
        ax.set_title('Mean and Standard Deviation of Ingredients in the Recipe', color=color)
        # Set axis ticks and labels to white
        ax.tick_params(axis='x', colors=color)
        ax.tick_params(axis='y', colors=color)
        ax.yaxis.label.set_color(color)
        ax.xaxis.label.set_color(color)
        
        
        ax.legend(["Mean", "Standard Deviation"], loc='upper right', facecolor='#333333', edgecolor='none', labelcolor=color)
        ax.set_ylim(0,100) 
    
        
        chart_container = ft.Container(
            content=MatplotlibChart(fig, expand=True),
            width=600,  
            height=400
            )
        
        panel = ft.ExpansionPanelList(
            expand_icon_color=ft.colors.BLUE,
            elevation=8,
            controls=[
                ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text("Plot of the Recipe")),
                    content=chart_container,
                )
            ]
        )        
        self.plot = panel
        self.page.add(self.plot)
        
        
        # oder boxplot
        # color = "white" if self.page.theme_mode == "dark" else "black"
        
        # fig, ax = plt.subplots()
        
        # fig.patch.set_facecolor('none')
        # ax.set_facecolor('none')

        # # Create boxplots
        # box = ax.boxplot(SAMPLES * 100, patch_artist=True,
        #                  boxprops=dict(facecolor='#0b105c', color=color),
        #                  capprops=dict(color=color),
        #                  whiskerprops=dict(color=color),
        #                  flierprops=dict(markeredgecolor=color),
        #                  medianprops=dict(color='#FF5722'))

        # # Set labels and title
        # ax.set_xticks(np.arange(1, len(ingredients) + 1))
        # ax.set_xticklabels(ingredients, rotation=45, ha="right", color=color)
        # ax.set_ylabel('Proportion of Ingredients', color=color)
        # ax.set_title('Boxplots of Ingredients in the Recipe', color=color)

        # # Set axis ticks and labels to the appropriate color
        # ax.tick_params(axis='x', colors=color)
        # ax.tick_params(axis='y', colors=color)
        # ax.yaxis.label.set_color(color)
        # ax.xaxis.label.set_color(color)

        # ax.set_ylim(0, 100)

        # chart_container = ft.Container(
        #     content=MatplotlibChart(fig, expand=True),
        #     width=600,  
        #     height=400
        # )
        
        # panel = ft.ExpansionPanelList(
        #     expand_icon_color=ft.colors.BLUE,
        #     elevation=8,
        #     controls=[
        #         ft.ExpansionPanel(
        #             header=ft.ListTile(title=ft.Text("Plot of the Recipe", color=color)),
        #             content=chart_container,
        #         )
        #     ]
        # )
        
        # self.plot = panel
        # self.page.add(self.plot)
        
    def remove_plot(self):
        if self.plot is not None and self.plot in self.page.controls:
            self.page.remove(self.plot)
            self.page.update()
            self.plot = None
        
                

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
        colums_ElevatedButton = {"xs": 12,"md": 2.25} 
        colums_Recipe = {"xs": 12, "md": 9}

        toggle_dark_mode_button = ft.ElevatedButton("Toggle Dark Mode", on_click=self.toggle_dark_mode,col=colums_ElevatedButton)
        new_recipe_button = ft.ElevatedButton("New Recipe", on_click=self.new_recipe, col=colums_ElevatedButton,)
        tutorial_button = ft.ElevatedButton(content=ft.Icon(ft.icons.INFO), on_click=lambda e: TutorialWindow(self.page).show(), col=colums_ElevatedButton)

        
        compute_button = self.create_icon_button(ft.icons.CALCULATE, 48, self.compute, "Compute")
        add_button = self.create_icon_button(ft.icons.ADD, 40, self.add_row, "Add new ingredient")
        delete_button = self.create_icon_button(ft.icons.REMOVE, 40, self.delete_row, "Delete ingredient")

        self.page.bottom_appbar = ft.BottomAppBar(
            height = 64,
            content= ft.Row([add_button, delete_button,ft.Container(expand=True), compute_button]),
            padding = ft.padding.symmetric(horizontal=8)
        )
        
        self.recipe_name = ft.TextField(
            label="Recipe Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col = {"xs": 7.416,"md":7 })
        
        self.recipe_whole_amount = ft.TextField(
            label="Dish Amount in gramm",
            hint_text="Standart 100",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            on_change= self.textbox_changed,
            height = 80,
            col = {"xs": 4.584, "md":2 }
            )
        
        self.page.add(ft.ResponsiveRow([new_recipe_button,toggle_dark_mode_button, tutorial_button], alignment = ft.MainAxisAlignment.CENTER))
        self.page.add(ft.ResponsiveRow([self.recipe_name, self.recipe_whole_amount], alignment = ft.MainAxisAlignment.CENTER))


 
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
        
        # get the inputs from the user
        inputs = self.get_inputs()

        ingredients = []
        empty_counter = 1
        # fill missing ingredient names with "ingredient miss x"
        for item in inputs:
            if item[0] == "":
                ingredients.append(f"ingredient miss {empty_counter}")
                empty_counter += 1
            else:
                ingredients.append(item[0])
        
        try:
            values_input = [float(item[1].strip()) if item[1].strip() != '' else None for item in inputs]
        except:
            self.popup_snackbar("Please enter a number", ft.colors.RED_200)
            return


        Nutrients =  None       # Nutrients should be provided in the input later on
        if Nutrients == None:
            Nutrients = [0,0,0,0,0,0]

        if not self.validate_input(values_input,ingredients):
            return

        # set the computing flag to True
        self.computing = True
        
        # delete the output text and the plot
        self.remove_all_output(e)
        
        SAMPLES = Input.createMatrices(ingredients, values_input, Nutrients, self.page)
       
        # Output the results
        self.output(SAMPLES,ingredients)
        self.compute_plot(SAMPLES, ingredients)

        # set the computing flag to False
        self.computing = False 

   
    def validate_input(self, values_input, ingredients):
        if sum([float(value) if value != None else 0 for value in values_input]) >= 1:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("The given amounts should be less than 1"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return False
        
        # check if the ingredient names are unique
        n = len(ingredients)
        for i in range(n):
            for j in range(i + 1, n):
                if ingredients[i] == ingredients[j]:
                    self.popup_snackbar("Please enter non-repeating ingredient names", ft.colors.RED_200)
                    return False
     
        return True
        
        
    def output(self, samples, ingredients):

        mean_sample = np.mean(samples, axis=0)
        std_sample = np.std(samples, axis=0)
        textSize = 15  
        recipe_name = ft.Text("Dish: " + self.recipe_name.value, theme_style=ft.TextThemeStyle.TITLE_MEDIUM)
        rows = []

        # catching wrong input for the dish amount
        whole_amount = self.recipe_whole_amount.value
        if whole_amount == "":
            whole_amount = "100"
        if not whole_amount.isdigit():
            whole_amount = "100"
            self.popup_snackbar("Please enter a number for the dish amount", ft.colors.RED_200)
            
        for i, ingredient in enumerate(ingredients):
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(ingredient, size=textSize)),
                ft.DataCell(ft.Text(f"{round(mean_sample[i] * int(whole_amount))}g", size=textSize)),
                ft.DataCell(ft.Text(f"{mean_sample[i] * 100:5.2g}%", size=textSize)),
                ft.DataCell(ft.Text(f"+/- {2 * std_sample[i] * 100:4.2f}%", size=textSize))
            ]))
            output_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Ingredient", size=textSize, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Amount", size=textSize, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Percentage", size=textSize, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Deviation", size=textSize, weight=ft.FontWeight.BOLD)),
                ],
                rows = rows,
                
            )
        
        self.text_elements = ft.Column([
                ft.Container(content=recipe_name, alignment=ft.alignment.center),
                ft.Container(content=output_table, alignment=ft.alignment.center),
            ],)
        
        self.page.add(self.text_elements)

        
    def delete_output_text(self):
        if self.text_elements is not None:
            self.page.remove(self.text_elements)
            self.text_elements = None

                        
    def remove_all_output(self,e):
        self.remove_plot()
        self.delete_output_text()
        
        

        
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
#ft.app(main, view=ft.AppView.WEB_BROWSER, assets_dir="./backend/tutorial_pictures")
