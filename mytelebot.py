from typing import final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import random
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TELE_TOKEN')
BOT_USERNAME: final = '@myBidisha_TeleRecipeBot'

# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Thanks for chatting with me! I am tomato! I can tell jokes and recipes, also you can search any image using me!\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am Tomato! I can tell jokes and recipes you want and can help you get any image you are looking for! Please type something so I respond!\n\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # API for joke
    url = "https://dad-jokes.p.rapidapi.com/random/joke"
    headers = {
        "X-RapidAPI-Key": os.getenv('JOKE_APIKEY'),
        "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    
    await update.message.reply_text(f"{json.loads(response.text)['body'][0]['setup']}\n{json.loads(response.text)['body'][0]['punchline']}")

async def fetch_random_image(query: str) -> str:
    # API for image
    url = f"https://google-api31.p.rapidapi.com/imagesearch"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.getenv('IMAGE_APIKEY'),
        "X-RapidAPI-Host": "google-api31.p.rapidapi.com"
    }
    payload = {
        "text": query,
        "safesearch": "off",
        "region": "wt-wt",
        "color": "",
        "size": "",
        "type_image": "",
        "layout": "",
        "max_results": 100
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and data['result']:
            images = [item['image'] for item in data['result']]
            return random.choice(images)
    return None

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide an image to search for.\nFollow the format: /image 'Name'")
        return
    
    query = ' '.join(context.args)
    image_url = await fetch_random_image(query)
    
    if image_url:
        await update.message.reply_photo(image_url)
    else:
        await update.message.reply_text("No images found for the provided query.")

async def recipe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a recipe to search for.\nFollow the format: /recipe 'Name'")
        return
    
    query = ' '.join(context.args)

    # API for recipe
    url = f'https://api.api-ninjas.com/v1/recipe?query={query}'
    headers = {'X-Api-Key': os.getenv('RECIPE_APIKEY')}
    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        recipes = json.loads(response.text)
        if not recipes:
            await update.message.reply_text("No recipes found for your query.")
            return
        for recipe in recipes:
            for key, value in recipe.items():
                await update.message.reply_text(f"{key}:\n{value}")        
        await update.message.reply_text("Image:")
        image_url = await fetch_random_image(query)
        if image_url:
            await update.message.reply_photo(image_url)
        else:
            await update.message.reply_text("No images found for the provided query.")
    else:
        await update.message.reply_text(f"Error: {response.status_code}\n{response.text}")

# RESPONSES
def handle_responses(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed or 'hi' in processed or 'hey' in processed:
        return "Hey there! How can I assist you?\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'how are you' in processed:
        return "I am good!\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'who are you' in processed or 'your name' in processed or 'what do you do' in processed:
        return "I am tomato!\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'good' in processed or 'well done' in processed or 'nice' in processed or 'great' in processed:
        return "Thank you very much! How can I help you more?\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'poor' in processed or 'bad' in processed:
        return "Sorry to hear that! Please let me know how may I help you.\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'lol' in processed or 'funny' in processed or 'haha' in processed:
        return "Haha! Hope you like the joke. Please let me know how may I help you more.\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    elif 'ok bye' in processed:
        return 'Good Bye! See ya!'
    elif 'thank' in processed or 'ok' in processed:
        return "I am glad to welcome you! Anything else you are looking for?\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"
    else:
        return "Sorry I dont understand what you say! Please follow the below commands to access me!\n\nEnter /help for help\nEnter /joke for a joke\nFollow the format: /recipe 'Name' for any recipe\nFollow the format: /image 'Name' for any image"

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('joke', joke_command))
    app.add_handler(CommandHandler('recipe', recipe_command))
    app.add_handler(CommandHandler('image', image_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_messages))

    # Errors
    app.add_error_handler(error)

    # Polling
    print('Polling...')
    app.run_polling(poll_interval=3)