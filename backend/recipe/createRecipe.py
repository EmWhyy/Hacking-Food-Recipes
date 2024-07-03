import transformers
import numpy as np


class Model:
    def __init__(self):
        model_id = "MettBrot/flan-t5-small-quaso-gen3"
        self.model = transformers.pipeline("text2text-generation", model=model_id, tokenizer=model_id)

    def __createRecipe(self, text):
        return self.model(text)
    
    def getRecipe(self, prompt):
        output = self.__createRecipe(prompt)
        return output
    
def createPrompt(recipeName, ingredients, meanOfSamples):
    prompt = f"Create a recipe for: Title {recipeName} Ingredients: "
    meanOfSamples = np.round(meanOfSamples, 2)
    for i, ingredient in enumerate(ingredients):
        prompt += f"{ingredient}, " if i != len(ingredients) - 1 else f" {ingredient}."
        # {meanOfSamples[i]}
    return prompt