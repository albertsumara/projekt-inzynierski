import pytest

pytestmark = pytest.mark.integration


def test_list_recipes_reads_database_and_calculates_nutrition(
    api_client, seeded_recipe
):
    response = api_client.post("/api/v1/recipe", json={})

    assert response.status_code == 200
    recipe = response.json()["recipes"][0]
    assert recipe["recipe"]["name"] == seeded_recipe.name
    assert recipe["recipe"]["recipes_products"][0]["product_name"] == "Apple"
    assert recipe["recipe_nutrition"]["calories"] == 178
    assert recipe["recipe_nutrition"]["protein"] == 2.2
    assert recipe["recipe_nutrition"]["carbs"] == 45.6
    assert recipe["recipe_nutrition"]["fat"] == 0.6
