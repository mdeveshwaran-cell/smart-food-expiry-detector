"""
Smart Recipe & Food Waste Reduction Engine
------------------------------------------
Provides targeted recipe suggestions and food preservation advice
for food items expiring soon to prevent waste and save money.
"""

RECIPE_DATABASE = [
    {
        'id': 'rec_french_toast',
        'title': 'Quick Golden French Toast',
        'keywords': ['bread', 'bun', 'loaf', 'bakery'],
        'prep_time': '10 mins',
        'difficulty': 'Easy',
        'description': 'The ultimate way to revitalize stale or expiring bread into a delicious breakfast.',
        'ingredients': ['4 slices of bread', '2 eggs', '1/2 cup milk', '1 tsp cinnamon or sugar', '1 tbsp butter'],
        'steps': [
            'Whisk eggs, milk, and cinnamon together in a shallow dish.',
            'Dip each slice of bread into the egg mixture for 10-15 seconds per side.',
            'Melt butter in a skillet over medium heat.',
            'Cook bread for 2-3 minutes per side until golden brown and crisp.'
        ],
        'waste_tip': 'Bread nearing expiry can also be frozen for up to 3 months or toasted into crunchy salad croutons!'
    },
    {
        'id': 'rec_banana_smoothie',
        'title': 'Energy Boost Banana Smoothie',
        'keywords': ['banana', 'milk', 'yogurt', 'fruit'],
        'prep_time': '5 mins',
        'difficulty': 'Super Easy',
        'description': 'Overripe, spotty bananas are naturally sweet and perfect for thick nutritious smoothies.',
        'ingredients': ['2 ripe bananas', '1 cup milk or yogurt', '1 tbsp honey or peanut butter', 'Ice cubes'],
        'steps': [
            'Peel and slice the bananas.',
            'Combine bananas, milk, and honey in a blender.',
            'Blend on high speed until creamy and frothy.',
            'Pour into a glass and serve cold.'
        ],
        'waste_tip': 'Peel and freeze overripe bananas in ziplock bags; they blend like soft-serve ice cream!'
    },
    {
        'id': 'rec_tomato_pasta_sauce',
        'title': 'Rustic Fresh Tomato Sauce',
        'keywords': ['tomato', 'tomatoes', 'garlic', 'vegetable'],
        'prep_time': '20 mins',
        'difficulty': 'Easy',
        'description': 'Soft or wrinkly tomatoes make the richest, sweetest homemade pasta sauce.',
        'ingredients': ['4-5 ripe tomatoes (chopped)', '2 cloves minced garlic', '2 tbsp olive oil', 'Salt, pepper & dried oregano'],
        'steps': [
            'Heat olive oil in a pan and sauté garlic until fragrant (30 seconds).',
            'Add chopped ripe tomatoes, a pinch of salt, and oregano.',
            'Simmer on low-medium heat for 15-20 minutes until the tomatoes break down into a thick sauce.',
            'Toss with boiled pasta or freeze in jars for future meals.'
        ],
        'waste_tip': 'Do not refrigerate raw unripe tomatoes; store them at room temperature stem-side down.'
    },
    {
        'id': 'rec_veggie_fried_rice',
        'title': 'Clear-the-Fridge Fried Rice',
        'keywords': ['rice', 'carrot', 'onion', 'egg', 'vegetable', 'peas', 'spinach', 'cabbage'],
        'prep_time': '15 mins',
        'difficulty': 'Easy',
        'description': 'Use up leftover cooked rice and any expiring vegetables in your fridge in one savory wok.',
        'ingredients': ['2 cups cooked cold rice', '1 cup mixed chopped veggies', '2 beaten eggs', '2 tbsp soy sauce', '1 tbsp oil'],
        'steps': [
            'Heat oil in a wok or large pan on high heat.',
            'Stir-fry chopped veggies for 3-4 minutes until tender-crisp.',
            'Push veggies aside, pour in beaten eggs, and scramble quickly.',
            'Add cooked rice and soy sauce; toss vigorously for 3 minutes until steaming hot.'
        ],
        'waste_tip': 'Cooked rice can be safely refrigerated for up to 4 days or frozen for 1 month.'
    },
    {
        'id': 'rec_fresh_paneer_curd',
        'title': 'Quick Homemade Cottage Cheese (Paneer)',
        'keywords': ['milk', 'dairy'],
        'prep_time': '20 mins',
        'difficulty': 'Medium',
        'description': 'If you have a liter of milk expiring in 1-2 days, turn it into fresh soft paneer.',
        'ingredients': ['1 liter full-cream milk', '2 tbsp lemon juice or white vinegar'],
        'steps': [
            'Bring milk to a gentle boil in a heavy pot, stirring occasionally.',
            'Turn off the heat and slowly drizzle in lemon juice while stirring.',
            'Watch the curds separate from the greenish whey.',
            'Strain curds through a muslin cloth or fine strainer, rinse with water, and press flat for 20 mins.'
        ],
        'waste_tip': 'Don\'t throw away the whey water—it is packed with protein and great for kneading dough or cooking soups!'
    },
    {
        'id': 'rec_veggie_frittata',
        'title': 'Herb & Veggie Skillet Frittata',
        'keywords': ['egg', 'eggs', 'cheese', 'spinach', 'tomato', 'potato', 'vegetable'],
        'prep_time': '15 mins',
        'difficulty': 'Easy',
        'description': 'The easiest oven/stovetop bake to rescue assorted vegetables and leftover eggs.',
        'ingredients': ['4 eggs', '1/4 cup milk or grated cheese', '1 cup chopped vegetables', '1 tbsp butter or olive oil', 'Salt & pepper'],
        'steps': [
            'Whisk eggs, milk, salt, and pepper in a bowl.',
            'Sauté chopped vegetables in an oven-safe skillet with butter until softened.',
            'Pour whisked eggs over vegetables and cook over low heat for 5 minutes until edges set.',
            'Cover with a lid or broil in oven for 3-5 minutes until the center is cooked through.'
        ],
        'waste_tip': 'Eggs remain safe to consume even 1-2 weeks past printed sell-by dates if they pass the water float test!'
    },
    {
        'id': 'rec_fruit_compote',
        'title': 'Warm Fruit Compote / Jam',
        'keywords': ['apple', 'berry', 'strawberry', 'fruit', 'pear', 'peach'],
        'prep_time': '15 mins',
        'difficulty': 'Easy',
        'description': 'Simmer bruised or soft fruits with a splash of water and honey for pancake and yogurt topping.',
        'ingredients': ['2 cups diced fruits', '2 tbsp sugar or honey', '1 tbsp lemon juice', '2 tbsp water'],
        'steps': [
            'Combine fruits, sugar, lemon juice, and water in a saucepan.',
            'Simmer over medium heat for 10-12 minutes until fruit softens and releases syrup.',
            'Mash slightly with a spoon and let cool.'
        ],
        'waste_tip': 'Keep apples separated from other fruits because apples emit ethylene gas which accelerates ripening.'
    }
]

