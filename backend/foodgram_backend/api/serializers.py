from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers, status

from recipes.models import (MAX_NUMBER, MIN_NUMBER, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов при получении рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'name', 'image',
                  'text', 'cooking_time', 'is_in_shopping_cart'
                  )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorite_recipe.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shopping_cart_recipe.filter(recipe=obj).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        min_value=MIN_NUMBER, max_value=MAX_NUMBER
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_NUMBER, max_value=MAX_NUMBER
    )

    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'text',
                  'cooking_time', 'ingredients', 'image')

    def validate_cooking_time(self, cooking_time):
        print(cooking_time)
        if cooking_time <= MIN_NUMBER:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        if cooking_time > MAX_NUMBER:
            raise serializers.ValidationError(
                'Время приготовления не может быть больше 32000'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        print(ingredients)
        for ingredient in ingredients:
            if int(ingredient['amount']) <= MIN_NUMBER:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
            if int(ingredient['amount']) > MAX_NUMBER:
                raise serializers.ValidationError(
                    'Количество ингредиентов не может быть больше 32000'
                )
        return ingredients

    def create_ingredients(ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount'],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        if ingredients:
            ingredients.recipe_ingredient.filter(recipe=recipe).delete()
            self.create_ingredients(ingredients, recipe)
        if tags_data:
            recipe.tags.set(tags_data)

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.favorite_recipe.filter(recipe=recipe).exists():
            raise exceptions.ValidationError(
                detail='Рецепт уже есть в избранном!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.shopping_cart_recipe.filter(recipe=recipe).exists():
            raise exceptions.ValidationError(
                detail='Рецепт уже есть в списке покупок!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
