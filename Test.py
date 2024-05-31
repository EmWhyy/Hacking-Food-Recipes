import backend.Input as Input

Ingredients = [
        "gek. Hülsenfrüchte (braune Berglinsen)",
        "Kokosfett",
        "Sonnenblumenöl",
        "geröstete Zwiebeln (in Sonnenblumenöl)",
        "Zitronensaft",
        "Gewürze",
        "Agavendicksaft",
        "geräuchertes Meersalz",
        "Koriander",
    ]
givenAmounts = [0.63, None, None, None, None, None, None, None, 0.016]
Nutrients = [0,0,0,0,0,0]

Input.createMatrices(Ingredients, givenAmounts, Nutrients, None, "Test")