STORAGE_GUIDELINES = {
    'Dairy': {
        'best_place': 'Back of Refrigerator (Coldest zone, 1°C to 4°C)',
        'advice': 'Never store milk in the refrigerator door shelves where temperature fluctuates most when opened.',
        'freeze_ok': True
    },
    'Fruits': {
        'best_place': 'Fruit Crisper Drawer or Countertop (until ripe)',
        'advice': 'Keep ethylene producers (apples, bananas) separate from sensitive fruits (berries, melons).',
        'freeze_ok': True
    },
    'Vegetables': {
        'best_place': 'High Humidity Crisper Drawer',
        'advice': 'Store greens wrapped in paper towels inside an airtight box to absorb excess condensation.',
        'freeze_ok': True
    },
    'Bakery': {
        'best_place': 'Bread Box or Freezer',
        'advice': 'Do not refrigerate bread as cold temperatures speed up retrogradation (staling). Freeze sliced bread instead.',
        'freeze_ok': True
    },
    'Meat & Poultry': {
        'best_place': 'Bottom shelf of refrigerator (below all ready-to-eat foods)',
        'advice': 'Store in a leak-proof tray. If not cooking within 48 hours, freeze immediately.',
        'freeze_ok': True
    },
    'Grains & Cereals': {
        'best_place': 'Airtight containers in cool, dark pantry',
        'advice': 'Keep away from direct sunlight and humidity to prevent pantry pests and mold.',
        'freeze_ok': False
    },
    'Beverages': {
        'best_place': 'Refrigerator after opening',
        'advice': 'Consume juices within 5-7 days after breaking the seal.',
        'freeze_ok': False
    },
    'Other': {
        'best_place': 'Pantry or Refrigerator depending on package directions',
        'advice': 'Check label instructions for proper shelf life once opened.',
        'freeze_ok': False
    }
}

def get_recipes_for_items(food_items):
    """
    Matches recipes based on food items that are expiring soon or active in inventory.
    Returns sorted list of matching recipes with highlighted matching items.
    """
    matched = []
    if not food_items:
        # Return standard popular waste-reduction recipes
        return RECIPE_DATABASE[:3]

    item_names = [f.name.lower() for f in food_items]
    categories = [f.category.lower() for f in food_items]

    for recipe in RECIPE_DATABASE:
        matching_reasons = []
        for kw in recipe['keywords']:
            for item in item_names:
                if kw in item:
                    matching_reasons.append(f"Matches your '{item.title()}'")
            for cat in categories:
                if kw in cat:
                    matching_reasons.append(f"Matches category '{cat.title()}'")

        if matching_reasons:
            rec_copy = dict(recipe)
            rec_copy['matching_reasons'] = list(set(matching_reasons))
            matched.append(rec_copy)

    # If no direct matches, return top recipes as recommendations
    if not matched:
        return RECIPE_DATABASE[:3]

    return matched

def get_storage_advice(category, food_name=""):
    """Returns storage instructions and waste reduction tips for a category/item."""
    default = {
        'best_place': 'Cool, dry location or refrigerator depending on label',
        'advice': 'Check package seal and keep away from heat sources.',
        'freeze_ok': False
    }
    return STORAGE_GUIDELINES.get(category, default)
