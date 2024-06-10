import transformers
import numpy as np


class Model:
    def __init__(self):
        self.model = transformers.pipeline("text2text-generation", model="flax-community/t5-recipe-generation")

    def __createRecipe(self, text):
        return self.model(text)
    
    def getRecipe(self, prompt):
        output = self.__createRecipe(prompt)

        output = output[0]['generated_text'].split('directions:')[1]
        return output
    
def createPrompt(recipeName, ingredients, meanOfSamples):
    prompt = f"Title: {recipeName}; Ingredients:"
    meanOfSamples = np.round(meanOfSamples, 2)
    for i, ingredient in enumerate(ingredients):
        prompt += f" {ingredient}," if i != len(ingredients) - 1 else f" {ingredient}."
        # {meanOfSamples[i]}
    return prompt