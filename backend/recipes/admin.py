from django.contrib.admin import ModelAdmin, register
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from recipes.models import (Ingredient, Tag, Recipe, IngredientFromRecipe,
                            Favourite, ShoppingCart)


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


@register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'id', 'author', 'favourites')
    readonly_fields = ('favourites',)
    list_filter = ('author', 'name', 'tags')

    def favourites(self, obj):
        return obj.favourites.count()


@register(IngredientFromRecipe)
class IngredientFromRecipeAdmin(ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@register(Favourite)
class FavouriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe')


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
