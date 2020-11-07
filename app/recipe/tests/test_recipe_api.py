from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def sample_tag(user, name='Tag'):
    '''
    Create and return a sample tag
    '''
    return Tag.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    '''
    Create and return a sample recipe
    '''
    defaults = {
        'title': 'Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    '''
    Test unauthenticated recipe API access
    '''
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''
        Test that authentication is required
        '''
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    '''
    Test authenticated recipe API access
    '''
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''
        Test retrieving a list of recipes
        '''
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''
        Test retrieving recipes for user
        '''
        self.user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'password'
        )
        sample_recipe(user=self.user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
