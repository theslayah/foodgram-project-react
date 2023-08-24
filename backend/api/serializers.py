from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import Ingredient, Tag, Recipe, IngredientFromRecipe
from rest_framework import status
from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework.exceptions import ValidationError

from rest_framework.serializers import ModelSerializer

from users.models import User, Subscribe


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

        def get_is_subscribed(self, object):
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
            return Subscribe.objects.filter(user=user,
                                            author=object.id).exists()


class SubscribeSerializer(UserSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username')

        def validate(self, data):
            author = self.instance
            user = self.context.get('request').user
            if Subscribe.objects.filter(author=author, user=user).exists():
                raise ValidationError(
                    detail='Вы уже подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                raise ValidationError(
                    detail='Нельзя подписаться на самого себя!',
                    code=status.HTTP_400_BAD_REQUEST
                )
            return data

        def get_recipes_count(self, obj):
            return obj.recipes.count()

        def get_recipes(self, obj):
            request = self.context.get('request')
            limit = request.GET.get('recipes_limit')
            recipes = obj.recipes.all()
            if limit:
                recipes = recipes[:int(limit)]
            serializer = InfoRecipeSerializer(recipes,
                                              many=True, read_only=True)
            return serializer.data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientFromRecipeSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientFromRecipe
        fields = ('id', 'amount')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class InfoRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeGetSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientFromRecipe.objects.filter(recipe=obj)
        return IngredientFromRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeSerializer(ModelSerializer):
    ingredients = IngredientFromRecipeSerializer(many=True)
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate_ingredients(self, ingredients):
        """Проверка на уникальность и количество интгредиентов."""
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise ValidationError(
                    'Не может быть меньше 1'
                )
            if int(ingredient.get('amount')) > 100:
                raise ValidationError(
                    'Не может быть больше 100'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверка на уникальность тегов."""
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    @transaction.atomic
    def add_ingredients(self, ingredients, recipe):
        IngredientFromRecipe.objects.bulk_create(
            [IngredientFromRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data
