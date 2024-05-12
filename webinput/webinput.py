import flet as ft
from flet import TextField,ElevatedButton


def main(page: ft.Page):
    # List to store input rows
    input_rows = []

    def add_row(e):
        # Function to add a new row
        name_input = ft.TextField(label="Provide name")
        number_input = ft.TextField(label="Provide number")
        input_row = ft.Row([name_input, number_input])
        input_rows.append(input_row)
        page.add(input_row)

    def compute(e):
        # Function to compute and display the inputs
        inputs = []
        for row in input_rows:
            name_input, number_input = row.controls  # Unpack the controls within the row
            inputs.append((name_input.value, number_input.value))  # Get values from the text fields
        print("Inputs:", inputs)

    # Button to add a new row
    add_button = ft.ElevatedButton("Add Row", on_click=add_row)

    # Button to compute inputs
    compute_button = ft.ElevatedButton("Compute", on_click=compute)

    # Add the buttons to the page
    page.add(ft.Row([add_button, compute_button]))

ft.app(main)
