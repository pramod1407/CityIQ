from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import SignUpForm
from .models import ChatHistory, UserProfile
import json
from google import genai

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Welcome to CityIQ, {user.first_name}!')
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def get_chat_history(request):
    chats = ChatHistory.objects.filter(user=request.user)[:50]
    data = [{
        'query': chat.query,
        'response': chat.response,
        'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in chats]
    return JsonResponse({'chats': data})

@login_required
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_prompt = data.get('prompt', '')
            
            if not user_prompt:
                return JsonResponse({'error': 'No prompt provided'}, status=400)
            
            # System context for Kolhapur
            system_prompt = "You are an expert local guide for Kolhapur City, Maharashtra. You are helpful, polite, and enthusiastic. Keep answers concise (under 100 words unless asked for a plan). Format output with Markdown (bolding key terms). Focus on Kolhapur history, food (Misal, Tambda Pandhra Rassa), Mahalaxmi temple, and travel logic. If asked about prices, give estimates in INR."
            
            # Create Gemini client with SDK
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Generate response using SDK with correct model name
            response = client.models.generate_content(
                model='gemini-2.5-flash',  # Changed to gemini-2.5-flash
                contents=user_prompt,
                config={
                    'system_instruction': system_prompt,
                    'temperature': 0.7,
                }
            )
            
            ai_response = response.text
            
            # Save to database
            ChatHistory.objects.create(
                user=request.user,
                query=user_prompt,
                response=ai_response
            )
            
            return JsonResponse({'response': ai_response})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@login_required
def clear_chat(request):
    if request.method == 'POST':
        ChatHistory.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)