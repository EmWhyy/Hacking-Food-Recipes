import flet as ft
import numpy as np
from flet import Text
from flet.matplotlib_chart import MatplotlibChart

import os
import backend.Input as Input
import backend.recipe.createRecipe as createRecipe

import matplotlib
import matplotlib.pyplot as plt
 
matplotlib.use("svg")
tutorial_shown = False


class TutorialWindow:
    def __init__(self, page):
        self.page = page
        self.slides = [
            {"image": "quby-high-five.png", "text": "Welcome to our Recipe Calculator! \nThis application helps you calculate the optimal ingredient ratios for your recipes.\nStart by entering the name of your recipe and then add your ingredients along with their quantities."},
            {"image": "tutorial_dish_amount.png", "text": "Here you can input the amount of the dish in grams.\nThis is useful to calculate the amount of each ingredient in the recipe.\nIf you don't enter a value, the default value is 100 grams."},
            {"image": "tutorial_valid_input.png", "text": "Here you can input the ingredients of your recipe along with their quantities.\nEnter the quantities as decimal numbers (e.g., 0.6 for 60%).\nThis forms the basis for the recipe calculations."},
            {"image": "tutorial_valid_output+plots.png", "text": "This is how a possible recipe output looks like.\nYou will see the mean and standard deviation of the ingredients in the recipe.\nAdditionally, you will see a plot of the ingredients in the recipe.\nThis helps you to visualize the ingredient ratios and their deviations."},            
            {"image": "tutorial_ai_output.png", "text": "Here you can see the ai-output button that explains how to make actually make the desired dish."},
            {"image": "tutorial_add_and_remove_button.png", "text": "The blue and red buttons at the bottom right add or remove input rows.\nHere you can enter ingredient names and their quantities in decimal form."},
            {"image": "tutorial_compute_button.png", "text": "The green button at the bottom left starts the calculation.\nThis is the most important step to analyze the entered ingredient ratios and get the results."},
            {"image": "tutorial_new_recipe.png", "text": "The 'New Recipe' button at the top left clears all outputs and lets you start fresh.\nThis is useful when you want to create a new recipe from scratch."},
            {"image": "tutorial_toggle_darkmode.png", "text": "This button switches the appearance of the page between a light and dark theme according to your preference."},
            {"image": "tutorial_tutorial_button.png", "text": "The 'i' button brings you back to the tutorial.\nThis is helpful if you need a refresher on how to use the application."}
        ]
        self.current_slide = 0
        self.image = ft.Image(src=self.slides[self.current_slide]["image"])
        self.text = ft.Text(self.slides[self.current_slide]["text"])
        self.dialog = None

    def close_tutorial(self, e=None):
        self.page.dialog.open = False
        self.page.update()

    def update_slide(self):
        slide = self.slides[self.current_slide]
        self.image.src = slide["image"]
        self.text.value = slide["text"]
        self.image.update()
        self.text.update()

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
        
        # Calculate window size based on the main window size
        tutorial_width = self.page.width * 0.7
        tutorial_height = self.page.height * 0.7
    
        self.page.dialog = ft.AlertDialog(
            content=ft.Container(
                width=tutorial_width,
                height=tutorial_height,
                padding=ft.padding.all(10),
                content=ft.Column([
                    ft.Row([close_button],
                            alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(content=self.image, alignment=ft.alignment.center, expand=3),
                    ft.Container(content=self.text, alignment=ft.alignment.center, expand=1),
                    ft.Row([prev_button, next_button],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                ]),
                alignment=ft.alignment.center,
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
        self.model = createRecipe.Model()
        self.name = None
        self.ingredients = []
        self.mean_sample = None
        self.ai_output = None
        self.SAMPLE = None
        
# Input region 

    # Function to add a row
    def add_row(self, e):

        if (self.plot is not None) or (self.text_elements is not None) or (self.ai_output is not None):
            self.remove_all_output(e)

        name_input = ft.TextField(
            label="Ingredient Name",
            border_color= "black" if self.page.theme_mode == "light" else "white",
            height = 80,
            col={"xs": 7.416,"md":6 }
            )
        
        amount_input = ft.TextField(
            label="Amount in %",
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
        
        if (self.plot is not None) or (self.text_elements is not None) or (self.ai_output is not None):
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
 
    def compute_plot(self):
        color = "white" if self.page.theme_mode == "dark" else "black"
        
        mean_sample = np.mean(self.SAMPLES, axis=0)
        std_sample = np.std(self.SAMPLES, axis=0)
        
        fig, ax = plt.subplots()
        
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        ax.bar(self.ingredients, mean_sample * 100, align='center', color='#0b105c', alpha=0.7, ecolor='none', capsize=10)
        ax.errorbar(self.ingredients, mean_sample * 100, yerr=std_sample * 100, fmt='none', ecolor='#FF5722', capsize=5)


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
        ai_output_button = ft.ElevatedButton("AI output", on_click=self.createRecipe, col=colums_ElevatedButton)

        
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
        
        self.page.add(ft.ResponsiveRow([new_recipe_button,toggle_dark_mode_button,ai_output_button, tutorial_button], alignment = ft.MainAxisAlignment.CENTER))
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

        self.ingredients = []
        empty_counter = 1
        # fill missing ingredient names with "ingredient miss x"
        for item in inputs:
            if item[0] == "":
                self.ingredients.append(f"ingredient miss {empty_counter}")
                empty_counter += 1
            else:
                self.ingredients.append(item[0])
        
        try:
            values_input = [float(item[1].strip())/100 if item[1].strip() != '' else None for item in inputs]
        except:
            self.popup_snackbar("Please enter a number", ft.colors.RED_200)
            return


        Nutrients =  None       # Nutrients should be provided in the input later on
        if Nutrients == None:
            Nutrients = [0,0,0,0,0,0]

        if not self.validate_input(values_input):
            return

        # set the computing flag to True
        self.computing = True
        
        # delete the output text and the plot
        self.remove_all_output(e)
        
        self.SAMPLES = Input.createMatrices(self.ingredients, values_input, Nutrients, self.page)
       
        # Output the results
        self.output()
        self.compute_plot()

        # set the computing flag to False
        self.computing = False 

   
    def validate_input(self, values_input):
        max_index = len(values_input) - 1

        #if every amount is given
        
        if not None in values_input:
            if sum(values_input) != 1:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        ft.Text("The amounts are given and do not add up to 100%! Please adjust your inputs!"), 
                        open=True,
                        bgcolor=ft.colors.RED_200)
                    )
                return False
            return True


        #checking whether the order of values is correct

        temp = values_input.copy()
        temp = [value for value in temp if value is not None]
        for ind in range(len(temp)):
            if(temp[ind] > temp[max(0, ind - 1)]):
                self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("Amounts are not in the right order! Please adjust your inputs!"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
                 )
                return False

        #get minimum value of the inputs and check if its under 100%

        temp = values_input.copy()
        for ind in range(len(values_input)):
            if values_input[max_index - ind] == None:
                if max_index - ind + 1 < len(values_input):
                    temp[max_index - ind] = temp[max_index - ind + 1]
                else:
                    temp[max_index - ind] = 0
        if sum([float(value) for value in temp]) > 1:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("With those amounts the total amount is going to be over 100%! Please adjust your inputs!"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return False
        

        #get maximum value of the inputs and check if its over 100%
        if values_input[0] == None:
            return True

        temp = values_input.copy()
        for ind in range(len(values_input)):
            if values_input[ind] == None:
                if ind - 1 >= 0:
                    temp[ind] = temp[ind - 1]
                else:
                    temp[ind] = 0
        #print(temp)
        if sum([float(value) for value in temp]) < 1:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("With those amounts the total amount is going to be under 100%! Please adjust your inputs!"), 
                    open=True,
                    bgcolor=ft.colors.RED_200)
            )
            return False
        
        # check if the ingredient names are unique
        n = len(self.ingredients)
        for i in range(n):
            for j in range(i + 1, n):
                if self.ingredients[i] == self.ingredients[j]:
                    self.popup_snackbar("Please enter non-repeating ingredient names", ft.colors.RED_200)
                    return False
     
        return True
        
        
    def output(self):

        self.mean_sample = np.mean(self.SAMPLES, axis=0)
        std_sample = np.std(self.SAMPLES, axis=0)
        textSize = 15  
        recipe_name = ft.Text("Dish: " + self.recipe_name.value, theme_style=ft.TextThemeStyle.TITLE_MEDIUM)
        rows = []

        self.name = self.recipe_name.value

        # catching wrong input for the dish amount
        whole_amount = self.recipe_whole_amount.value
        if whole_amount == "":
            whole_amount = "100"
        if not whole_amount.isdigit():
            whole_amount = "100"
            self.popup_snackbar("Please enter a number for the dish amount", ft.colors.RED_200)
            
        for i, ingredient in enumerate(self.ingredients):
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(ingredient, size=textSize)),
                ft.DataCell(ft.Text(f"{round(self.mean_sample[i] * int(whole_amount))}g", size=textSize)),
                ft.DataCell(ft.Text(f"{self.mean_sample[i] * 100:5.2g}%", size=textSize)),
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



    def createRecipe(self,e):
        if self.name is None or self.ingredients is None or self.mean_sample is None:
            self.popup_snackbar("There is no recipe to create", ft.colors.RED_200)
            return
        if self.ai_output is not None:
            self.page.remove(self.ai_output)
            self.ai_output = None
            
        self.remove_plot()
        prompt = createRecipe.createPrompt(self.name, self.ingredients, self.mean_sample)
        print(prompt)
        recipe = self.model.getRecipe(prompt)
        print(recipe)
        test = ft.Text(f"AI Output:", weight=ft.FontWeight.BOLD, size=15)
        reccipe = ft.Text(recipe, weight=ft.FontWeight.W_400, size=15)
        self.ai_output = ft.Container(
            content=ft.Column([test, reccipe]),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )
        self.page.add(self.ai_output)
        self.compute_plot()
        


        
    def delete_output_text(self):
        if self.text_elements is not None:
            self.page.remove(self.text_elements)
            if self.ai_output is not None:
                self.page.remove(self.ai_output)
                self.ai_output = None
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
#ft.app(main, assets_dir="./backend/tutorial_pictures")   
ft.app(main, view=ft.AppView.WEB_BROWSER, assets_dir="./backend/tutorial_pictures")
