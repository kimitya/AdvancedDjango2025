from django.shortcuts import render, redirect
from .models import Food, Consume, HealthGoal
from django.http import JsonResponse
from .models import Food
from .forms import FoodForm, HealthGoalForm
from django.contrib.auth.decorators import login_required


def index(request):
    user = request.user
    foods = Food.objects.all()
    consumed_food = Consume.objects.filter(user=user)

    health_goal, created = HealthGoal.objects.get_or_create(user=user)
    if request.method =="POST":
        food_consumed = request.POST['food_consumed']
        c = Food.objects.get(name=food_consumed)
        user = request.user
        consume = Consume(user=user, food_consumed=c)
        consume.save()
        foods = Food.objects.all()
    else:
        foods = Food.objects.all()
    consumed_food = Consume.objects.filter(user=request.user)
    return render(request, 'app/index.html', {'foods': foods, 'consumed_food':consumed_food, 'health_goal': health_goal})

def delete_consume(request, id):
    consumed_food = Consume.objects.get(id=id)
    if request.method=="POST":
        consumed_food.delete()
        return redirect('/')
    return render(request, 'app/delete.html')

# def update_goal(request):
#     user = request.user
#     health_goal, created = HealthGoal.objects.get_or_create(user=user)
#
#     if request.method == "POST":
#         health_goal.daily_calorie_goal = request.POST.get('daily_calorie_goal', health_goal.daily_calorie_goal)
#         health_goal.carb_goal = request.POST.get('carb_goal', health_goal.carb_goal)
#         health_goal.protein_goal = request.POST.get('protein_goal', health_goal.protein_goal)
#         health_goal.fat_goal = request.POST.get('fat_goal', health_goal.fat_goal)
#         health_goal.save()
#         return redirect('index')
#
#     return render(request, 'app/update_goal.html', {'health_goal': health_goal})

def nutrient_data(request):
    consumed = Consume.objects.filter(user=request.user)
    data = {
        "carbs": sum(c.food_consumed.carbs for c in consumed),
        "proteins": sum(c.food_consumed.proteins for c in consumed),
        "fats": sum(c.food_consumed.fats for c in consumed)
    }
    return JsonResponse(data)

def chart_data(request):
    consumed = Consume.objects.filter(user=request.user)
    data = {
        "labels": [c.food_consumed.name for c in consumed],
        "carbs": [c.food_consumed.carbs for c in consumed],
        "proteins": [c.food_consumed.proteins for c in consumed],
        "fats": [c.food_consumed.fats for c in consumed],
        "calories": [c.food_consumed.calories for c in consumed],
    }
    return JsonResponse(data)

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {"form": form})


def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the food to the global registry
            return redirect("index")  # Redirects back to the homepage
    else:
        form = FoodForm()
    return render(request, "app/add_food.html", {"form": form})

@login_required
def update_goals(request):
    goal, created = HealthGoal.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = HealthGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = HealthGoalForm(instance=goal)
    return render(request, "app/update_goals.html", {"form": form})

@login_required
def chart_data(request):
    consumed = Consume.objects.filter(user=request.user)
    goal, _ = HealthGoal.objects.get_or_create(user=request.user)

    data = {
        "labels": [c.food_consumed.name for c in consumed],
        "carbs": [c.food_consumed.carbs for c in consumed],
        "proteins": [c.food_consumed.proteins for c in consumed],
        "fats": [c.food_consumed.fats for c in consumed],
        "calories": [c.food_consumed.calories for c in consumed],
        "goal_carbs": goal.carb_goal,
        "goal_proteins": goal.protein_goal,
        "goal_fats": goal.fat_goal,
        "goal_calories": goal.daily_calorie_goal,
    }
    return JsonResponse(data)





