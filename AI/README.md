We finedtuned our own model because none of the models we could find on Huggingface were working for our usecase.

We used the [RecipeNGL](https://recipenlg.cs.put.poznan.pl) Database to finetune a [Flan-t5](https://huggingface.co/google/flan-t5-small) model. 
To avoid long loading times and relieve some stress of off our less than optimal server we chose to use a small version with around 77 Million Parameters.

The finetuning code isnt completely original we took a base [code](https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/summarization.ipynb) for finetuning a t5 model and adjusted it to our data and model.
