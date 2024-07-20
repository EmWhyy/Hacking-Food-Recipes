We finedtuned our own model because none of the models we could find on Huggingface were working for our usecase.

We used the https://recipenlg.cs.put.poznan.pl Database to finetune a flan-t5 model. 
To avoid long loading times and relieve some stress of off our less than optimal server we chose to use a small version with around 77 Million Parameters.
